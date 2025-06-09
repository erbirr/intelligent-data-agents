// Configuración Global
const API_BASE_URL = window.location.origin;
let currentResults = null;
let currentMetadata = null;

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Función principal de inicialización
async function initializeApp() {
    console.log('Inicializando aplicación MCP...');
    
    // Verificar estado del sistema
    await checkSystemStatus();
    
    // Cargar estado de agentes
    await refreshAgentsStatus();
    
    // Configurar event listeners
    setupEventListeners();
    
    console.log('Aplicación MCP inicializada correctamente');
}

// Configurar event listeners
function setupEventListeners() {
    // Formularios de conexión
    document.getElementById('neo4jForm').addEventListener('submit', (e) => {
        e.preventDefault();
        testConnection('neo4j');
    });
    
    document.getElementById('postgresForm').addEventListener('submit', (e) => {
        e.preventDefault();
        testConnection('postgres');
    });
    
    // Enter en el textarea de consulta
    document.getElementById('queryInput').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            executeQuery();
        }
    });
    
    // Cerrar modal con Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
    
    // Actualizar estado cada 30 segundos
    setInterval(checkSystemStatus, 30000);
}

// Verificar estado del sistema
async function checkSystemStatus() {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    if (!statusIndicator || !statusText) {
        console.warn('Elementos de estado del sistema no encontrados');
        return;
    }
    
    try {
        statusIndicator.className = 'status-indicator checking';
        statusText.textContent = 'Verificando...';
        
        const response = await fetch(`${API_BASE_URL}/health`);
        
        if (response.ok) {
            const data = await response.json();
            statusIndicator.className = 'status-indicator online';
            statusText.textContent = `Sistema Activo - v${data.version}`;
        } else {
            throw new Error('Sistema no disponible');
        }
    } catch (error) {
        console.error('Error verificando estado del sistema:', error);
        if (statusIndicator && statusText) {
            statusIndicator.className = 'status-indicator offline';
            statusText.textContent = 'Sistema Desconectado';
        }
    }
}

// Probar conexión a base de datos
async function testConnection(dbType) {
    console.log(`Iniciando test de conexión para ${dbType}`);
    
    const button = document.querySelector(`#${dbType}Form .btn-test`);
    const spinner = button?.querySelector('.loading-spinner');
    const text = button?.querySelector('span');
    const status = document.getElementById(`${dbType}Status`);
    
    if (!button || !status) {
        console.error('Elementos del formulario no encontrados');
        return;
    }
    
    // Obtener datos del formulario
    const formData = getFormData(dbType);
    if (!formData) return;
    
    console.log('Datos del formulario:', formData);
    
    try {
        // Mostrar estado de carga
        button.disabled = true;
        if (spinner) spinner.style.display = 'block';
        if (text) text.textContent = 'Probando...';
        status.className = 'connection-status testing';
        status.innerHTML = '<i class="fas fa-circle"></i><span>Probando...</span>';
        
        const url = `${API_BASE_URL}/connections/${dbType}/test`;
        console.log('Enviando request a:', url);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        console.log('Respuesta recibida:', response.status, response.statusText);
        
        const result = await response.json();
        console.log('Resultado del test:', result);
        
        if (result.success) {
            status.className = 'connection-status connected';
            status.innerHTML = '<i class="fas fa-circle"></i><span>Conectado</span>';
            
            console.log('Mostrando notificación de éxito');
            showNotification('success', 'Conexión Exitosa', result.message, result.details);
        } else {
            status.className = 'connection-status disconnected';
            status.innerHTML = '<i class="fas fa-circle"></i><span>Error</span>';
            
            console.log('Mostrando notificación de error');
            showNotification('error', 'Error de Conexión', result.message);
        }
        
    } catch (error) {
        console.error(`Error testing ${dbType} connection:`, error);
        status.className = 'connection-status disconnected';
        status.innerHTML = '<i class="fas fa-circle"></i><span>Error</span>';
        
        showNotification('error', 'Error de Red', `No se pudo conectar al servidor: ${error.message}`);
    } finally {
        // Restaurar estado del botón
        button.disabled = false;
        spinner.style.display = 'none';
        text.textContent = 'Probar Conexión';
    }
}

