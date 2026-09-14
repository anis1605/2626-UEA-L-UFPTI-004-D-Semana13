// Script interactivo para Ferretería El Constructor - Semana 11

document.addEventListener('DOMContentLoaded', function () {
    console.log('Ferretería El Constructor - Módulo de Formularios Flask-WTF cargado con éxito.');

    // Auto-cierre de alertas flash después de 5 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Inicialización de Tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
