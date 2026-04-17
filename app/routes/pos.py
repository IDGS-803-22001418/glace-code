import json
from flask import Blueprint, render_template, flash, request, redirect, url_for
from app import db, user_logger
from app.models import Product, Customer, User, Venta, DetalleVenta
from flask_login import login_required, current_user # type: ignore
from app.decorators import roles_required
from datetime import datetime

pos_bp = Blueprint('pos', __name__)

@pos_bp.route('/')
@login_required
@roles_required('seller')
def index():
    productos = Product.query.filter(Product.stock > 0).order_by(Product.categoria, Product.nombre_producto).all()
    clientes = Customer.query.join(User).order_by(User.nombre_completo).all()
    
    categorias = {}
    for producto in productos:
        if producto.categoria not in categorias:
            categorias[producto.categoria] = []
        categorias[producto.categoria].append(producto)
    
    return render_template('internal/pos/index.html', 
                         productos=productos,
                         clientes=clientes,
                         categorias=categorias)

@pos_bp.route('/confirm-sale')
@login_required
@roles_required('seller')
def confirm_sale():
    return render_template('internal/pos/confirm_sale.html')

@pos_bp.route('/registrar-venta', methods=['POST'])
@login_required
@roles_required('seller')
def register_sale():
    try:
        productos_json = request.form.get('productos_json')
        total = float(request.form.get('total', 0))
        metodo_pago = request.form.get('metodo_pago')
        monto_recibido = float(request.form.get('monto_recibido', 0))
        monto_cambio = float(request.form.get('monto_cambio', 0))
        cliente_id = request.form.get('cliente_id')
        
        productos = json.loads(productos_json)
        
        if not productos:
            flash('No hay productos en la venta', 'danger')
            return redirect(url_for('pos.index'))
        
        # Crear venta
        nueva_venta = Venta(
            cliente_id=int(cliente_id) if cliente_id and cliente_id != '' else None,
            metodo_pago=metodo_pago,
            monto_recibido=monto_recibido,
            monto_cambio=monto_cambio,
            lugar_entrega='Tienda',
            fecha_hora_entrega=datetime.now(),
            estado='Entregado'
        )
        db.session.add(nueva_venta)
        db.session.flush()
        
        # Detalles y actualizar stock
        for item in productos:
            detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=item['id'],
                cantidad=item['cantidad'],
                precio_unitario_aplicado=item['precio']
            )
            db.session.add(detalle)
            
            producto = Product.query.get(item['id'])
            if producto:
                producto.stock -= item['cantidad']
        
        # Actualizar puntos del cliente
        if cliente_id and cliente_id != '':
            cliente = Customer.query.get(int(cliente_id))
            if cliente:
                puntos_ganados = int(total / 10)
                cliente.puntos_acumulados += puntos_ganados
        
        db.session.commit()
        
        user_logger.log_action(
            current_user,
            module="Punto de Venta",
            action=f"Se registró la venta {nueva_venta.id} por ${total}",
            success=True,
        )
        
        # Limpiar sessionStorage (desde el cliente, pero ya se redirige)
        flash('Venta registrada exitosamente', 'success')
        return redirect(url_for('pos.index'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        flash(f'Error al registrar la venta: {str(e)}', 'danger')
        return redirect(url_for('pos.index'))
