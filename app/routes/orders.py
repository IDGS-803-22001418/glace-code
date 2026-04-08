from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user  # type: ignore
from app.decorators import roles_required
from app import db
from app.models import Product, Venta, DetalleVenta, CustomOrder, Customer, Recipe, ProductionTask, RecipeDetail, Insumo
from datetime import datetime, timezone, timedelta

orders_bp = Blueprint('orders', __name__)


def _to_base_units(detail: RecipeDetail) -> tuple[float | None, str | None]:
    """Helper to convert recipe detail quantity to insumo base units."""
    insumo = detail.insumo
    if not insumo:
        return None, "Insumo no encontrado."
    
    if detail.unidad_medida_id == insumo.unidad_base_id:
        return detail.cantidad, None

    for conv in insumo.conversiones:
        if conv.is_active and conv.unidad_destino_id == detail.unidad_medida_id:
            if not conv.factor_conversion or conv.factor_conversion == 0:
                return None, f"Factor de conversión inválido para {insumo.nombre_insumo}."
            return detail.cantidad / conv.factor_conversion, None

    return None, f"No se encontró conversión para {insumo.nombre_insumo}."


@orders_bp.route('/')
@login_required
@roles_required('chef', 'seller')
def index():
    # Only show orders with at least one custom item
    custom_sales = (
        Venta.query
        .join(DetalleVenta)
        .join(CustomOrder)
        .filter(Venta.estado != 'Entregado')
        .order_by(Venta.fecha_hora.asc())
        .distinct()
        .all()
    )
    return render_template('internal/orders/index.html', sales=custom_sales)


