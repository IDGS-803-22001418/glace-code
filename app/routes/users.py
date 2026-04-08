import math
import re
from datetime import datetime
from typing import TypedDict
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user # type: ignore
from sqlalchemy import func, or_
from app import db, user_logger
from app.decorators import roles_required
from app.models import User, UserRole

users_bp = Blueprint('users', __name__)


class UserRow(TypedDict):
    id: int
    nombre_completo: str
    correo_electronico: str
    rol_asignado: str
    initials: str


class UserLogRow(TypedDict):
    id: str
    date: str
    user_name: str
    module: str
    action: str
    success: bool


def _is_valid_email(email: str) -> bool:
    email = (email or '').strip()
    if not email or len(email) > 150:
        return False
    return re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email) is not None

@users_bp.route('/')
@login_required
@roles_required('admin')
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

    base_query = db.session.query(User).filter(User.rol_asignado != UserRole.CUSTOMER, User.is_active == True)  # type: ignore[arg-type]

    if raw_query:
        like = f"%{raw_query.lower()}%"
        base_query = base_query.filter(
            or_(
                func.lower(User.nombre_completo).like(like),
                func.lower(User.correo_electronico).like(like),
                func.lower(User.rol_asignado).like(like),
            )
        )

    total = base_query.count()
    total_pages = max(1, math.ceil(total / per_page))
    if page > total_pages:
        page = total_pages

    users = (
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

    rows: list[UserRow] = []
    for user in users:
        rows.append(
            {
                'id': user.id,
                'nombre_completo': user.nombre_completo,
                'correo_electronico': user.correo_electronico,
                'rol_asignado': user.rol_asignado,
                'initials': initials(user.nombre_completo),
            }
        )

    start_item = 0 if total == 0 else ((page - 1) * per_page + 1)
    end_item = min(total, page * per_page)

    return render_template(
        'internal/users/index.html',
        users=rows,
        q=raw_query,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        start_item=start_item,
        end_item=end_item,
    )
    
@users_bp.route('/logs')
@login_required
@roles_required('admin')
def logs():
    raw_query = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int) or 1
    per_page = request.args.get('per_page', 10, type=int) or 10

    if page < 1:
        page = 1
    if per_page < 5:
        per_page = 5
    if per_page > 50:
        per_page = 50

    logs_docs, total = user_logger.get_logs(raw_query, page, per_page)
    total_pages = max(1, math.ceil(total / per_page))

    if page > total_pages:
        page = total_pages
        logs_docs, total = user_logger.get_logs(raw_query, page, per_page)

    rows: list[UserLogRow] = []
    for doc in logs_docs:
        log_date = doc.get('date')
        formatted_date = '-'
        if isinstance(log_date, datetime):
            formatted_date = log_date.strftime('%d/%m/%Y %H:%M:%S')

        rows.append(
            {
                'id': str(doc.get('_id', '')),
                'date': formatted_date,
                'user_name': str(doc.get('user_name') or 'unknown'),
                'module': str(doc.get('module') or '-'),
                'action': str(doc.get('action') or '-'),
                'success': bool(doc.get('success', False)),
            }
        )

    start_item = 0 if total == 0 else ((page - 1) * per_page + 1)
    end_item = min(total, page * per_page)

    return render_template(
        'internal/users/logs.html',
        logs=rows,
        q=raw_query,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        start_item=start_item,
        end_item=end_item,
    )


@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create():
    if request.method == 'POST':
        nombre_completo = (request.form.get('nombre_completo') or '').strip()
        correo_electronico = User.normalize_email(request.form.get('correo_electronico') or '')
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''
        rol_asignado = (request.form.get('rol_asignado') or '').strip().lower()

        allowed_roles = {UserRole.ADMIN, UserRole.CHEF, UserRole.SELLER}

        if not nombre_completo:
            flash('El nombre completo es obligatorio.', 'error')
            return redirect(url_for('users.create'))

        if len(nombre_completo) > 150:
            flash('El nombre completo no puede exceder 150 caracteres.', 'error')
            return redirect(url_for('users.create'))

        if not _is_valid_email(correo_electronico):
            flash('Ingresa un correo electrónico válido.', 'error')
            return redirect(url_for('users.create'))

        if not password or len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'error')
            return redirect(url_for('users.create'))

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('users.create'))

        if rol_asignado not in allowed_roles:
            flash('Selecciona un rol válido para el usuario.', 'error')
            return redirect(url_for('users.create'))

        existing_user = db.session.query(User).filter_by(correo_electronico=correo_electronico).first()
        if existing_user:
            flash('Ya existe una cuenta con ese correo electrónico.', 'error')
            return redirect(url_for('users.create'))

        try:
            user = User(
                nombre_completo=nombre_completo,
                correo_electronico=correo_electronico,
                password=password,
                rol_asignado=rol_asignado,
            )
            db.session.add(user)
            db.session.commit()
            user_logger.log_action(
                current_user,
                module="Usuarios",
                action=f"Se creó el usuario {user.nombre_completo} con ID {user.id}",
                success=True
            )
            flash('Usuario registrado exitosamente.', 'success')
            return redirect(url_for('users.index'))
        except Exception:
            db.session.rollback()
            user_logger.log_action(
                current_user,
                module="Usuarios",
                action=f"Error al crear el usuario {nombre_completo}",
                success=False
            )
            flash('No se pudo registrar el usuario. Intenta nuevamente.', 'error')
            return redirect(url_for('users.create'))

    return render_template('internal/users/create.html')


