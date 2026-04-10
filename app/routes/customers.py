from __future__ import annotations
import math
import re
from typing import TypedDict
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user # type: ignore
from sqlalchemy import func, or_
from app import db, user_logger
from app.decorators import roles_required
from app.models import Customer, User, UserRole, Venta


class CustomerRow(TypedDict):
    id: int
    nombre_completo: str
    correo_electronico: str
    telefono: str
    puntos_acumulados: int
    nivel: str
    initials: str
    ultima_compra: str | None


def _is_valid_email(email: str) -> bool:
    email = (email or '').strip()
    if not email or len(email) > 150:
        return False
    return re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email) is not None


def _is_valid_phone(phone: str) -> bool:
    phone = (phone or '').strip()
    if not phone or len(phone) > 20:
        return False
    return re.match(r"^\+?[0-9]{7,20}$", phone) is not None

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/')
@login_required
@roles_required('admin', 'seller')
def index():
    raw_query = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int) or 1
    per_page = request.args.get('per_page', 10, type=int) or 10

    if page < 1:
        page = 1
    if per_page < 5:
        per_page = 5
    if per_page > 50:
        per_page = 50

    # Subconsulta para obtener la fecha de la última compra de cada cliente
    last_purchase_sub = (
        db.session.query(
            Venta.cliente_id,
            func.max(Venta.fecha_hora).label('last_date')
        )
        .group_by(Venta.cliente_id)
        .subquery()
    )

    base_query = (
        db.session.query(Customer, last_purchase_sub.c.last_date)
        .join(User, Customer.user_id == User.id)
        .outerjoin(last_purchase_sub, Customer.id == last_purchase_sub.c.cliente_id)
        .filter(Customer.is_active == True, User.is_active == True)
        .options(db.joinedload(Customer.user))
    )

    if raw_query:
        like = f"%{raw_query.lower()}%"
        base_query = base_query.filter(
            or_(
                func.lower(User.nombre_completo).like(like),
                func.lower(User.correo_electronico).like(like),
                func.lower(Customer.telefono).like(like),
            )
        )

    total = base_query.count()
    total_pages = max(1, math.ceil(total / per_page))
    if page > total_pages:
        page = total_pages

    customers = (
        base_query.order_by(User.nombre_completo)
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    def initials(full_name: str) -> str:
        parts = [p for p in (full_name or '').strip().split() if p]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][:1] + parts[-1][:1]).upper()

    rows: list[CustomerRow] = []
    for customer, last_date in customers:
        user = customer.user
        nivel = customer.nivel_cliente()
        rows.append(
            {
                'id': customer.id,
                'nombre_completo': getattr(user, 'nombre_completo', '') if user else '',
                'correo_electronico': getattr(user, 'correo_electronico', '') if user else '',
                'telefono': customer.telefono or '',
                'puntos_acumulados': customer.puntos_acumulados or 0,
                'nivel': nivel,
                'initials': initials(getattr(user, 'nombre_completo', '') if user else ''),
                'ultima_compra': last_date.strftime('%d/%m/%Y') if last_date else None,
            }
        )

    start_item = 0 if total == 0 else ((page - 1) * per_page + 1)
    end_item = min(total, page * per_page)

    return render_template(
        'internal/customers/index.html',
        customers=rows,
        q=raw_query,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        start_item=start_item,
        end_item=end_item,
    )
    
@customers_bp.route('/my-profile', methods=['GET'])
@login_required
@roles_required('customer')
def my_profile():
    user = db.session.query(User).filter_by(id=current_user.id).first()
    if not user:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('customers.my_profile'))
    customer = db.session.query(Customer).filter_by(user_id=user.id).first()
    if not customer:
        flash('Perfil de cliente no encontrado.', 'error')
        return redirect(url_for('customers.my_profile'))

    # Fetch only last 3 orders
    purchases = db.session.query(Venta).filter_by(cliente_id=customer.id).order_by(Venta.fecha_hora.desc()).limit(3).all()

    return render_template('internal/customers/my-profile.html', customer=customer, user=user, purchases=purchases)


