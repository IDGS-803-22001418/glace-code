from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Product, Insumo, Customer, DetalleVenta, Venta, Merma, User
from flask_login import login_required # type: ignore
from app.decorators import roles_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
@roles_required('admin')
def index():
    return render_template('internal/reports/index.html')

@reports_bp.route('/api/reporte-ventas')
@login_required
@roles_required('admin')
def api_reporte_ventas():
    try:
        tipo = request.args.get('tipo', 'semana')
        
        if tipo == 'semana':
            semana = request.args.get('semana')
            año = int(semana.split('-')[0])
            semana_num = int(semana.split('-W')[1])
            
            from datetime import datetime, timedelta
            # Calcular fecha de inicio de la semana
            inicio_semana = datetime.strptime(f'{año}-W{semana_num}-1', "%Y-W%W-%w")
            fin_semana = inicio_semana + timedelta(days=6)
            
            # Consulta corregida
            resultados = db.session.query(
                DetalleVenta.id,
                DetalleVenta.cantidad,
                DetalleVenta.precio_unitario_aplicado,
                Venta.fecha_hora,
                Product,
                User.nombre_completo
            ).join(Venta, Venta.id == DetalleVenta.venta_id
            ).join(Product, Product.id == DetalleVenta.producto_id
            ).outerjoin(Customer, Customer.id == Venta.cliente_id
            ).outerjoin(User, User.id == Customer.user_id
            ).filter(
                Venta.fecha_hora >= inicio_semana,
                Venta.fecha_hora <= fin_semana,
                Venta.estado != 'Cancelado'
            ).all()
            
            datos = []
            total_monto = 0
            total_cantidad = 0
            total_utilidad = 0
            
            for r in resultados:
                nombre_cliente = r.nombre_completo if r.nombre_completo else 'Mostrador'
                monto = r.cantidad * r.precio_unitario_aplicado
                
                # Calcular utilidad
                costo_produccion = r.Product.costo_produccion_estimado
                utilidad = monto - (costo_produccion * r.cantidad)
                
                total_monto += monto
                total_cantidad += r.cantidad
                total_utilidad += utilidad
                
                datos.append({
                    'fecha': r.fecha_hora.strftime('%d/%m/%Y'),
                    'producto': r.Product.nombre_producto,
                    'cliente': nombre_cliente,
                    'cantidad': r.cantidad,
                    'monto': monto,
                    'utilidad': utilidad
                })
        else:  # mes
            mes = request.args.get('mes')
            año, mes_num = map(int, mes.split('-'))
            
            # Consulta corregida para mes
            resultados = db.session.query(
                DetalleVenta.id,
                DetalleVenta.cantidad,
                DetalleVenta.precio_unitario_aplicado,
                Venta.fecha_hora,
                Product,
                User.nombre_completo
            ).join(Venta, Venta.id == DetalleVenta.venta_id
            ).join(Product, Product.id == DetalleVenta.producto_id
            ).outerjoin(Customer, Customer.id == Venta.cliente_id
            ).outerjoin(User, User.id == Customer.user_id
            ).filter(
                db.extract('year', Venta.fecha_hora) == año,
                db.extract('month', Venta.fecha_hora) == mes_num,
                Venta.estado != 'Cancelado'
            ).all()
            
            datos = []
            total_monto = 0
            total_cantidad = 0
            total_utilidad = 0
            
            for r in resultados:
                nombre_cliente = r.nombre_completo if r.nombre_completo else 'Mostrador'
                monto = r.cantidad * r.precio_unitario_aplicado
                
                # Calcular utilidad
                costo_produccion = r.Product.costo_produccion_estimado
                utilidad = monto - (costo_produccion * r.cantidad)
                
                total_monto += monto
                total_cantidad += r.cantidad
                total_utilidad += utilidad
                
                datos.append({
                    'fecha': r.fecha_hora.strftime('%d/%m/%Y'),
                    'producto': r.Product.nombre_producto,
                    'cliente': nombre_cliente,
                    'cantidad': r.cantidad,
                    'monto': monto,
                    'utilidad': utilidad
                })
        
        return jsonify({
            'success': True,
            'datos': datos,
            'total_monto': total_monto,
            'total_cantidad': total_cantidad,
            'total_utilidad': total_utilidad
        })
        
    except Exception as e:
        print(f"Error en reporte-ventas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@reports_bp.route('/api/reporte-mermas-periodo')
@login_required
@roles_required('admin')
def api_reporte_mermas_periodo():
    try:
        tipo = request.args.get('tipo', 'semana')
        print(tipo)
        
        if tipo == 'semana':
            semana = request.args.get('semana')
            # Formato: "2026-W14"
            año = int(semana.split('-')[0])
            semana_num = int(semana.split('-W')[1]) - 1
            print(año, semana_num)
            
            # Calcular fecha de inicio y fin de la semana
            from datetime import datetime, timedelta
            inicio_semana = datetime.strptime(f'{año}-W{semana_num}-1', "%Y-W%W-%w")
            fin_semana = inicio_semana + timedelta(days=6)
            print(inicio_semana, fin_semana)
            
            mermas = Merma.query.filter(
                Merma.fecha_registro >= inicio_semana,
                Merma.fecha_registro <= fin_semana,
                Merma.is_active == True
            ).all()
            
        else:  # mes
            mes = request.args.get('mes')
            año, mes_num = map(int, mes.split('-'))
            
            mermas = Merma.query.filter(
                db.extract('year', Merma.fecha_registro) == año,
                db.extract('month', Merma.fecha_registro) == mes_num,
                Merma.is_active == True
            ).all()
        
        datos = []
        total_perdidas = 0
        
        for m in mermas:
            nombre = ''
            unidad = ''
            perdida = 0
            
            if m.insumo_id:
                insumo = Insumo.query.get(m.insumo_id)
                if insumo:
                    nombre = insumo.nombre_insumo
                    if insumo.unidad_base:
                        unidad = insumo.unidad_base.abreviatura or 'uds'
                    perdida = m.cantidad_perdida * insumo.precio_estimado  # Costo estimado
            elif m.producto_id:
                producto = Product.query.get(m.producto_id)
                if producto:
                    nombre = producto.nombre_producto
                    unidad = 'uds'
                    perdida = m.cantidad_perdida * producto.precio_venta
            else:
                nombre = 'Desconocido'
                unidad = 'uds'
                perdida = m.cantidad_perdida * 10
            
            total_perdidas += perdida
            
            datos.append({
                'fecha': m.fecha_registro.strftime('%d/%m/%Y %H:%M') if m.fecha_registro else '',
                'nombre': nombre,
                'cantidad': m.cantidad_perdida,
                'unidad': unidad,
                'causa': m.causa or 'No especificada',
                'perdida': perdida
            })
        
        return jsonify({'success': True, 'datos': datos, 'total_perdidas': total_perdidas})
        
    except Exception as e:
        print(f"Error en reporte-mermas-periodo: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
