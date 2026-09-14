from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class ProveedorForm(FlaskForm):
    """
    Formulario para el registro y edición de proveedores de materiales.
    """
    ruc = StringField(
        'RUC del Proveedor',
        validators=[
            DataRequired(message='El RUC del proveedor es obligatorio.'),
            Length(min=10, max=13, message='El RUC debe contener entre 10 y 13 dígitos.'),
            Regexp(r'^\d+$', message='El RUC solo debe contener caracteres numéricos.')
        ],
        render_kw={'placeholder': 'Ej. 1790012345001', 'autocomplete': 'off'}
    )

    empresa = StringField(
        'Razón Social / Nombre Comercial',
        validators=[
            DataRequired(message='La razón social de la empresa es obligatoria.'),
            Length(min=3, max=100, message='El nombre de la empresa debe tener entre 3 y 100 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. Holcim Ecuador S.A.', 'autocomplete': 'off'}
    )

    categoria = SelectField(
        'Línea de Suministro',
        choices=[
            ('', '-- Seleccione una categoría de suministro --'),
            ('Cementos y Hormigon', 'Cementos y Hormigón'),
            ('Acero y Varillas', 'Acero y Varillas'),
            ('Agregados y Grava', 'Agregados y Grava'),
            ('Carpinteria y Tablas', 'Carpintería y Tablas'),
            ('Mamposteria y Bloques', 'Mampostería y Bloques'),
            ('Pinturas y Acabados', 'Pinturas y Acabados'),
            ('Herramientas y Ferreteria', 'Herramientas y Ferretería General')
        ],
        validators=[
            DataRequired(message='Debe seleccionar una línea de suministro.')
        ]
    )

    contacto = StringField(
        'Contacto Principal / Asesor Comercial',
        validators=[
            DataRequired(message='El nombre del contacto principal es obligatorio.'),
            Length(min=3, max=100, message='El nombre del contacto debe tener entre 3 y 100 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. Ing. Ricardo Gómez', 'autocomplete': 'off'}
    )

    telefono = StringField(
        'Teléfono Corporativo',
        validators=[
            DataRequired(message='El teléfono corporativo es obligatorio.'),
            Length(min=7, max=15, message='El teléfono debe tener entre 7 y 15 dígitos.')
        ],
        render_kw={'placeholder': 'Ej. 02-2987654 o 0991234567', 'autocomplete': 'off'}
    )

    ciudad = StringField(
        'Ciudad Principal de Distribución',
        validators=[
            DataRequired(message='La ciudad es obligatoria.'),
            Length(min=3, max=50, message='La ciudad debe tener entre 3 y 50 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. Guayaquil, Quito o Puyo', 'autocomplete': 'off'}
    )

    activo = BooleanField(
        'Convenio Comercial Vigente / Activo',
        default=True
    )

    submit = SubmitField('Guardar Proveedor')