@customers_bp.route('/my-orders', methods=['GET'])
@login_required
@roles_required('customer')
def my_orders():
    customer = db.session.query(Customer).filter_by(user_id=current_user.id).first()
    if not customer:
        return "Perfil de cliente no encontrado", 404

    purchases = db.session.query(Venta).filter_by(cliente_id=customer.id).order_by(Venta.fecha_hora.desc()).all()
    return render_template('internal/customers/my-orders.html', purchases=purchases)


@customers_bp.route('/my-orders/<int:venta_id>', methods=['GET'])
@login_required
@roles_required('customer')
def order_detail(venta_id: int):
    venta = db.session.get(Venta, venta_id)
    if not venta:
        flash('Pedido no encontrado.', 'error')
        return redirect(url_for('customers.my_orders'))

    # Security check: Ensure this order belongs to the logged-in customer
    customer = db.session.query(Customer).filter_by(user_id=current_user.id).first()
    if not customer or venta.cliente_id != customer.id:
        flash('No tienes permiso para ver este pedido.', 'error')
        return redirect(url_for('customers.my_orders'))

    return render_template('internal/customers/order-detail.html', venta=venta)


@customers_bp.route('/my-profile/update', methods=['POST'])
@login_required
@roles_required('customer')
def update_my_profile():
    user = db.session.query(User).filter_by(id=current_user.id).first()
    if not user:
        return "Usuario no encontrado", 404

    customer = db.session.query(Customer).filter_by(user_id=user.id).first()
    if not customer:
        return "Perfil de cliente no encontrado", 404

    nombre_completo = (request.form.get('nombre_completo') or '').strip()
    correo_electronico = User.normalize_email(request.form.get('correo_electronico') or '')
    telefono = (request.form.get('telefono') or '').strip()
    direccion_despacho = (request.form.get('direccion_despacho') or '').strip()

    if not nombre_completo:
        flash('El nombre completo es obligatorio.', 'error')
        return redirect(url_for('customers.my_profile'))

    if len(nombre_completo) > 150:
        flash('El nombre completo no puede exceder 150 caracteres.', 'error')
        return redirect(url_for('customers.my_profile'))

    if not _is_valid_email(correo_electronico):
        flash('Ingresa un correo electrónico válido.', 'error')
        return redirect(url_for('customers.my_profile'))

    if not _is_valid_phone(telefono):
        flash('Ingresa un teléfono válido (solo números).', 'error')
        return redirect(url_for('customers.my_profile'))

    if not direccion_despacho:
        flash('La dirección de despacho es obligatoria.', 'error')
        return redirect(url_for('customers.my_profile'))

    if len(direccion_despacho) > 200:
        flash('La dirección de despacho no puede exceder 200 caracteres.', 'error')
        return redirect(url_for('customers.my_profile'))

    email_owner = db.session.query(User).filter_by(correo_electronico=correo_electronico).first()
    if email_owner and email_owner.id != user.id:
        flash('Ya existe una cuenta con ese correo electrónico.', 'error')
        return redirect(url_for('customers.my_profile'))

    try:
        user.nombre_completo = nombre_completo
        user.correo_electronico = correo_electronico
        customer.telefono = telefono
        customer.direccion_despacho = direccion_despacho
        db.session.commit()
        user_logger.log_action(
            current_user,
            module="Clientes",
            action="Cliente actualizó su perfil",
            success=True,
        )
        flash('Tus datos personales se actualizaron correctamente.', 'success')
    except Exception:
        db.session.rollback()
        flash('No se pudieron actualizar tus datos. Intenta nuevamente.', 'error')

    return redirect(url_for('customers.my_profile'))


