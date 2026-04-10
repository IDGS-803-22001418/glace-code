from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user # type: ignore
from app.decorators import roles_required
from app.models import Purchase, Supplier, Insumo, PurchaseDetail, UnidadMedida
from app import db, user_logger
from sqlalchemy import or_

compras_bp = Blueprint('purchases', __name__)

@compras_bp.route('/')
@roles_required('admin', 'chef', 'seller')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Purchase.query.filter_by(is_active=True)
    
    if search:
        query = query.join(Supplier).filter(
            or_(
                Purchase.id.like(f"%{search}%"),
                Supplier.nombre_empresa.ilike(f"%{search}%"),
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
    
    query = Purchase.query.filter_by(is_active=True)
    
    if search:
        query = query.join(Supplier).filter(
            or_(
                Purchase.id.like(f"%{search}%"),
                Supplier.nombre_empresa.ilike(f"%{search}%"),
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
            unidades_medida_ids = request.form.getlist('unidad_medida_id[]')
            
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

                unidad_medida_id = int(unidades_medida_ids[i]) if unidades_medida_ids and i < len(unidades_medida_ids) else insumo.unidad_base_id
                
                detalle = PurchaseDetail(
                    purchase_id=nueva_compra.id,
                    insumo_id=insumo.id,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    unidad_medida_id=unidad_medida_id
                )
                db.session.add(detalle)
                
                # Assign insumo explicitly to calculate base quantity correctly
                detalle.insumo = insumo
                cant_base = detalle.cantidad_en_unidad_base()
                if cant_base is not None:
                    insumo.stock_actual += cant_base
                else:
                    insumo.stock_actual += cantidad
            
            db.session.commit()
            user_logger.log_action(
                current_user,
                module="Compras",
                action="Se registró una compra al proveedor",
                success=True,
            )
            flash('Compra registrada exitosamente.', 'success')
            return redirect(url_for('purchases.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la compra: {str(e)}', 'error')
            return redirect(url_for('purchases.crear'))

    proveedores = Supplier.query.filter_by(is_active=True).all()
    insumos = Insumo.query.filter_by(is_active=True).all()
    # Convertimos los insumos a una lista de diccionarios para el tojson de Jinja
    # Incluimos categoria y unidad base para el filtrado y visualización client-side
    insumos_json = []
    for i in insumos:
        conversions = [{'id': i.unidad_base.id, 'nombre': i.unidad_base.nombre, 'abreviatura': i.unidad_base.abreviatura}] if i.unidad_base else []
        for conv in i.conversiones:
            if conv.is_active and conv.unidad_destino:
                conversions.append({
                    'id': conv.unidad_destino.id,
                    'nombre': conv.unidad_destino.nombre,
                    'abreviatura': conv.unidad_destino.abreviatura
                })
        insumos_json.append({
            'id': i.id, 
            'nombre_insumo': i.nombre_insumo, 
            'categoria': i.categoria,
            'unidad_base': i.unidad_base.abreviatura if i.unidad_base else '',
            'unidades_permitidas': conversions
        })
    
    return render_template('internal/purchases/crear.html', 
                         proveedores=proveedores, 
                         insumos=insumos_json)

@compras_bp.route('/ver/<int:id>')
@roles_required('admin', 'chef', 'seller')
@login_required
def ver(id):
    compra = Purchase.query.filter_by(id=id, is_active=True).first()
    if not compra:
        flash('Compra no encontrada.', 'error')
        return redirect(url_for('purchases.index'))
    return render_template('internal/purchases/ver.html', compra=compra)

@compras_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@roles_required('admin', 'chef', 'seller')
@login_required
def editar(id):
    compra = Purchase.query.filter_by(id=id, is_active=True).first()
    if not compra:
        flash('Compra no encontrada.', 'error')
        return redirect(url_for('purchases.index'))
    
    if request.method == 'POST':
        try:
            # Revertir stock actual de los detalles viejos antes de borrarlos
            for detalle in compra.detalles:
                insumo = detalle.insumo
                if insumo:
                    cant_base = detalle.cantidad_en_unidad_base()
                    if cant_base is not None:
                        insumo.stock_actual -= cant_base
                    else:
                        insumo.stock_actual -= detalle.cantidad
            
            # Limpiar detalles viejos
            PurchaseDetail.query.filter_by(purchase_id=compra.id).delete()
            
            # Obtener datos del formulario
            proveedor_id = request.form.get('proveedor_id')
            insumo_ids = request.form.getlist('insumo_id[]')
            cantidades = request.form.getlist('cantidad[]')
            precios = request.form.getlist('precio_unitario[]')
            unidades_medida_ids = request.form.getlist('unidad_medida_id[]')
            
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
                unidad_medida_id = int(unidades_medida_ids[i]) if unidades_medida_ids and i < len(unidades_medida_ids) else insumo.unidad_base_id
                
                nuevo_detalle = PurchaseDetail(
                    insumo_id=insumo.id,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    unidad_medida_id=unidad_medida_id
                )
                compra.detalles.append(nuevo_detalle)
                
                # Sumar nuevo stock
                nuevo_detalle.insumo = insumo
                cant_base = nuevo_detalle.cantidad_en_unidad_base()
                if cant_base is not None:
                    insumo.stock_actual += cant_base
                else:
                    insumo.stock_actual += cantidad
            
            db.session.commit()
            user_logger.log_action(
                current_user,
                module="Compras",
                action="Se actualizó una compra",
                success=True,
            )
            flash('Compra actualizada exitosamente.', 'success')
            return redirect(url_for('purchases.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la compra: {str(e)}', 'error')
            return redirect(url_for('purchases.editar', id=id))

    # GET: Preparar datos para el formulario
    proveedores = Supplier.query.filter_by(is_active=True).all()
    insumos = Insumo.query.filter_by(is_active=True).all()
    insumos_json = []
    for i in insumos:
        conversions = [{'id': i.unidad_base.id, 'nombre': i.unidad_base.nombre, 'abreviatura': i.unidad_base.abreviatura}] if i.unidad_base else []
        for conv in i.conversiones:
            if conv.is_active and conv.unidad_destino:
                conversions.append({
                    'id': conv.unidad_destino.id,
                    'nombre': conv.unidad_destino.nombre,
                    'abreviatura': conv.unidad_destino.abreviatura
                })
        insumos_json.append({
            'id': i.id, 
            'nombre_insumo': i.nombre_insumo, 
            'categoria': i.categoria,
            'unidad_base': i.unidad_base.abreviatura if i.unidad_base else '',
            'unidades_permitidas': conversions
        })
    
    # Transfomar detalles actuales para facilidad en JS
    detalles_json = [
        {
            'insumo_id': d.insumo_id,
            'cantidad': d.cantidad,
            'precio_unitario': d.precio_unitario,
            'unidad_medida_id': d.unidad_medida_id
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
    compra = Purchase.query.filter_by(id=id, is_active=True).first()
    if not compra:
        flash('Compra no encontrada.', 'error')
        return redirect(url_for('purchases.index'))
    
    if request.method == 'POST':
        try:
            # Revertir stock actual de los detalles antes de borrar la compra
            for detalle in compra.detalles:
                if detalle.insumo:
                    cant_base = detalle.cantidad_en_unidad_base()
                    if cant_base is not None:
                        detalle.insumo.stock_actual -= cant_base
                    else:
                        detalle.insumo.stock_actual -= detalle.cantidad
            
            compra.is_active = False
            db.session.commit()
            user_logger.log_action(
                current_user,
                module="Compras",
                action="Se eliminó una compra",
                success=True,
            )
            flash('Compra eliminada y stock actualizado correctamente.', 'success')
            return redirect(url_for('purchases.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar la compra: {str(e)}', 'error')
            return redirect(url_for('purchases.index'))
            
    return render_template('internal/purchases/eliminar.html', compra=compra)
