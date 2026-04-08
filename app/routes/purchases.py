from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required # type: ignore
from app.decorators import roles_required
from app.models import Purchase, Supplier, Insumo, PurchaseDetail, UnidadMedida
from app import db
from sqlalchemy import or_

compras_bp = Blueprint('purchases', __name__)

@compras_bp.route('/')
@roles_required('admin', 'chef', 'seller')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Purchase.query
    
    if search:
        query = query.join(Supplier).filter(
            or_(
                Purchase.id.like(f"%{search}%"),
                Supplier.nombre_empresa.ilike(f"%{search}%"),
                Purchase.estado_pedido.ilike(f"%{search}%")
            )
        )
    
    pagination = query.order_by(Purchase.id.desc()).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('internal/purchases/index.html', 
                         compras=pagination.items, 
                         total=pagination.total, 
                         page=page, 
                         total_pages=pagination.pages, 
                         search=search)

@compras_bp.route('/api/buscar')
@roles_required('admin', 'chef', 'seller')
@login_required
def api_buscar():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Purchase.query
    
    if search:
        query = query.join(Supplier).filter(
            or_(
                Purchase.id.like(f"%{search}%"),
                Supplier.nombre_empresa.ilike(f"%{search}%"),
                Purchase.estado_pedido.ilike(f"%{search}%")
            )
        )
    
    pagination = query.order_by(Purchase.id.desc()).paginate(page=page, per_page=10, error_out=False)
    
    compras_data = []
    for c in pagination.items:
        compras_data.append({
            'id': c.id,
            'proveedor_nombre': c.proveedor_nombre,
            'fecha_orden': c.fecha_orden.strftime('%d/%m/%Y') if c.fecha_orden else 'N/A',
            'total': c.total,
            'estado_pedido': c.estado_pedido
        })
        
    return jsonify({
        'compras': compras_data,
        'total': pagination.total,
        'page': page,
        'total_pages': pagination.pages
    })

