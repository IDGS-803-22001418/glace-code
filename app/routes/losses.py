from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required # type: ignore
from app.decorators import roles_required
from sqlalchemy import or_, cast, String
from app import db
from app.models import Merma, Insumo

losses_bp = Blueprint('losses', __name__)

@losses_bp.route('/')
@login_required
@roles_required('chef')
def index():
    page = request.args.get('page', 1, type=int)
    query_param = request.args.get('q', '').strip()
    
    base_query = Merma.query.join(Insumo).filter(Merma.is_active == True)
    
    if query_param:
        # Creamos el filtro de búsqueda
        search_filter = or_(
            Insumo.nombre_insumo.ilike(f'%{query_param}%'),
            Merma.causa.ilike(f'%{query_param}%'),
            # Convertimos la fecha a string genérico para evitar errores entre SQLite y MySQL
            cast(Merma.fecha_registro, String).ilike(f'%{query_param}%')
        )
        base_query = base_query.filter(search_filter)
    
    mermas_obj = base_query.order_by(Merma.fecha_registro.desc()).paginate(
        page=page, per_page=8, error_out=False
    )
    
    return render_template('internal/losses/Mermas.html', mermas_obj=mermas_obj)

@losses_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@roles_required('chef')
def nueva_merma():
    if request.method == 'POST':
        insumo_id = request.form.get('insumo_id')
        cantidad = float(request.form.get('cantidad_perdida'))
        causa = request.form.get('causa')
        notas = request.form.get('notas_adicionales')

        try:
            nueva = Merma(
                insumo_id=insumo_id,
                cantidad_perdida=cantidad,
                causa=causa,
                notas_adicionales=notas
            )

            insumo = Insumo.query.get(insumo_id)
            if insumo:
                if cantidad > insumo.stock_actual:
                    flash(f"No puedes mermar más unidades ({cantidad}) de las que hay disponibles ({insumo.stock_actual}).", "error")
                    return redirect(url_for('losses.nueva_merma'))

                insumo.stock_actual -= cantidad
                if insumo.stock_actual < 0:
                    insumo.stock_actual = 0 

            db.session.add(nueva)
            db.session.commit()
            flash("Merma registrada satisfactoriamente.", "success")
            return redirect(url_for('losses.index'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar merma: {e}")
            flash(f"Error al registrar merma: {e}", "error")
            return redirect(url_for('losses.nueva_merma'))

    insumos = Insumo.query.all()
    return render_template('internal/losses/Registrar.html', insumos=insumos)

@losses_bp.route('/modificar/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('chef')
def modificar_merma(id):
    merma_actual = Merma.query.filter_by(id=id, is_active=True).first_or_404()
    insumos = Insumo.query.all()
    
    if request.method == 'POST':
        try:
            # 1. Recuperar info antigua para revertir stock
            insumo_anterior = Insumo.query.get(merma_actual.insumo_id)
            cantidad_anterior = merma_actual.cantidad_perdida
            
            # 2. Obtener info nueva
            nuevo_insumo_id = int(request.form.get('insumo_id'))
            nueva_cantidad = float(request.form.get('cantidad_perdida'))

            # 3. Revertir stock del insumo original
            if insumo_anterior:
                insumo_anterior.stock_actual += cantidad_anterior

            # 4. Actualizar datos de la merma
            merma_actual.insumo_id = nuevo_insumo_id
            merma_actual.cantidad_perdida = nueva_cantidad
            merma_actual.causa = request.form.get('causa')
            merma_actual.notas_adicionales = request.form.get('notas_adicionales')

            # 5. Aplicar resta al (posiblemente nuevo) insumo
            insumo_nuevo = Insumo.query.get(nuevo_insumo_id)
            if insumo_nuevo:
                if nueva_cantidad > insumo_nuevo.stock_actual:
                    db.session.rollback()
                    flash(f"No puedes mermar más unidades ({nueva_cantidad}) de las que hay disponibles ({insumo_nuevo.stock_actual}) para este insumo.", "error")
                    return redirect(url_for('losses.modificar_merma', id=merma_actual.id))

                insumo_nuevo.stock_actual -= nueva_cantidad
                if insumo_nuevo.stock_actual < 0:
                    insumo_nuevo.stock_actual = 0

            db.session.commit()
            flash("Merma actualizada correctamente.", "success")
            return redirect(url_for('losses.index'))
        except Exception as e:
            db.session.rollback()
            print(f"Error al modificar: {e}")
            flash(f"Error al modificar: {e}", "error")

    return render_template('internal/losses/Modificar.html', merma=merma_actual, insumos=insumos)

@losses_bp.route('/eliminar/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('chef')
def eliminar_merma(id):
    # Buscamos la merma que se desea eliminar
    merma_a_eliminar = Merma.query.filter_by(id=id, is_active=True).first_or_404()
    
    # SI EL MÉTODO ES POST: El usuario confirmó la eliminación desde el formulario
    if request.method == 'POST':
        try:
            # 1. Recuperar el stock en el inventario de Insumos
            insumo = Insumo.query.get(merma_a_eliminar.insumo_id)
            if insumo:
                insumo.stock_actual += merma_a_eliminar.cantidad_perdida
            
            # 2. Eliminación suave (soft-delete)
            merma_a_eliminar.is_active = False
            db.session.commit()
            
            flash("Merma eliminada y stock restituido.", "success")
            # Redirigir a la lista principal tras el éxito
            return redirect(url_for('losses.index'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar la merma: {e}")
            flash(f"Error al eliminar la merma: {e}", "error")
            return redirect(url_for('losses.index'))

    # SI EL MÉTODO ES GET: Mostramos la página de confirmación (el HTML que ya tienes)
    return render_template('internal/losses/Eliminar.html', merma=merma_a_eliminar)