// Obtener datos del formulario
function getFormData(dbType) {
    const form = document.getElementById(`${dbType}Form`);
    const formData = {};
    
    if (dbType === 'neo4j') {
        formData.uri = form.uri.value.trim();
        formData.user = form.user.value.trim();
        formData.password = form.password.value;
        formData.database = form.database.value.trim() || 'neo4j';
        
        if (!formData.uri || !formData.user || !formData.password) {
            showNotification('warning', 'Campos Requeridos', 'Por favor complete todos los campos obligatorios');
            return null;
        }
    } else if (dbType === 'postgres') {
        formData.host = form.host.value.trim();
        formData.port = parseInt(form.port.value) || 5432;
        formData.database = form.database.value.trim();
        formData.user = form.user.value.trim();
        formData.password = form.password.value;
        
        if (!formData.host || !formData.database || !formData.user || !formData.password) {
            showNotification('warning', 'Campos Requeridos', 'Por favor complete todos los campos obligatorios');
            return null;
        }
    }
    
    return formData;
}

// Ejecutar consulta
async function executeQuery() {
    const queryInput = document.getElementById('queryInput');
    const executeBtn = document.getElementById('executeQueryBtn');
    const spinner = executeBtn.querySelector('.loading-spinner');
    const text = executeBtn.querySelector('span');
    const resultsPanel = document.getElementById('resultsPanel');
    
    const query = queryInput.value.trim();
    if (!query) {
        showNotification('warning', 'Consulta Vacía', 'Por favor ingrese una consulta');
        return;
    }
    
    try {
        // Mostrar estado de carga
        executeBtn.disabled = true;
        spinner.style.display = 'block';
        text.textContent = 'Procesando...';
        
        // Preparar request
        const requestData = {
            query: query,
            context: null
        };
        
        // Agregar configuraciones personalizadas si están marcadas
        if (document.getElementById('useCustomNeo4j').checked) {
            const neo4jConfig = getFormData('neo4j');
            if (neo4jConfig) {
                requestData.neo4j_config = neo4jConfig;
            }
        }
        
        if (document.getElementById('useCustomPostgres').checked) {
            const postgresConfig = getFormData('postgres');
            if (postgresConfig) {
                requestData.postgres_config = postgresConfig;
            }
        }
        
        const startTime = Date.now();
        
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const endTime = Date.now();
        const actualExecutionTime = (endTime - startTime) / 1000;
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error en la consulta');
        }
        
        const result = await response.json();
        
        // Guardar resultados globalmente
        currentResults = result.result;
        currentMetadata = result.metadata;
        
        // Mostrar resultados
        displayResults(result, actualExecutionTime);
        resultsPanel.style.display = 'block';
        
        // Scroll to results
        resultsPanel.scrollIntoView({ behavior: 'smooth' });
        
        showNotification('success', 'Consulta Ejecutada', 'Resultados obtenidos correctamente');
        
    } catch (error) {
        console.error('Error executing query:', error);
        showNotification('error', 'Error en la Consulta', error.message);
    } finally {
        // Restaurar estado del botón
        executeBtn.disabled = false;
        spinner.style.display = 'none';
        text.textContent = 'Ejecutar Consulta';
    }
}

// Mostrar resultados
function displayResults(result, executionTime) {
    // Actualizar información de ejecución
    document.getElementById('executionTime').textContent = `Tiempo: ${result.execution_time?.toFixed(3) || executionTime.toFixed(3)}s`;
    document.getElementById('agentUsed').textContent = `Agente: ${result.metadata?.agent || 'Orquestador'}`;
    
    // Mostrar en tabla
    displayTableResults(result.result);
    
    // Mostrar JSON
    displayJsonResults(result);
    
    // Mostrar metadatos
    displayMetadata(result.metadata);
}