@customers_bp.route('/my-profile/password', methods=['POST'])
@login_required
@roles_required('customer')
def update_my_password():
    user = db.session.query(User).filter_by(id=current_user.id).first()
    if not user:
        return "Usuario no encontrado", 404

    current_password = request.form.get('current_password') or ''
    new_password = request.form.get('new_password') or ''
    confirm_password = request.form.get('confirm_password') or ''

    if not user.check_password(current_password):
        flash('La contraseña actual no es correcta.', 'error')
        return redirect(url_for('customers.my_profile'))

    if len(new_password) < 8:
        flash('La nueva contraseña debe tener al menos 8 caracteres.', 'error')
        return redirect(url_for('customers.my_profile'))

    if new_password != confirm_password:
        flash('La confirmación de contraseña no coincide.', 'error')
        return redirect(url_for('customers.my_profile'))

    try:
        user.set_password(new_password)
        db.session.commit()
        user_logger.log_action(
            current_user,
            module="Clientes",
            action="Cliente actualizó su contraseña",
            success=True,
        )
        flash('Tu contraseña fue actualizada correctamente.', 'success')
    except Exception:
        db.session.rollback()
        flash('No se pudo actualizar tu contraseña. Intenta nuevamente.', 'error')

    return redirect(url_for('customers.my_profile'))
    
@customers_bp.route('/view/<int:customer_id>')
@login_required
@roles_required('admin', 'seller')
def view(customer_id: int):
    customer = db.session.query(Customer).filter_by(id=customer_id, is_active=True).first()
    if not customer:
        flash('Cliente no encontrado.', 'error')
        return redirect(url_for('customers.index'))

    # Metrics calculation
    ventas = db.session.query(Venta).filter_by(cliente_id=customer.id).all()
    total_spent = sum(v.monto_recibido for v in ventas)
    order_count = len(ventas)
    avg_ticket = total_spent / order_count if order_count > 0 else 0
    
    # Recent history
    history = db.session.query(Venta).filter_by(cliente_id=customer.id).order_by(Venta.fecha_hora.desc()).limit(10).all()

    return render_template(
        'internal/customers/view.html',
        customer=customer,
        total_spent=total_spent,
        order_count=order_count,
        avg_ticket=avg_ticket,
        history=history
    )

@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'seller')
def create():
    if request.method == 'POST':
        nombre_completo = (request.form.get('nombre_completo') or '').strip()
        correo_electronico = User.normalize_email(request.form.get('correo_electronico') or '')
        telefono = (request.form.get('telefono') or '').strip()
        direccion_despacho = (request.form.get('direccion_despacho') or '').strip()

        if not nombre_completo:
            flash('El nombre completo es obligatorio.', 'error')
            return redirect(url_for('customers.create'))

        if len(nombre_completo) > 150:
            flash('El nombre completo no puede exceder 150 caracteres.', 'error')
            return redirect(url_for('customers.create'))

        if not _is_valid_email(correo_electronico):
            flash('Ingresa un correo electrónico válido.', 'error')
            return redirect(url_for('customers.create'))

        if not telefono:
            flash('El teléfono es obligatorio.', 'error')
            return redirect(url_for('customers.create'))

        if not _is_valid_phone(telefono):
            flash('Ingresa un teléfono válido (solo números).', 'error')
            return redirect(url_for('customers.create'))

        if direccion_despacho and len(direccion_despacho) > 200:
            flash('La dirección de despacho no puede exceder 200 caracteres.', 'error')
            return redirect(url_for('customers.create'))

        existing_user = db.session.query(User).filter_by(correo_electronico=correo_electronico).first()
        if existing_user:
            flash('Ya existe una cuenta con ese correo electrónico.', 'error')
            return redirect(url_for('customers.create'))

        # Contraseña por defecto: nombre completo sin espacios
        default_password = nombre_completo.replace(' ', '')

        try:
            user = User(
                nombre_completo=nombre_completo,
                correo_electronico=correo_electronico,
                password=default_password,
                rol_asignado=UserRole.CUSTOMER,
            )
            db.session.add(user)
            db.session.flush()  # ensure user.id

            customer = Customer(
                user=user,
                telefono=telefono,
                direccion_despacho=direccion_despacho,
            )
            db.session.add(customer)
            db.session.commit()

            user_logger.log_action(
                current_user,
                module="Clientes",
                action=f"Se creó el cliente {user.nombre_completo} con ID {customer.id}",
                success=True,
            )

            flash('Cliente creado exitosamente.', 'success')
            return redirect(url_for('customers.index'))
        except Exception:
            db.session.rollback()
            user_logger.log_action(
                current_user,
                module="Clientes",
                action=f"Error al crear el cliente {nombre_completo}",
                success=False,
            )
            flash('No se pudo crear el cliente. Intenta nuevamente.', 'error')
            return redirect(url_for('customers.create'))

    return render_template('internal/customers/create.html')


