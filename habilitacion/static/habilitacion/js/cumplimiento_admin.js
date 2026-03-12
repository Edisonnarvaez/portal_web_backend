/**
 * Script para filtrado dinámico de servicios en formulario de Cumplimiento
 * Cuando el usuario selecciona una autoevaluación, actualiza automáticamente
 * el dropdown de servicios para mostrar solo los del prestador correcto.
 */

(function() {
    'use strict';

    // Elementos del DOM
    const autoevaluacionSelect = document.getElementById('id_autoevaluacion');
    const servicioSelect = document.getElementById('id_servicio_sede');

    // URL del endpoint que proporciona servicios filtrados
    const API_ENDPOINT = '/api/habilitacion/cumplimientos/servicios_de_autoevaluacion/';

    /**
     * Obtener CSRF token de la página
     */
    function getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Actualizar dropdown de servicios basado en autoevaluación seleccionada
     */
    async function actualizarServicios() {
        const autoevaluacionId = autoevaluacionSelect.value;

        // Si no hay autoevaluación seleccionada, mostrar todos los servicios
        if (!autoevaluacionId) {
            console.log('Sin autoevaluación seleccionada');
            servicioSelect.innerHTML = '<option value="">---------</option>';
            return;
        }

        try {
            console.log(`Obteniendo servicios para autoevaluación ID: ${autoevaluacionId}`);
            
            // Llamar al endpoint
            const url = `${API_ENDPOINT}?autoevaluacion_id=${autoevaluacionId}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });

            if (!response.ok) {
                console.error(`Error API: ${response.status} - ${response.statusText}`);
                mostrarError(`Error al obtener servicios: ${response.status}`);
                return;
            }

            const data = await response.json();
            console.log('Datos recibidos:', data);

            // Construir opciones del dropdown
            let html = '<option value="">---------</option>';
            
            if (data.servicios && data.servicios.length > 0) {
                data.servicios.forEach(servicio => {
                    html += `<option value="${servicio.id}">
                        ${servicio.codigo_servicio} - ${servicio.nombre_servicio} 
                        (${servicio.complejidad})
                    </option>`;
                });
                console.log(`Se cargaron ${data.servicios.length} servicios`);
            } else {
                html += '<option value="">No hay servicios disponibles</option>';
                console.warn('No hay servicios para este prestador');
            }

            // Actualizar dropdown
            servicioSelect.innerHTML = html;
            
            // Mostrar info del prestador (opcional pero útil)
            mostrarInfoPrestador(data.prestador);

        } catch (error) {
            console.error('Error al actualizar servicios:', error);
            mostrarError(`Error técnico: ${error.message}`);
        }
    }

    /**
     * Mostrar información del prestador (para feedback visual)
     */
    function mostrarInfoPrestador(prestador) {
        if (!prestador) return;
        
        console.log(`Prestador seleccionado: ${prestador.codigo_reps} - ${prestador.nombre}`);
        
        // Crear elemento para mostrar el prestador
        let infoPrestador = document.getElementById('info-prestador');
        if (!infoPrestador) {
            infoPrestador = document.createElement('div');
            infoPrestador.id = 'info-prestador';
            infoPrestador.style.cssText = `
                padding: 10px;
                margin: 10px 0;
                background-color: #d1ecf1;
                border: 1px solid #bee5eb;
                border-radius: 4px;
                color: #0c5460;
                font-size: 14px;
            `;
            autoevaluacionSelect.parentElement.appendChild(infoPrestador);
        }
        
        infoPrestador.innerHTML = `
            <strong>Prestador:</strong> ${prestador.codigo_reps} - ${prestador.nombre}
        `;
    }

    /**
     * Mostrar mensaje de error
     */
    function mostrarError(mensaje) {
        console.error(mensaje);
        
        let errorDiv = document.getElementById('error-servicios');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'error-servicios';
            servicioSelect.parentElement.appendChild(errorDiv);
        }
        
        errorDiv.innerHTML = `<p style="color: #dc3545;">${mensaje}</p>`;
        setTimeout(() => {
            errorDiv.innerHTML = '';
        }, 5000);
    }

    /**
     * Inicializar cuando el DOM esté listo
     */
    function inicializar() {
        console.log('Inicializando filtrado dinámico de cumplimientos...');
        
        if (!autoevaluacionSelect || !servicioSelect) {
            console.warn('No se encontraron los elementos del formulario de cumplimiento');
            return;
        }

        // Escuchar cambios en el select de autoevaluación
        autoevaluacionSelect.addEventListener('change', function() {
            console.log('Cambio detectado en autoevaluación');
            actualizarServicios();
        });

        // Si hay valor inicial, cargar servicios
        if (autoevaluacionSelect.value) {
            console.log('Autoevaluación pre-seleccionada, cargando servicios...');
            actualizarServicios();
        }

        console.log('Filtrado dinámico inicializado correctamente');
    }

    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }
})();
