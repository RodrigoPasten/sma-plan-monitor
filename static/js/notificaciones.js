document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando notificaciones...');

    const notificacionesDropdown = document.getElementById('notificacionesDropdown');

    if (!notificacionesDropdown) {
        console.error('No se encontró el elemento notificacionesDropdown');
        return;
    }

    function actualizarContadorNotificaciones() {
        // Usar la URL exactamente como la probaste
        fetch('/api/v1/notificaciones/no-leidas/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log('Respuesta de API:', data);

                const cantidad = data.cantidad;

                // Buscar el badge existente dentro del dropdown
                let badge = notificacionesDropdown.querySelector('.badge');

                if (cantidad > 0) {
                    // Si el badge ya existe, solo actualiza el texto
                    if (badge) {
                        badge.textContent = cantidad;
                        badge.style.display = '';  // Asegura que sea visible
                    } else {
                        // Si no existe, crea uno nuevo
                        badge = document.createElement('span');
                        badge.className = 'badge bg-danger rounded-pill';
                        badge.textContent = cantidad;

                        // Inserta el badge después del ícono de campana
                        const bellIcon = notificacionesDropdown.querySelector('.bi-bell');
                        if (bellIcon) {
                            bellIcon.insertAdjacentElement('afterend', badge);
                        } else {
                            notificacionesDropdown.appendChild(badge);
                        }
                    }
                } else if (badge) {
                    // Si no hay notificaciones, oculta el badge
                    badge.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error al obtener notificaciones:', error);
            });
    }

    // Ejecutar inmediatamente
    actualizarContadorNotificaciones();

    // Actualizar cada 30 segundos
    setInterval(actualizarContadorNotificaciones, 30000);
});