from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DecimalField, validators


class InsumoForm(FlaskForm):
    id = IntegerField('id')
    nombre_insumo = StringField('Nombre del Insumo', [
        validators.DataRequired(message='Ingrese el nombre del insumo'),
        validators.Length(min=3, max=100, message='Nombre demasiado corto o largo')
    ])
    categoria = StringField('Categoría', [
        validators.DataRequired(message='La categoría es requerida')
    ])
    # Usamos DecimalField para manejar pesos y volúmenes con precisión
    stock_actual = DecimalField('Stock Actual', [
        validators.NumberRange(min=0, message='El stock no puede ser negativo')
    ], default=0)
    
    stock_minimo_alerta = DecimalField('Stock Mínimo (Alerta)', [
        validators.NumberRange(min=0, message='La alerta debe ser un número positivo')
    ], default=0)
    
    # Este campo se llenará dinámicamente desde la base de datos en la ruta
    unidad_base_id = SelectField('Unidad de Medida', coerce=int, validators=[
        validators.DataRequired(message='Seleccione una unidad de medida')
    ])
