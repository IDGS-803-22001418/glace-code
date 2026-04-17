import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user  # type: ignore
from app.decorators import roles_required
from app.mongo import mongo
from app import user_logger

configuration_bp = Blueprint('configuration', __name__)

@configuration_bp.route('/', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def index():
    db = mongo.db
    config_collection = db['configuration'] if db is not None else None
    
    if request.method == 'POST':
        razon_social = request.form.get('razon_social')
        rfc = request.form.get('rfc')
        direccion_fiscal = request.form.get('direccion_fiscal')
        telefono_contacto = request.form.get('telefono_contacto')
        
        if 'logotipo' in request.files:
            file = request.files['logotipo']
            if file and file.filename:
                # Save as app/static/images/icon.png
                filepath = os.path.join(current_app.root_path, 'static', 'images', 'icon.png')
                file.save(filepath)
                
        if config_collection is not None:
            config_data = {
                'razon_social': razon_social,
                'rfc': rfc,
                'direccion_fiscal': direccion_fiscal,
                'telefono_contacto': telefono_contacto
            }
            config_collection.update_one(
                {'_id': 'main_config'},
                {'$set': config_data},
                upsert=True
            )
            user_logger.log_action(
                current_user,
                module="Configuración",
                action=f"Se actualizó la configuración",
                success=True,
            )
            flash('Configuración guardada correctamente.', 'success')
        else:
            user_logger.log_action(
                current_user,
                module="Configuración",
                action=f"Error al actualizar la configuración",
                success=False,
            )
            flash('Error: No se pudo conectar a la base de datos.', 'error')
            
        return redirect(url_for('configuration.index'))
        
    config = {}
    if config_collection is not None:
        config = config_collection.find_one({'_id': 'main_config'}) or {}
        
    return render_template('internal/configuration/index.html', config=config)