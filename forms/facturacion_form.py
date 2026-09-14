from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class FacturacionForm(FlaskForm):
    """
    Formulario para la emisión y edición de comprobantes de facturación.
    """
    numero = StringField(
        'Número de Comprobante / Factura',
        validators=[
            DataRequired(message='El número de comprobante es obligatorio.'),
            Length(min=5, max=20, message='El número de factura debe contener entre 5 y 20 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. FAC-00105', 'autocomplete': 'off'}
    )

    fecha = DateField(
        'Fecha de Emisión',
        format='%Y-%m-%d',
        validators=[
            DataRequired(message='Debe ingresar una fecha de emisión válida (AAAA-MM-DD).')
        ],
        render_kw={'type': 'date'}
    )

    cliente = StringField(
        'Nombre del Cliente / Razón Social',
        validators=[
            DataRequired(message='El nombre del cliente destinatario es obligatorio.'),
            Length(min=3, max=100, message='El nombre del cliente debe tener entre 3 y 100 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. Carlos Alberto Mendoza o Constructora Los Andes', 'autocomplete': 'off'}
    )

    subtotal = FloatField(
        'Subtotal ($ USD)',
        validators=[
            DataRequired(message='El subtotal es obligatorio.'),
            NumberRange(min=0.01, max=1000000.0, message='El subtotal debe ser un valor positivo mayor a $0.00.')
        ],
        render_kw={'placeholder': 'Ej. 250.00', 'step': '0.01', 'min': '0.01', 'id': 'subtotal-input'}
    )

    iva = FloatField(
        'IVA 15% ($ USD)',
        validators=[
            Optional(),
            NumberRange(min=0.0, max=1000000.0, message='El valor del IVA no puede ser negativo.')
        ],
        render_kw={'placeholder': 'Calculado automáticamente (15%)', 'step': '0.01', 'id': 'iva-input'}
    )

    total = FloatField(
        'Total General ($ USD)',
        validators=[
            Optional(),
            NumberRange(min=0.01, max=1000000.0, message='El total debe ser mayor a $0.00.')
        ],
        render_kw={'placeholder': 'Calculado automáticamente (Subtotal + IVA)', 'step': '0.01', 'id': 'total-input'}
    )

    estado = SelectField(
        'Estado de la Factura',
        choices=[
            ('', '-- Seleccione el estado --'),
            ('Pagada', 'Pagada (Efectivo / Transferencia)'),
            ('Pendiente', 'Pendiente de Cobro'),
            ('Anulada', 'Anulada')
        ],
        validators=[
            DataRequired(message='Debe seleccionar el estado de la factura.')
        ]
    )

    submit = SubmitField('Procesar Factura')
