from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db, user_logger
from app.models import Insumo, UnidadMedida
from sqlalchemy import or_
from app.forms import InsumoForm
from flask_login import login_required, current_user # type: ignore
from app.decorators import roles_required

categorias = [
    'Materias Primas', 'Packaging', 'Lácteos', 'Chocolates',
    'Frutas', 'Esencias', 'Decoraciones', 'Insumos de Repostería', 'Otros'
]

supplies_bp = Blueprint('supplies', __name__)

@supplies_bp.route("/", methods=['GET'])
@login_required
@roles_required('admin', 'chef')
def index():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip() # Captura lo que viene del HTML
    
    # 1. Query base (solo activos)
    query = Insumo.query.filter(Insumo.is_active == True)
    
    # 2. Si el usuario escribió algo, filtramos
    if search_query:
        # Aquí es donde se usa el or_ que importamos
        query = query.filter(
            or_(
                Insumo.nombre_insumo.ilike(f'%{search_query}%'),
                Insumo.categoria.ilike(f'%{search_query}%')
            )
        )
    
    # 3. Al final paginamos los resultados (ya sean filtrados o todos)
    insumo_obj = query.paginate(page=page, per_page=10)
    
    return render_template('internal/supplies/Insumos.html', insumo_obj=insumo_obj)

