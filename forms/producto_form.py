from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductoForm(FlaskForm):
    """
    Formulario para el registro y edición de productos en el inventario.
    Hereda de FlaskForm para soportar validación y protección CSRF.
    Incluye campo proveedor_ruc para la relación de clave foránea con Proveedores.
    """
    id = StringField(
        'Código del Producto',
        validators=[
            DataRequired(message='El código del producto es obligatorio.'),
            Length(min=3, max=20, message='El código debe contener entre 3 y 20 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. PROD-008', 'autocomplete': 'off'}
    )

    nombre = StringField(
        'Nombre del Material / Producto',
        validators=[
            DataRequired(message='El nombre del material es obligatorio.'),
            Length(min=3, max=100, message='El nombre debe contener entre 3 y 100 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. Cemento Portland Tipo I 50kg', 'autocomplete': 'off'}
    )

    categoria = SelectField(
        'Categoría',
        choices=[
            ('', '-- Seleccione una categoría --'),
            ('Estructural', 'Estructural'),
            ('Agregados', 'Agregados'),
            ('Acero', 'Acero'),
            ('Carpinteria', 'Carpintería'),
            ('Mamposteria', 'Mampostería'),
            ('Acabados', 'Acabados'),
            ('Herramientas', 'Herramientas')
        ],
        validators=[
            DataRequired(message='Debe seleccionar una categoría válida.')
        ]
    )

    unidad = SelectField(
        'Unidad de Medida',
        choices=[
            ('', '-- Seleccione una unidad --'),
            ('Saco', 'Saco'),
            ('Metro Cubico', 'Metro Cúbico'),
            ('Unidad', 'Unidad'),
            ('Pieza', 'Pieza'),
            ('Millar', 'Millar'),
            ('Caneca', 'Caneca'),
            ('Kilogramo', 'Kilogramo')
        ],
        validators=[
            DataRequired(message='Debe seleccionar una unidad de medida.')
        ]
    )

    stock = IntegerField(
        'Cantidad en Stock',
        validators=[
            DataRequired(message='El stock inicial es obligatorio.'),
            NumberRange(min=0, max=100000, message='El stock debe ser un valor entero no negativo (>= 0).')
        ],
        render_kw={'placeholder': 'Ej. 150', 'min': '0'}
    )

    precio = FloatField(
        'Precio Unitario ($ USD)',
        validators=[
            DataRequired(message='El precio unitario es obligatorio.'),
            NumberRange(min=0.01, max=100000.0, message='El precio debe ser un valor numérico mayor a $0.00.')
        ],
        render_kw={'placeholder': 'Ej. 12.50', 'step': '0.01', 'min': '0.01'}
    )

    proveedor_ruc = SelectField(
        'Proveedor Asignado (Relación Clave Foránea)',
        choices=[('', '-- Seleccione un proveedor aliado --')],
        validators=[Optional()]
    )

    submit = SubmitField('Guardar Producto')