// Mostrar resultados en tabla
function displayTableResults(data) {
    const table = document.getElementById('resultsTable');
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    
    // Limpiar tabla
    thead.innerHTML = '';
    tbody.innerHTML = '';
    
    if (!data || (Array.isArray(data) && data.length === 0)) {
        tbody.innerHTML = '<tr><td colspan="100%" class="empty-state">No hay datos para mostrar</td></tr>';
        return;
    }
    
    if (Array.isArray(data) && data.length > 0) {
        // Crear encabezados basados en las claves del primer objeto
        const headers = Object.keys(data[0]);
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        
        // Crear filas de datos
        data.forEach(row => {
            const tr = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                const value = row[header];
                td.textContent = value !== null && value !== undefined ? value : '';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    } else if (typeof data === 'object') {
        // Objeto único - mostrar como clave-valor
        const headerRow = document.createElement('tr');
        ['Propiedad', 'Valor'].forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        
        Object.entries(data).forEach(([key, value]) => {
            const tr = document.createElement('tr');
            const keyTd = document.createElement('td');
            const valueTd = document.createElement('td');
            keyTd.textContent = key;
            valueTd.textContent = typeof value === 'object' ? JSON.stringify(value) : value;
            tr.appendChild(keyTd);
            tr.appendChild(valueTd);
            tbody.appendChild(tr);
        });
    } else {
        // Valor simple
        const headerRow = document.createElement('tr');
        const th = document.createElement('th');
        th.textContent = 'Resultado';
        headerRow.appendChild(th);
        thead.appendChild(headerRow);
        
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.textContent = data;
        tr.appendChild(td);
        tbody.appendChild(tr);
    }
}

// Mostrar JSON
function displayJsonResults(result) {
    const jsonViewer = document.getElementById('jsonResults');
    jsonViewer.textContent = JSON.stringify(result, null, 2);
}

// Mostrar metadatos
function displayMetadata(metadata) {
    const metadataViewer = document.getElementById('metadataResults');
    metadataViewer.innerHTML = '';
    
    if (!metadata) {
        metadataViewer.innerHTML = '<p class="empty-state">No hay metadatos disponibles</p>';
        return;
    }
    
    Object.entries(metadata).forEach(([key, value]) => {
        const item = document.createElement('div');
        item.className = 'metadata-item';
        item.innerHTML = `
            <span><strong>${key}:</strong></span>
            <span>${typeof value === 'object' ? JSON.stringify(value) : value}</span>
        `;
        metadataViewer.appendChild(item);
    });
}

// Cambiar tab de resultados
function switchTab(tabName, buttonElement = null) {
    // Ocultar todos los contenidos
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Desactivar todos los botones
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Mostrar contenido seleccionado
    document.getElementById(`${tabName}View`).classList.add('active');
    
    // Activar botón seleccionado
    if (buttonElement) {
        buttonElement.classList.add('active');
    } else {
        // Buscar el botón que corresponde al tab
        const tabButton = document.querySelector(`[onclick*="${tabName}"]`);
        if (tabButton) {
            tabButton.classList.add('active');
        }
    }
}

// Exportar resultados
function exportResults(format) {
    if (!currentResults) {
        showNotification('warning', 'Sin Datos', 'No hay resultados para exportar');
        return;
    }
    
    let content, filename, mimeType;
    
    if (format === 'json') {
        content = JSON.stringify({
            results: currentResults,
            metadata: currentMetadata,
            exported_at: new Date().toISOString()
        }, null, 2);
        filename = `mcp_results_${Date.now()}.json`;
        mimeType = 'application/json';
    } else if (format === 'csv') {
        content = convertToCSV(currentResults);
        filename = `mcp_results_${Date.now()}.csv`;
        mimeType = 'text/csv';
    }
    
    // Crear y descargar archivo
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('success', 'Exportación Exitosa', `Archivo ${filename} descargado`);
}

// Convertir a CSV
function convertToCSV(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return 'No hay datos para exportar';
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => 
            headers.map(header => {
                const value = row[header];
                // Escapar comillas y comas
                if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value;
            }).join(',')
        )
    ].join('\n');
    
    return csvContent;
}

// Limpiar resultados
function clearResults() {
    currentResults = null;
    currentMetadata = null;
    document.getElementById('resultsPanel').style.display = 'none';
    document.getElementById('queryInput').value = '';
    showNotification('success', 'Limpiado', 'Resultados eliminados');
}