@customers_bp.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'seller')
def edit(customer_id: int):
    customer = db.session.query(Customer).filter_by(id=customer_id, is_active=True).first()
    if not customer:
        flash('Cliente no encontrado.', 'error')
        return redirect(url_for('customers.index'))

    user = db.session.query(User).filter_by(id=customer.user_id).first()
    if not user:
        return "Usuario del cliente no encontrado", 404

    if request.method == 'POST':
        nombre_completo = (request.form.get('nombre_completo') or '').strip()
        correo_electronico = User.normalize_email(request.form.get('correo_electronico') or '')
        telefono = (request.form.get('telefono') or '').strip()
        direccion_despacho = (request.form.get('direccion_despacho') or '').strip()
        puntos_raw = (request.form.get('puntos_acumulados') or '').strip()

        if not nombre_completo:
            flash('El nombre completo es obligatorio.', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

        if len(nombre_completo) > 150:
            flash('El nombre completo no puede exceder 150 caracteres.', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

        if not _is_valid_email(correo_electronico):
            flash('Ingresa un correo electrónico válido.', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

        if not _is_valid_phone(telefono):
            flash('Ingresa un teléfono válido (solo números).', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

        if direccion_despacho and len(direccion_despacho) > 200:
            flash('La dirección de despacho no puede exceder 200 caracteres.', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

        try:
            puntos_acumulados = int(puntos_raw)
        except (TypeError, ValueError):
            flash('Los puntos acumulados deben ser un número entero.', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

        if puntos_acumulados < 0:
            flash('Los puntos acumulados no pueden ser negativos.', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

        email_owner = db.session.query(User).filter_by(correo_electronico=correo_electronico).first()
        if email_owner and email_owner.id != user.id:
            flash('Ya existe una cuenta con ese correo electrónico.', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

        try:
            # User: nombre y correo (sin modificar contraseña)
            user.nombre_completo = nombre_completo
            user.correo_electronico = correo_electronico

            # Customer: teléfono, dirección y puntos
            customer.telefono = telefono
            customer.direccion_despacho = direccion_despacho
            customer.puntos_acumulados = puntos_acumulados

            db.session.commit()
            
            user_logger.log_action(
                current_user,
                module="Clientes",
                action=f"Se actualizó el cliente {user.nombre_completo} con ID {customer.id}",
                success=True,
            )
            
            flash('Cliente actualizado exitosamente.', 'success')
            return redirect(url_for('customers.index'))
        except Exception:
            db.session.rollback()
            user_logger.log_action(
                current_user,
                module="Clientes",
                action=f"Error al actualizar el cliente {user.nombre_completo} con ID {customer.id}",
                success=False,
            )
            flash('No se pudo actualizar el cliente. Intenta nuevamente.', 'error')
            return redirect(url_for('customers.edit', customer_id=customer_id))

    return render_template('internal/customers/edit.html', customer=customer)

@customers_bp.route('/delete/<int:customer_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'seller')
def delete(customer_id: int):
    customer = db.session.query(Customer).filter_by(id=customer_id, is_active=True).first()
    if not customer:
        flash('Cliente no encontrado.', 'error')
        return redirect(url_for('customers.index'))

    if request.method == 'POST':
        try:
            user = customer.user
            if user:
                user.is_active = False
                user.correo_electronico = f"{user.correo_electronico}.deleted.{user.id}"
            customer.is_active = False
            db.session.commit()
            user_logger.log_action(
                current_user,
                module="Clientes",
                action=f"Se eliminó el cliente {user.nombre_completo} con ID {customer.id}",
                success=True,
            )
            flash('Cliente eliminado exitosamente.', 'success')
            return redirect(url_for('customers.index'))
        except Exception as e:
            db.session.rollback()
            user_logger.log_action(
                current_user,
                module="Clientes",
                action=f"Error al eliminar el cliente {getattr(customer.user, 'nombre_completo', 'unknown')} con ID {customer.id}",
                success=False,
            )
            return f"Error al eliminar cliente: {e}", 500
    return render_template('internal/customers/delete.html', customer=customer)
