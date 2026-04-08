import re
from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user  # type: ignore
from app import db, user_logger
from app.models import User, Customer, UserRole

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email') or ''
        password = request.form.get('password') or ''

        user = db.session.query(User).filter_by(correo_electronico=email).first()
        if user and user.is_active and user.check_password(password):
            login_user(user)

            # Log successful login
            if not user.is_customer():
                user_logger.log_action(
                    current_user=user,
                    module="Autenticación",
                    action="Usuario inició sesión",
                    success=True,
                )

            next_page = request.args.get('next')
            print(f"Next page: {next_page}")
            if next_page:
                return redirect(next_page)
            elif user.is_customer():
                return redirect(url_for('main.index'))
            else:
                return redirect(url_for('main.internal'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'error')
            return redirect(url_for('auth.login'))
    
    if current_user.is_authenticated:
        if current_user.is_customer():
            return redirect(url_for('main.index'))
        else:
            return redirect(url_for('main.internal'))
    return render_template('login.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))

def _is_valid_email(email: str) -> bool:
    email = (email or '').strip()
    if not email or len(email) > 150:
        return False
    # Simple, pragmatic validation; database uniqueness is enforced separately.
    return re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email) is not None


def _is_valid_phone(phone: str) -> bool:
    phone = (phone or '').strip()
    if not phone or len(phone) > 20:
        return False
    # Allow optional leading '+' and then digits only.
    return re.match(r"^\+?[0-9]{7,20}$", phone) is not None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre_completo = (request.form.get('nombre_completo') or '').strip()
        correo_electronico = User.normalize_email(request.form.get('correo_electronico') or '')
        telefono = (request.form.get('telefono') or '').strip()
        direccion_despacho = (request.form.get('direccion_despacho') or '').strip()
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''

        if not nombre_completo:
            flash('El nombre completo es obligatorio.', 'error')
            return redirect(url_for('auth.register'))

        if len(nombre_completo) > 150:
            flash('El nombre completo no puede exceder 150 caracteres.', 'error')
            return redirect(url_for('auth.register'))

        if not _is_valid_email(correo_electronico):
            flash('Ingresa un correo electrónico válido.', 'error')
            return redirect(url_for('auth.register'))

        if not telefono:
            flash('El teléfono es obligatorio.', 'error')
            return redirect(url_for('auth.register'))

        if not _is_valid_phone(telefono):
            flash('Ingresa un teléfono válido (solo números).', 'error')
            return redirect(url_for('auth.register'))

        if not direccion_despacho:
            flash('La dirección de despacho es obligatoria.', 'error')
            return redirect(url_for('auth.register'))

        if len(direccion_despacho) > 200:
            flash('La dirección de despacho no puede exceder 200 caracteres.', 'error')
            return redirect(url_for('auth.register'))

        if not password or len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'error')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('auth.register'))

        existing_user = db.session.query(User).filter_by(correo_electronico=correo_electronico).first()
        if existing_user:
            flash('Ya existe una cuenta con ese correo electrónico.', 'error')
            return redirect(url_for('auth.register'))

        try:
            user = User(
                nombre_completo=nombre_completo,
                correo_electronico=correo_electronico,
                password=password,
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

            login_user(user)
            return redirect(url_for('main.index'))
        except Exception:
            db.session.rollback()
            flash('No se pudo crear la cuenta. Intenta nuevamente.', 'error')
            return redirect(url_for('auth.register'))

    if current_user.is_authenticated:
        if current_user.is_customer():
            return redirect(url_for('main.index'))
        return redirect(url_for('main.internal'))

    return render_template('register.html')