from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user # type: ignore
from app.decorators import roles_required
from app.models import Supplier
from app import db, user_logger

categorias = [
    'Materias Primas', 'Packaging', 'Lácteos', 'Chocolates',
    'Frutas', 'Esencias', 'Decoraciones', 'Insumos de Repostería', 'Otros'
]

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/')
@login_required
@roles_required('admin')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Supplier.query.filter_by(is_active=True)
    if search:
        query = query.filter(
            (Supplier.nombre_empresa.ilike(f'%{search}%')) |
            (Supplier.categoria_insumos.ilike(f'%{search}%')) |
            (Supplier.nombre_contacto.ilike(f'%{search}%')) |
            (Supplier.correo_electronico.ilike(f'%{search}%'))
        )

    pagination = query.paginate(page=page, per_page=10, error_out=False)
    proveedores = pagination.items
    total = pagination.total
    total_pages = pagination.pages

    return render_template('internal/suppliers/index.html',
                           proveedores=proveedores,
                           total=total,
                           page=page,
                           total_pages=total_pages,
                           search=search)

@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create():
    if request.method == 'POST':
        nombre_empresa = request.form.get('nombre_empresa')
        categoria_insumos = request.form.get('categoria_insumos')
        nombre_contacto = request.form.get('nombre_contacto')
        telefono = request.form.get('telefono')
        correo_electronico = request.form.get('correo_electronico')
        direccion_fisica = request.form.get('direccion_fisica')
        notas_adicionales = request.form.get('notas_adicionales')

        nuevo_proveedor = Supplier(
            nombre_empresa=nombre_empresa,
            categoria_insumos=categoria_insumos,
            nombre_contacto=nombre_contacto,
            telefono=telefono,
            correo_electronico=correo_electronico,
            direccion_fisica=direccion_fisica,
            notas_adicionales=notas_adicionales
        )

        db.session.add(nuevo_proveedor)
        db.session.commit()
        user_logger.log_action(
            current_user,
            module="Proveedores",
            action=f"Se creó el proveedor {nuevo_proveedor.nombre_empresa}",
            success=True,
        )

        return redirect(url_for('suppliers.index'))

    return render_template('internal/suppliers/create.html', categorias=categorias)

@suppliers_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit(id):
    supplier = Supplier.query.filter_by(id=id, is_active=True).first_or_404()

    if request.method == 'POST':
        supplier.nombre_empresa = request.form.get('nombre_empresa')
        supplier.categoria_insumos = request.form.get('categoria_insumos')
        supplier.nombre_contacto = request.form.get('nombre_contacto')
        supplier.telefono = request.form.get('telefono')
        supplier.correo_electronico = request.form.get('correo_electronico')
        supplier.direccion_fisica = request.form.get('direccion_fisica')
        supplier.notas_adicionales = request.form.get('notas_adicionales')

        db.session.commit()
        user_logger.log_action(
            current_user,
            module="Proveedores",
            action=f"Se actualizó el proveedor {supplier.nombre_empresa}",
            success=True,
        )
        return redirect(url_for('suppliers.index'))

    return render_template('internal/suppliers/edit.html', proveedor=supplier, categorias=categorias)

@suppliers_bp.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def delete(id):
    supplier = Supplier.query.filter_by(id=id, is_active=True).first_or_404()

    if request.method == 'POST':
        supplier.is_active = False
        db.session.commit()
        user_logger.log_action(
            current_user,
            module="Proveedores",
            action=f"Se eliminó el proveedor {supplier.nombre_empresa}",
            success=True,
        )
        return redirect(url_for('suppliers.index'))

    return render_template('internal/suppliers/delete.html', proveedor=supplier)