@compras_bp.route('/crear', methods=['GET', 'POST'])
@roles_required('admin', 'chef', 'seller')
@login_required
def crear():
    if request.method == 'POST':
        try:
            proveedor_id = request.form.get('proveedor_id')            
            insumo_ids = request.form.getlist('insumo_id[]')
            cantidades = request.form.getlist('cantidad[]')
            precios = request.form.getlist('precio_unitario[]')
            
            if not insumo_ids:
                flash('La orden debe tener al menos un insumo.', 'error')
                return redirect(url_for('purchases.crear'))
            
            nueva_compra = Purchase(
                supplier_id=int(proveedor_id),
                fecha_orden=db.func.current_timestamp(),
            )
            
            db.session.add(nueva_compra)
            db.session.flush() # Para obtener el ID de la compra
            
            subtotal_acumulado = 0
            
            for i in range(len(insumo_ids)):
                insumo = db.session.get(Insumo, int(insumo_ids[i]))
                if not insumo:
                    continue
                
                cantidad = float(cantidades[i])
                precio = float(precios[i])
                subtotal_acumulado += (cantidad * precio)
                
                # Validación: Check if supply category matches supplier category
                if insumo.categoria != nueva_compra.supplier.categoria_insumos:
                    # In this specific app, it might be allowed but we follow the logic:
                    # "ese proveedor solo puede proveer insumos de esa categoria"
                    flash(f'El insumo "{insumo.nombre_insumo}" no pertenece a la categoría "{nueva_compra.supplier.categoria_insumos}" del proveedor.', 'error')
                    db.session.rollback()
                    return redirect(url_for('purchases.crear'))

                detalle = PurchaseDetail(
                    purchase_id=nueva_compra.id,
                    insumo_id=insumo.id,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    unidad_medida_id=insumo.unidad_base_id # Usamos la unidad base por defecto
                )
                db.session.add(detalle)
                
                insumo.stock_actual += cantidad
            
            db.session.commit()
            flash('Compra registrada exitosamente.', 'success')
            return redirect(url_for('purchases.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la compra: {str(e)}', 'error')
            return redirect(url_for('purchases.crear'))

    proveedores = Supplier.query.all()
    insumos = Insumo.query.filter_by(is_active=True).all()
    # Convertimos los insumos a una lista de diccionarios para el tojson de Jinja
    # Incluimos categoria y unidad base para el filtrado y visualización client-side
    insumos_json = [
        {
            'id': i.id, 
            'nombre_insumo': i.nombre_insumo, 
            'categoria': i.categoria,
            'unidad_base': i.unidad_base.abreviatura if i.unidad_base else ''
        } for i in insumos
    ]
    
    return render_template('internal/purchases/crear.html', 
                         proveedores=proveedores, 
                         insumos=insumos_json)

@compras_bp.route('/ver/<int:id>')
@roles_required('admin', 'chef', 'seller')
@login_required
def ver(id):
    compra = db.session.get(Purchase, id)
    if not compra:
        flash('Compra no encontrada.', 'error')
        return redirect(url_for('purchases.index'))
    return render_template('internal/purchases/ver.html', compra=compra)

@compras_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@roles_required('admin', 'chef', 'seller')
@login_required
def editar(id):
    compra = db.session.get(Purchase, id)
    if not compra:
        flash('Compra no encontrada.', 'error')
        return redirect(url_for('purchases.index'))
    
    if request.method == 'POST':
        try:
            # Revertir stock actual de los detalles viejos antes de borrarlos
            for detalle in compra.detalles:
                insumo = detalle.insumo
                if insumo:
                    insumo.stock_actual -= detalle.cantidad
            
            # Limpiar detalles viejos
            PurchaseDetail.query.filter_by(purchase_id=compra.id).delete()
            
            # Obtener datos del formulario
            proveedor_id = request.form.get('proveedor_id')
            insumo_ids = request.form.getlist('insumo_id[]')
            cantidades = request.form.getlist('cantidad[]')
            precios = request.form.getlist('precio_unitario[]')
            
            if not insumo_ids:
                flash('La orden debe tener al menos un insumo.', 'error')
                return redirect(url_for('purchases.editar', id=id))
            
            # Limpiar detalles viejos de la colección (esto activará el delete-orphan en la DB)
            compra.detalles = []
            db.session.flush()

            # Actualizar el proveedor
            compra.supplier_id = int(proveedor_id)
            
            # Verificar proveedor para validación de categoría
            proveedor = db.session.get(Supplier, int(proveedor_id))
            
            for i in range(len(insumo_ids)):
                insumo = db.session.get(Insumo, int(insumo_ids[i]))
                if not insumo:
                    continue
                
                # Validación: Check if supply category matches supplier category
                if insumo.categoria != proveedor.categoria_insumos:
                    flash(f'El insumo "{insumo.nombre_insumo}" no pertenece a la categoría "{proveedor.categoria_insumos}" del proveedor.', 'error')
                    db.session.rollback()
                    return redirect(url_for('purchases.editar', id=id))

                cantidad = float(cantidades[i])
                precio = float(precios[i])
                
                nuevo_detalle = PurchaseDetail(
                    insumo_id=insumo.id,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    unidad_medida_id=insumo.unidad_base_id
                )
                compra.detalles.append(nuevo_detalle)
                
                # Sumar nuevo stock
                insumo.stock_actual += cantidad
            
            db.session.commit()
            flash('Compra actualizada exitosamente.', 'success')
            return redirect(url_for('purchases.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la compra: {str(e)}', 'error')
            return redirect(url_for('purchases.editar', id=id))

    # GET: Preparar datos para el formulario
    proveedores = Supplier.query.all()
    insumos = Insumo.query.filter_by(is_active=True).all()
    insumos_json = [
        {
            'id': i.id, 
            'nombre_insumo': i.nombre_insumo, 
            'categoria': i.categoria,
            'unidad_base': i.unidad_base.abreviatura if i.unidad_base else ''
        } for i in insumos
    ]
    
    # Transfomar detalles actuales para facilidad en JS
    detalles_json = [
        {
            'insumo_id': d.insumo_id,
            'cantidad': d.cantidad,
            'precio_unitario': d.precio_unitario,
            'unidad_base': d.insumo.unidad_base.abreviatura if d.insumo and d.insumo.unidad_base else ''
        } for d in compra.detalles
    ]
    
    return render_template('internal/purchases/editar.html', 
                         compra=compra,
                         detalles_json=detalles_json,
                         proveedores=proveedores, 
                         insumos=insumos_json)

@compras_bp.route('/eliminar/<int:id>', methods=['GET', 'POST'])
@roles_required('admin', 'chef', 'seller')
@login_required
def eliminar(id):
    compra = db.session.get(Purchase, id)
    if not compra:
        flash('Compra no encontrada.', 'error')
        return redirect(url_for('purchases.index'))
    
    if request.method == 'POST':
        try:
            # Revertir stock actual de los detalles antes de borrar la compra
            for detalle in compra.detalles:
                if detalle.insumo:
                    detalle.insumo.stock_actual -= detalle.cantidad
            
            db.session.delete(compra)
            db.session.commit()
            flash('Compra eliminada y stock actualizado correctamente.', 'success')
            return redirect(url_for('purchases.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar la compra: {str(e)}', 'error')
            return redirect(url_for('purchases.index'))
            
    return render_template('internal/purchases/eliminar.html', compra=compra)