// Actualizar estado de agentes
async function refreshAgentsStatus() {
    const agentsGrid = document.getElementById('agentsGrid');
    
    try {
        const response = await fetch(`${API_BASE_URL}/agents/status`);
        
        if (!response.ok) {
            throw new Error('No se pudo obtener el estado de los agentes');
        }
        
        const status = await response.json();
        
        agentsGrid.innerHTML = '';
        
        // Crear cards para cada agente
        Object.entries(status).forEach(([agentName, agentStatus]) => {
            if (agentName === 'error') return;
            
            const card = document.createElement('div');
            card.className = `agent-card ${agentStatus.connected ? 'connected' : 'disconnected'}`;
            
            card.innerHTML = `
                <div class="agent-header">
                    <span class="agent-name">${agentName.charAt(0).toUpperCase() + agentName.slice(1)}</span>
                    <span class="agent-status ${agentStatus.connected ? 'connected' : 'disconnected'}">
                        ${agentStatus.connected ? 'Conectado' : 'Desconectado'}
                    </span>
                </div>
                <div class="agent-details">
                    ${Object.entries(agentStatus).map(([key, value]) => {
                        if (key === 'connected') return '';
                        return `<div><strong>${key}:</strong> ${typeof value === 'object' ? JSON.stringify(value) : value}</div>`;
                    }).join('')}
                </div>
            `;
            
            agentsGrid.appendChild(card);
        });
        
        if (status.error) {
            agentsGrid.innerHTML = `<div class="empty-state">Error: ${status.error}</div>`;
        }
        
    } catch (error) {
        console.error('Error loading agents status:', error);
        agentsGrid.innerHTML = '<div class="empty-state">Error cargando estado de agentes</div>';
    }
}

// Establecer consulta de ejemplo
function setExampleQuery(query) {
    document.getElementById('queryInput').value = query;
    document.getElementById('queryInput').focus();
}

// Mostrar notificación/modal
function showNotification(type, title, message, details = null) {
    console.log('showNotification llamada con:', { type, title, message, details });
    
    const modal = document.getElementById('notificationModal');
    const modalIcon = document.getElementById('modalIcon');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalDetails = document.getElementById('modalDetails');
    
    if (!modal || !modalIcon || !modalTitle || !modalMessage || !modalDetails) {
        console.error('Elementos del modal no encontrados');
        return;
    }
    
    // Configurar icono según tipo
    let iconClass, iconSymbol;
    switch (type) {
        case 'success':
            iconClass = 'success';
            iconSymbol = '✓';
            break;
        case 'error':
            iconClass = 'error';
            iconSymbol = '✗';
            break;
        case 'warning':
            iconClass = 'warning';
            iconSymbol = '⚠';
            break;
        default:
            iconClass = '';
            iconSymbol = 'ℹ';
    }
    
    modalIcon.className = `modal-icon ${iconClass}`;
    modalIcon.textContent = iconSymbol;
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    
    // Mostrar detalles si están disponibles
    if (details) {
        modalDetails.style.display = 'block';
        modalDetails.textContent = typeof details === 'object' ? JSON.stringify(details, null, 2) : details;
    } else {
        modalDetails.style.display = 'none';
    }
    
    modal.style.display = 'block';
    
    // Auto-cerrar después de 5 segundos para mensajes de éxito
    if (type === 'success') {
        setTimeout(closeModal, 5000);
    }
}

// Cerrar modal
function closeModal() {
    document.getElementById('notificationModal').style.display = 'none';
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('notificationModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Utilidades adicionales
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Validación de formularios
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--danger-color)';
            isValid = false;
        } else {
            input.style.borderColor = 'var(--gray-300)';
        }
    });
    
    return isValid;
}

// Manejar errores de red
function handleNetworkError(error) {
    console.error('Network error:', error);
    showNotification('error', 'Error de Red', 'No se pudo conectar al servidor. Verifique su conexión.');
}

// Inicializar tooltips (si se necesitan)
function initializeTooltips() {
    // Implementar tooltips si es necesario
}

// Debug helper
function logApiCall(endpoint, method, data = null) {
    console.group(`API Call: ${method} ${endpoint}`);
    if (data) {
        console.log('Request data:', data);
    }
    console.groupEnd();
}

// Verificar compatibilidad del navegador
function checkBrowserCompatibility() {
    if (!window.fetch) {
        showNotification('error', 'Navegador No Compatible', 'Su navegador no soporta las características requeridas. Por favor actualice su navegador.');
        return false;
    }
    return true;
}

// Inicializar verificación de compatibilidad
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkBrowserCompatibility);
} else {
    checkBrowserCompatibility();
}