@orders_bp.route('/start-production/<int:venta_id>', methods=['POST'])
@login_required
@roles_required('chef')
def start_production(venta_id: int):
    venta = db.session.get(Venta, venta_id)
    if not venta:
        flash('Venta no encontrada.', 'danger')
        return redirect(url_for('orders.index'))

    # 1. Encontrar la receta
    # 2. Validar insumos
    # 3. Restar insumos
    
    try:
        items_to_produce = []
        for detalle in venta.detalles:
            if not detalle.custom_order:
                continue
            
            # Buscar receta que genere 1 unidad
            recipe = Recipe.query.filter_by(product_id=detalle.producto_id, cantidad_producida=1.0, is_active=True).first()
            if not recipe:
                flash(f'No se encontró una receta que genere exactamente 1 unidad para "{detalle.producto.nombre_producto}". Por favor, agrega esta receta antes de continuar.', 'warning')
                return redirect(url_for('orders.index'))
            
            items_to_produce.append((detalle, recipe))

        # Validar insumos para TODOS los items primero
        deductions = []
        for detalle, recipe in items_to_produce:
            # Multiplicamos los requerimientos de la receta por la cantidad del pedido
            for rec_detail in recipe.details:
                if not rec_detail.is_active:
                    continue
                
                cant_base, err = _to_base_units(rec_detail)
                if err:
                    flash(err, 'danger')
                    return redirect(url_for('orders.index'))
                
                total_needed = cant_base * detalle.cantidad
                if rec_detail.insumo.stock_actual < total_needed:
                    flash(f'Insumo insuficiente: {rec_detail.insumo.nombre_insumo}. Necesario: {total_needed}, Disponible: {rec_detail.insumo.stock_actual}', 'danger')
                    return redirect(url_for('orders.index'))
                
                deductions.append((rec_detail.insumo, total_needed))

        # Realizar deducciones y crear tareas
        for insumo_obj, qty in deductions:
            insumo_obj.stock_actual -= qty
        
        venta.estado = 'En Producción'
        db.session.commit()
        flash('Pedido en producción', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar: {str(e)}', 'danger')
        
    return redirect(url_for('orders.index'))


@orders_bp.route('/mark-as-ready/<int:venta_id>', methods=['POST'])
@login_required
@roles_required('chef')
def mark_as_ready(venta_id: int):
    venta = db.session.get(Venta, venta_id)
    if venta:
        venta.estado = 'Listo'
        db.session.commit()
        flash('Pedido marcado como listo para entrega.', 'success')
    return redirect(url_for('orders.index'))


@orders_bp.route('/mark-as-delivered/<int:venta_id>', methods=['POST'])
@login_required
@roles_required('seller')
def mark_as_delivered(venta_id: int):
    venta = db.session.get(Venta, venta_id)
    if venta:
        venta.estado = 'Entregado'
        db.session.commit()
        flash('Venta finalizada: Pedido entregado al cliente.', 'success')
    return redirect(url_for('orders.index'))


def _get_cart():
    """Return the current cart list from the session."""
    return session.get('cart', [])


def _save_cart(cart):
    session['cart'] = cart
    session.modified = True


@orders_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
@roles_required('customer')
def add_to_cart(product_id: int):
    """
    Add a product to the session cart and redirect to the cart page.
    Accepts JSON or form data via AJAX / regular form.
    """
    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        return jsonify({'ok': False, 'message': 'Producto no encontrado.'}), 404

    cart = _get_cart()

    # Check if product already exists in cart → increment quantity
    for item in cart:
        if item['product_id'] == product_id:
            item['cantidad'] += 1
            _save_cart(cart)
            return jsonify({
                'ok': True,
                'cart_count': sum(i['cantidad'] for i in cart),
                'redirect': url_for('orders.cart'),
            })

    # New item
    cart.append({
        'product_id': product.id,
        'nombre': product.nombre_producto,
        'precio': product.precio_venta,
        'imagen_url': product.imagen_url or '',
        'categoria': product.categoria or '',
        'cantidad': 1,
    })
    _save_cart(cart)

    return jsonify({
        'ok': True,
        'cart_count': sum(i['cantidad'] for i in cart),
        'redirect': url_for('orders.cart'),
    })


@orders_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required
@roles_required('customer')
def remove_from_cart(product_id: int):
    cart = _get_cart()
    cart = [item for item in cart if item['product_id'] != product_id]
    _save_cart(cart)
    return redirect(url_for('orders.cart'))


@orders_bp.route('/cart/update/<int:product_id>', methods=['POST'])
@login_required
@roles_required('customer')
def update_cart_item(product_id: int):
    """Update quantity for a product in the cart."""
    try:
        cantidad = int(request.form.get('cantidad', 1))
    except (ValueError, TypeError):
        cantidad = 1

    cart = _get_cart()
    for item in cart:
        if item['product_id'] == product_id:
            if cantidad < 1:
                cart.remove(item)
            else:
                item['cantidad'] = cantidad
            break
    _save_cart(cart)
    return redirect(url_for('orders.cart'))


@orders_bp.route('/cart/clear', methods=['POST'])
@login_required
@roles_required('customer')
def clear_cart():
    _save_cart([])
    return redirect(url_for('orders.cart'))


@orders_bp.route('/cart')
@login_required
@roles_required('customer')
def cart():
    cart_items = _get_cart()
    subtotal = sum(item['precio'] * item['cantidad'] for item in cart_items)
    return render_template(
        'cart.html',
        cart_items=cart_items,
        subtotal=subtotal,
    )


@orders_bp.route('/checkout', methods=['POST'])
@login_required
@roles_required('customer')
def checkout():
    """
    Process custom order checkout via JSON payload.
    Expected keys: fecha_entrega, hora_entrega, lugar_entrega, items (list of custom data).
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'message': 'No se recibieron datos.'}), 400

        cart_items = _get_cart()
        if not cart_items:
            return jsonify({'ok': False, 'message': 'El carrito está vacío.'}), 400

        # Create base Venta
        # We assume the payment is already 'simulated' success
        
        # Check if customer profile exists
        customer = Customer.query.filter_by(user_id=current_user.id).first()
        if not customer:
            return jsonify({'ok': False, 'message': 'Perfil de cliente no encontrado.'}), 404

        # Combine items from session cart with customization data from payload
        # Payloads items can have different IDs or same IDs multiple times (usually unique in our cart)
        custom_data_map = {int(p['product_id']): p for p in data.get('items', [])}

        fecha_entrega_str = f"{data.get('fecha_entrega')} {data.get('hora_entrega')}"
        try:
            fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d %H:%M')
        except ValueError:
            return jsonify({'ok': False, 'message': 'Formato de fecha/hora inválido.'}), 400

        # Validación de 2 días de anticipación
        # Se toma como tiempo de referencia el momento actual
        ahora = datetime.now()
        minima_fecha = ahora + timedelta(days=2)
        if fecha_entrega < minima_fecha:
            return jsonify({
                'ok': False, 
                'message': 'Lo sentimos, los pedidos personalizados deben realizarse con al menos 2 días (48 horas) de anticipación.'
            }), 400

        nueva_venta = Venta(
            cliente_id=customer.id,
            metodo_pago='tarjeta', # In this flow it's simulated payment
            lugar_entrega=data.get('lugar_entrega', 'tienda').capitalize(),
            fecha_hora_entrega=fecha_entrega,
            estado='Pendiente',
            monto_recibido=sum(item['precio'] * item['cantidad'] * 1.16 for item in cart_items),
            monto_cambio=0
        )
        db.session.add(nueva_venta)
        db.session.flush() # To get nuova_venta.id

        for item in cart_items:
            product_id = item['product_id']
            # Create detail
            detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=product_id,
                cantidad=item['cantidad'],
                precio_unitario_aplicado=item['precio']
            )
            db.session.add(detalle)
            db.session.flush()

            # Create CustomOrder if customization exists
            if product_id in custom_data_map:
                c_info = custom_data_map[product_id]
                custom_order = CustomOrder(
                    tipo_evento=c_info.get('tipo_evento', 'Otro'),
                    instrucciones_decoracion=c_info.get('instrucciones', '')
                )
                custom_order.detalle_venta_id = detalle.id
                db.session.add(custom_order)

            # CRITICAL: We DON'T deduct Product.stock here for custom orders
            # as per user requirement.

        # Update customer points
        subtotal = sum(item['precio'] * item['cantidad'] for item in cart_items)
        puntos_ganados = int(subtotal / 10)
        customer.puntos_acumulados += puntos_ganados

        db.session.commit()
        
        # Clear cart
        _save_cart([])
        
        return jsonify({
            'ok': True, 
            'message': 'Tu pedido ha sido registrado con éxito y está pendiente de aprobación por administración.',
            'id': nueva_venta.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'message': f'Error al procesar el pedido: {str(e)}'}), 500

