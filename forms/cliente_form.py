from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp


class ClienteForm(FlaskForm):
    """
    Formulario para el registro y edición de clientes.
    Incluye validación de longitud de identificación, formato de correo y datos requeridos.
    """
    ruc = StringField(
        'Cédula / RUC',
        validators=[
            DataRequired(message='La cédula o RUC es obligatorio.'),
            Length(min=10, max=13, message='El documento debe contener entre 10 (cédula) y 13 (RUC) dígitos.'),
            Regexp(r'^\d+$', message='La identificación solo debe contener dígitos numéricos.')
        ],
        render_kw={'placeholder': 'Ej. 1723456789 o 1712345678001', 'autocomplete': 'off'}
    )

    nombre = StringField(
        'Nombre Completo / Razón Social',
        validators=[
            DataRequired(message='El nombre del cliente es obligatorio.'),
            Length(min=3, max=100, message='El nombre debe contener entre 3 y 100 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. Constructora Pastaza S.A.', 'autocomplete': 'off'}
    )

    tipo = SelectField(
        'Tipo de Cliente',
        choices=[
            ('', '-- Seleccione el tipo de cliente --'),
            ('Frecuente', 'Cliente Frecuente'),
            ('Corporativo', 'Cliente Corporativo / Empresa'),
            ('Ocasion', 'Cliente de Ocasión'),
            ('Mayorista', 'Cliente Mayorista')
        ],
        validators=[
            DataRequired(message='Debe seleccionar un tipo de cliente.')
        ]
    )

    telefono = StringField(
        'Teléfono de Contacto',
        validators=[
            DataRequired(message='El teléfono de contacto es obligatorio.'),
            Length(min=7, max=15, message='El teléfono debe contener entre 7 y 15 dígitos.')
        ],
        render_kw={'placeholder': 'Ej. 0998765432 o 03-2884100', 'autocomplete': 'off'}
    )

    email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El correo electrónico es obligatorio.'),
            Email(message='Ingrese una dirección de correo electrónico con formato válido (ejemplo@dominio.com).')
        ],
        render_kw={'placeholder': 'Ej. contacto@constructora.com', 'type': 'email', 'autocomplete': 'off'}
    )

    direccion = StringField(
        'Dirección Domiciliaria / Fiscal',
        validators=[
            DataRequired(message='La dirección es obligatoria.'),
            Length(min=5, max=200, message='La dirección debe tener entre 5 y 200 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. Av. Alberto Zambrano y Ceslao Marín, Puyo', 'autocomplete': 'off'}
    )

    submit = SubmitField('Guardar Cliente')