@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit(user_id: int):
    user = db.session.query(User).filter_by(id=user_id, is_active=True).first()
    if not user:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('users.index'))

    if user.rol_asignado == UserRole.CUSTOMER:
        flash('Este módulo no permite editar usuarios con rol cliente.', 'error')
        return redirect(url_for('users.index'))

    if request.method == 'POST':
        nombre_completo = (request.form.get('nombre_completo') or '').strip()
        correo_electronico = User.normalize_email(request.form.get('correo_electronico') or '')
        rol_asignado = (request.form.get('rol_asignado') or '').strip().lower()
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''

        allowed_roles = {UserRole.ADMIN, UserRole.CHEF, UserRole.SELLER}

        if not nombre_completo:
            flash('El nombre completo es obligatorio.', 'error')
            return redirect(url_for('users.edit', user_id=user.id))

        if len(nombre_completo) > 150:
            flash('El nombre completo no puede exceder 150 caracteres.', 'error')
            return redirect(url_for('users.edit', user_id=user.id))

        if not _is_valid_email(correo_electronico):
            flash('Ingresa un correo electrónico válido.', 'error')
            return redirect(url_for('users.edit', user_id=user.id))

        if rol_asignado not in allowed_roles:
            flash('Selecciona un rol válido para el usuario.', 'error')
            return redirect(url_for('users.edit', user_id=user.id))

        existing_user = db.session.query(User).filter_by(correo_electronico=correo_electronico).first()
        if existing_user and existing_user.id != user.id:
            flash('Ya existe una cuenta con ese correo electrónico.', 'error')
            return redirect(url_for('users.edit', user_id=user.id))

        if user.rol_asignado == UserRole.ADMIN and rol_asignado != UserRole.ADMIN:
            admin_count = db.session.query(User).filter_by(rol_asignado=UserRole.ADMIN, is_active=True).count()
            if admin_count <= 1:
                flash('Debe existir al menos un usuario administrador en el sistema.', 'error')
                return redirect(url_for('users.edit', user_id=user.id))

        if password:
            if len(password) < 8:
                flash('La contraseña debe tener al menos 8 caracteres.', 'error')
                return redirect(url_for('users.edit', user_id=user.id))

            if password != confirm_password:
                flash('Las contraseñas no coinciden.', 'error')
                return redirect(url_for('users.edit', user_id=user.id))

        try:
            user.nombre_completo = nombre_completo
            user.correo_electronico = correo_electronico
            user.rol_asignado = rol_asignado

            if password:
                user.set_password(password)

            db.session.commit()
            user_logger.log_action(
                current_user,
                module="Usuarios",
                action=f"Se actualizó el usuario {user.nombre_completo} con ID {user.id}",
                success=True
            )
            flash('Usuario actualizado exitosamente.', 'success')
            return redirect(url_for('users.index'))
        except Exception:
            db.session.rollback()
            user_logger.log_action(
                current_user,
                module="Usuarios",
                action=f"Error al actualizar el usuario {user.nombre_completo} con ID {user.id}",
                success=False
            )

            flash('No se pudo actualizar el usuario. Intenta nuevamente.', 'error')
            return redirect(url_for('users.edit', user_id=user.id))

    return render_template('internal/users/edit.html', user=user)


@users_bp.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def delete(user_id: int):
    user = db.session.query(User).filter_by(id=user_id, is_active=True).first()
    if not user:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('users.index'))

    if user.rol_asignado == UserRole.CUSTOMER:
        flash('Este módulo no permite eliminar usuarios con rol cliente.', 'error')
        return redirect(url_for('users.index'))

    is_self = user.id == current_user.id
    admin_count = db.session.query(User).filter_by(rol_asignado=UserRole.ADMIN, is_active=True).count()
    is_last_admin = user.rol_asignado == UserRole.ADMIN and admin_count <= 1

    if request.method == 'POST':
        if is_self:
            flash('No puedes eliminar tu propio usuario.', 'error')
            return redirect(url_for('users.delete', user_id=user.id))

        if is_last_admin:
            flash('Debe existir al menos un usuario administrador en el sistema.', 'error')
            return redirect(url_for('users.delete', user_id=user.id))

        try:
            user.is_active = False
            user.correo_electronico = f"{user.correo_electronico}.deleted.{user.id}"
            db.session.commit()
            user_logger.log_action(
                current_user,
                module="Usuarios",
                action=f"Se eliminó el usuario {user.nombre_completo} con ID {user.id}",
                success=True
            )
            flash('Usuario eliminado exitosamente.', 'success')
            return redirect(url_for('users.index'))
        except Exception:
            db.session.rollback()
            user_logger.log_action(
                current_user,
                module="Usuarios",
                action=f"Error al eliminar el usuario {user.nombre_completo} con ID {user.id}",
                success=False
            )
            flash('No se pudo eliminar el usuario. Intenta nuevamente.', 'error')
            return redirect(url_for('users.delete', user_id=user.id))

    return render_template(
        'internal/users/delete.html',
        user=user,
        is_self=is_self,
        is_last_admin=is_last_admin,
    )
