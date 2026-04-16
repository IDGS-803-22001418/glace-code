from flask import Blueprint, render_template
from flask_login import login_required # type: ignore
from app.decorators import roles_required
from app import db
from app.models import Product
import random
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    active_products = db.session.query(Product).filter_by(is_active=True).all()
    random_products = random.sample(active_products, min(4, len(active_products)))
    return render_template('index.html', random_products=random_products)

@main_bp.route('/our-products')
def our_products():
    products = db.session.query(Product).filter_by(is_active=True).all()
    return render_template('our-products.html', products=products)

@main_bp.route('/internal')
@login_required
@roles_required('admin', 'chef')
def internal():
    from datetime import datetime
    from sqlalchemy import func
    from app.models import ProductionTask, Venta, DetalleVenta, CustomOrder, Insumo, db

    today = datetime.now().date()

    # 1. Producción (Lotes activos)
    produccion_count = db.session.query(ProductionTask).filter(ProductionTask.estado != 'Listo' and ProductionTask.is_active).count()

    # 2. Pedidos (Ventas con CustomOrder no listas/entregadas/canceladas)
    pedidos_count = db.session.query(Venta).join(DetalleVenta).join(CustomOrder).filter(
        ~Venta.estado.in_(['Listo', 'Entregado', 'Cancelado'])
    ).distinct().count()

    # 3. Ventas del día
    ventas_hoy = db.session.query(Venta).filter(func.date(Venta.fecha_hora) == today, Venta.estado != 'Cancelado').all()
    
    ventas_total_hoy = 0.0
    for v in ventas_hoy:
        ventas_total_hoy += sum(d.cantidad * d.precio_unitario_aplicado for d in v.detalles)
    
    # 4. Utilidad aproximada hoy
    costo_total_hoy = 0.0
    for v in ventas_hoy:
        for d in v.detalles:
            if d.producto:
                costo_produccion = d.producto.costo_produccion_estimado
                costo_total_hoy += costo_produccion * d.cantidad
                
    utilidad_hoy = ventas_total_hoy - costo_total_hoy
    
    # 5. Cálculo de promedios históricos para porcentajes
    ventas_historicas = db.session.query(Venta).filter(func.date(Venta.fecha_hora) < today, Venta.estado != 'Cancelado').all()
    ventas_por_dia = {}
    utilidad_por_dia = {}
    
    for v in ventas_historicas:
        dia = v.fecha_hora.date()
        venta_total = sum(d.cantidad * d.precio_unitario_aplicado for d in v.detalles)
        costo_total = sum((d.producto.costo_produccion_estimado if d.producto else 0.0) * d.cantidad for d in v.detalles)
        
        ventas_por_dia[dia] = ventas_por_dia.get(dia, 0.0) + venta_total
        utilidad_por_dia[dia] = utilidad_por_dia.get(dia, 0.0) + (venta_total - costo_total)
        
    num_dias = len(ventas_por_dia)
    promedio_historico_ventas = sum(ventas_por_dia.values()) / num_dias if num_dias > 0 else 0.0
    promedio_historico_utilidad = sum(utilidad_por_dia.values()) / num_dias if num_dias > 0 else 0.0
    
    # Calcular porcentajes
    if promedio_historico_ventas > 0:
        ventas_porcentaje = ((ventas_total_hoy - promedio_historico_ventas) / promedio_historico_ventas) * 100
    else:
        ventas_porcentaje = 100.0 if ventas_total_hoy > 0 else 0.0
        
    if promedio_historico_utilidad > 0:
        utilidad_porcentaje = ((utilidad_hoy - promedio_historico_utilidad) / promedio_historico_utilidad) * 100
    else:
        utilidad_porcentaje = 100.0 if utilidad_hoy > 0 else 0.0
        
    ventas_porcentaje = round(ventas_porcentaje, 1)
    utilidad_porcentaje = round(utilidad_porcentaje, 1)

    # 5. Actividad Reciente (Ventas de hoy)
    actividad_reciente = db.session.query(Venta).filter(
        func.date(Venta.fecha_hora) == today,
        Venta.estado != 'Cancelado'
    ).order_by(Venta.fecha_hora.desc()).limit(10).all()

    # 6. Alertas de inventario
    alertas_inventario = db.session.query(Insumo).filter(
        Insumo.stock_actual <= Insumo.stock_minimo_alerta,
        Insumo.is_active == True
    ).all()
    alertas_count = len(alertas_inventario)

    # Best selling products
    last_week_start = today - timedelta(days=7)
    last_month_start = today - timedelta(days=30)

    best_week = db.session.query(
        Product.nombre_producto,
        func.sum(DetalleVenta.cantidad).label('total')
    ).join(DetalleVenta, Product.id == DetalleVenta.producto_id
    ).join(Venta, DetalleVenta.venta_id == Venta.id
    ).filter(Venta.fecha_hora >= last_week_start, Venta.estado != 'Cancelado'
    ).group_by(Product.id
    ).order_by(func.sum(DetalleVenta.cantidad).desc()
    ).first()

    best_month = db.session.query(
        Product.nombre_producto,
        func.sum(DetalleVenta.cantidad).label('total')
    ).join(DetalleVenta, Product.id == DetalleVenta.producto_id
    ).join(Venta, DetalleVenta.venta_id == Venta.id
    ).filter(Venta.fecha_hora >= last_month_start, Venta.estado != 'Cancelado'
    ).group_by(Product.id
    ).order_by(func.sum(DetalleVenta.cantidad).desc()
    ).first()

    best_week_name = best_week.nombre_producto if best_week else None
    best_week_total = best_week.total if best_week else 0
    best_month_name = best_month.nombre_producto if best_month else None
    best_month_total = best_month.total if best_month else 0

    return render_template('internal/index.html',
                           produccion_count=produccion_count,
                           pedidos_count=pedidos_count,
                           ventas_total_hoy=ventas_total_hoy,
                           ventas_porcentaje=ventas_porcentaje,
                           utilidad_hoy=utilidad_hoy,
                           utilidad_porcentaje=utilidad_porcentaje,
                           actividad_reciente=actividad_reciente,
                           alertas_inventario=alertas_inventario,
                           alertas_count=alertas_count,
                           best_week_name=best_week_name,
                           best_week_total=best_week_total,
                           best_month_name=best_month_name,
                           best_month_total=best_month_total)