@supplies_bp.route("/nuevo_insumo", methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def nuevo_insumo():
    # 1. Inicializamos el formulario (FlaskForm maneja request.form automáticamente)
    form = InsumoForm()
    
    # 2. Llenamos los catálogos (Unidades de medida)
    unidades = UnidadMedida.query.all()
    form.unidad_base_id.choices = [(u.id, f'{u.nombre} ({u.abreviatura})') for u in unidades]
    
    # 3. Si el formulario es válido tras el envío (POST + CSRF OK)...
    if form.validate_on_submit():
        try:
            # Creamos el nuevo objeto Insumo con los datos del form
            nuevo = Insumo(
                nombre_insumo=form.nombre_insumo.data,
                categoria=form.categoria.data,
                stock_actual=form.stock_actual.data,
                stock_minimo_alerta=form.stock_minimo_alerta.data,
                unidad_base_id=form.unidad_base_id.data
            )
            
            # Guardamos en la base de datos
            db.session.add(nuevo)
            db.session.flush() # Para obtener el ID del nuevo insumo
            
            # Recuperar conversiones del form
            unidades_destino = request.form.getlist('unidad_destino[]')
            factores_conversion = request.form.getlist('factor_conversion[]')

            from app.models import ConversionUnidad
            for u_dest, f_conv in zip(unidades_destino, factores_conversion):
                if u_dest and f_conv:
                    try:
                        nueva_conv = ConversionUnidad(
                            factor_conversion=float(f_conv),
                            unidad_destino_id=int(u_dest),
                            insumo_id=nuevo.id
                        )
                        db.session.add(nueva_conv)
                    except ValueError:
                        pass # Ignorar valores inválidos
            
            db.session.commit()
            user_logger.log_action(
                current_user,
                module="Insumos",
                action="Se registró un nuevo insumo",
                success=True,
            )
            
            flash('¡Insumo registrado con éxito en Maison Glacé!', 'success')
            return redirect(url_for('supplies.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar: {str(e)}', 'danger')
            
    # Si es GET o el formulario falló, mostramos la página de registro
    return render_template('internal/supplies/Registrar.html', form=form, unidades=unidades, categorias=categorias)

@supplies_bp.route("/modificar", methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def modificar():
    create_form = InsumoForm()
    unidades = UnidadMedida.query.all()
    create_form.unidad_base_id.choices = [(u.id, f'{u.nombre} ({u.abreviatura})') for u in unidades]

    # Obtenemos el ID de la URL
    id_url = request.args.get('id')

    # IMPORTANTE: Si no hay ID en la URL, redirigir o mostrar error
    if not id_url:
        flash('No se proporcionó un ID válido', 'danger')
        return redirect(url_for('supplies.index'))

    # Buscamos el insumo
    insumo1 = db.session.query(Insumo).filter(Insumo.id == id_url).first()

    # Si insumo1 es None (no existe), evitamos que truene
    if insumo1 is None:
        flash('El insumo no existe en la base de datos', 'danger')
        return redirect(url_for('supplies.index'))

    if request.method == 'GET':
        # Ahora sí es seguro asignar los datos
        create_form.id.data = insumo1.id
        create_form.nombre_insumo.data = insumo1.nombre_insumo
        create_form.categoria.data = insumo1.categoria
        create_form.stock_actual.data = insumo1.stock_actual
        create_form.stock_minimo_alerta.data = insumo1.stock_minimo_alerta
        create_form.unidad_base_id.data = insumo1.unidad_base_id
        
    if create_form.validate_on_submit():
        # Lógica de guardado...
        insumo1.nombre_insumo = create_form.nombre_insumo.data
        insumo1.categoria = create_form.categoria.data
        insumo1.stock_actual = create_form.stock_actual.data
        insumo1.stock_minimo_alerta = create_form.stock_minimo_alerta.data
        insumo1.unidad_base_id = create_form.unidad_base_id.data
        
        # Procesar conversiones (desactivar las existentes y recrear para simplificar)
        from app.models import ConversionUnidad
        for conv in insumo1.conversiones:
            conv.is_active = False

        unidades_destino = request.form.getlist('unidad_destino[]')
        factores_conversion = request.form.getlist('factor_conversion[]')

        for u_dest, f_conv in zip(unidades_destino, factores_conversion):
            if u_dest and f_conv:
                try:
                    nueva_conv = ConversionUnidad(
                        factor_conversion=float(f_conv),
                        unidad_destino_id=int(u_dest),
                        insumo_id=insumo1.id
                    )
                    db.session.add(nueva_conv)
                except ValueError:
                    pass
        
        db.session.add(insumo1)
        db.session.commit()
        user_logger.log_action(
            current_user,
            module="Insumos",
            action="Se actualizó un insumo",
            success=True,
        )
        flash('Insumo actualizado con éxito', 'success')
        return redirect(url_for('supplies.index'))

    # Traer solo las conversiones activas para pasarlas a la vista
    conversiones_activas = [c for c in insumo1.conversiones if c.is_active]

    return render_template("internal/supplies/Modificar.html", form=create_form, unidades=unidades, conversiones_activas=conversiones_activas, categorias=categorias)

@supplies_bp.route("/eliminar", methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def eliminar_insumo():
    id_url = request.args.get('id')
    
    # Buscamos el insumo para mostrar la información en la pantalla de confirmación
    insumo_del = db.session.query(Insumo).filter(Insumo.id == id_url).first()

    if not insumo_del:
        flash('El insumo no existe', 'danger')
        return redirect(url_for('supplies.index'))

    if request.method == 'POST':
        try:
            insumo_del.is_active = False
            for conversion in insumo_del.conversiones:
                conversion.is_active = False
            db.session.commit()
            user_logger.log_action(
                current_user,
                module="Insumos",
                action="Se eliminó un insumo",
                success=True,
            )
            flash(f'¡{insumo_del.nombre_insumo} eliminado permanentemente!', 'success')
            return redirect(url_for('supplies.index'))
        except Exception as e:
            db.session.rollback()
            flash('No se pudo eliminar el insumo. Puede que haya un conflicto.', 'danger')
            return redirect(url_for('supplies.index'))

    return render_template("internal/supplies/Eliminar.html", insumo=insumo_del)

@supplies_bp.route("/api/<int:insumo_id>/units", methods=['GET'])
@login_required
@roles_required('admin')
def api_insumo_units(insumo_id: int):
    insumo = db.session.query(Insumo).filter_by(id=insumo_id, is_active=True).first()
    if not insumo:
        return jsonify({"error": "Insumo no encontrado"}), 404
    
    unidades = []
    if insumo.unidad_base:
        unidades.append({
            "id": insumo.unidad_base.id,
            "nombre": insumo.unidad_base.nombre,
            "abreviatura": insumo.unidad_base.abreviatura,
            "es_base": True
        })
        
    for conv in insumo.conversiones:
        if conv.is_active and conv.unidad_destino:
            unidades.append({
                "id": conv.unidad_destino.id,
                "nombre": conv.unidad_destino.nombre,
                "abreviatura": conv.unidad_destino.abreviatura,
                "es_base": False,
                "factor_conversion": conv.factor_conversion
            })
            
    return jsonify({"insumo_id": insumo_id, "unidades": unidades})
