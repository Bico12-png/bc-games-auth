// Global variables
const API_BASE_URL = '/api';
let currentPage = 1;
let currentLogsPage = 1;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    loadStats();
    loadKeys();
    
    // Auto-refresh stats every 30 seconds
    setInterval(loadStats, 30000);
}

function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });
    
    // Search key input - only allow numbers
    const searchKeyInput = document.getElementById('searchKey');
    if (searchKeyInput) {
        searchKeyInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }
    
    // Modal close on outside click
    document.getElementById('keyModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
}

function switchTab(tabName) {
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
    
    // Load data for specific tabs
    if (tabName === 'keys') {
        loadKeys();
    } else if (tabName === 'logs') {
        loadLogs();
    }
}

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// Statistics Functions
async function loadStats() {
    try {
        const data = await apiRequest('/stats');
        updateStatsDisplay(data.stats);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateStatsDisplay(stats) {
    document.getElementById('totalKeys').textContent = stats.total_keys || 0;
    document.getElementById('activeKeys').textContent = stats.active_keys || 0;
    document.getElementById('usedKeys').textContent = stats.used_keys || 0;
}

// Key Management Functions
async function createKeys() {
    const quantity = parseInt(document.getElementById('quantity').value);
    const expirationDays = parseInt(document.getElementById('expirationDays').value);
    
    if (!quantity || quantity < 1 || quantity > 1000) {
        showToast('Quantidade deve ser entre 1 e 1000', 'error');
        return;
    }
    
    if (!expirationDays || expirationDays < 1 || expirationDays > 365) {
        showToast('Dias de expiração deve ser entre 1 e 365', 'error');
        return;
    }
    
    try {
        const data = await apiRequest('/keys', {
            method: 'POST',
            body: JSON.stringify({
                quantity: quantity,
                expiration_days: expirationDays
            })
        });
        
        showToast(data.message, 'success');
        
        // Show created keys in a modal
        showCreatedKeysModal(data.keys);
        
        // Refresh data
        loadStats();
        loadKeys();
        
        // Reset form
        document.getElementById('quantity').value = 1;
        document.getElementById('expirationDays').value = 30;
        
    } catch (error) {
        console.error('Error creating keys:', error);
    }
}

function showCreatedKeysModal(keys) {
    const modalBody = document.getElementById('keyModalBody');
    modalBody.innerHTML = `
        <h4>Chaves Criadas com Sucesso!</h4>
        <p>Total: ${keys.length} chave(s)</p>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <strong>Chaves:</strong><br>
            ${keys.map(key => `<code style="background: white; padding: 2px 6px; margin: 2px; border-radius: 4px; display: inline-block;">${key}</code>`).join('')}
        </div>
        <button class="btn btn-primary" onclick="closeModal()">Fechar</button>
    `;
    document.getElementById('keyModal').style.display = 'block';
}

async function searchKey() {
    const keyValue = document.getElementById('searchKey').value.trim();
    
    if (!keyValue || keyValue.length !== 8) {
        showToast('Digite uma chave válida de 8 dígitos', 'error');
        return;
    }
    
    try {
        const data = await apiRequest(`/keys/${keyValue}`);
        showKeyDetailsModal(data.key);
    } catch (error) {
        console.error('Error searching key:', error);
    }
}

function showKeyDetailsModal(key) {
    const modalBody = document.getElementById('keyModalBody');
    modalBody.innerHTML = `
        <div class="key-details">
            <h4>Detalhes da Chave: ${key.key_value}</h4>
            <div class="detail-grid">
                <div class="detail-item">
                    <strong>Status:</strong>
                    <span class="status-badge status-${getStatusClass(key.status)}">${key.status}</span>
                </div>
                <div class="detail-item">
                    <strong>HWID:</strong>
                    <span>${key.hwid || 'Não definido'}</span>
                </div>
                <div class="detail-item">
                    <strong>Criada em:</strong>
                    <span>${formatDate(key.created_at)}</span>
                </div>
                <div class="detail-item">
                    <strong>Primeiro Login:</strong>
                    <span>${key.first_login_at ? formatDate(key.first_login_at) : 'Nunca'}</span>
                </div>
                <div class="detail-item">
                    <strong>Expira em:</strong>
                    <span>${key.expires_at ? formatDate(key.expires_at) : 'Não definido'}</span>
                </div>
                <div class="detail-item">
                    <strong>Total de Logins:</strong>
                    <span>${key.login_count}</span>
                </div>
                <div class="detail-item">
                    <strong>Dias de Expiração:</strong>
                    <span>${key.expiration_days} dias</span>
                </div>
            </div>
            <div class="modal-actions">
                ${key.is_paused ? 
                    `<button class="btn btn-success" onclick="unpauseKey('${key.key_value}')">Despausar</button>` :
                    `<button class="btn btn-warning" onclick="pauseKey('${key.key_value}')">Pausar</button>`
                }
                <button class="btn btn-secondary" onclick="resetHwid('${key.key_value}')">Resetar HWID</button>
                <button class="btn btn-danger" onclick="deleteKey('${key.key_value}')">Deletar</button>
                <button class="btn btn-primary" onclick="closeModal()">Fechar</button>
            </div>
        </div>
    `;
    document.getElementById('keyModal').style.display = 'block';
}

async function loadKeys(page = 1) {
    try {
        const data = await apiRequest(`/keys?page=${page}&per_page=20`);
        displayKeys(data.keys);
        displayKeysPagination(data.current_page, data.pages);
        currentPage = data.current_page;
    } catch (error) {
        console.error('Error loading keys:', error);
    }
}

function displayKeys(keys) {
    const tbody = document.getElementById('keysTableBody');
    
    if (keys.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">Nenhuma chave encontrada</td></tr>';
        return;
    }
    
    tbody.innerHTML = keys.map(key => `
        <tr>
            <td><code>${key.key_value}</code></td>
            <td><span class="status-badge status-${getStatusClass(key.status)}">${key.status}</span></td>
            <td>${key.hwid ? key.hwid.substring(0, 8) + '...' : '-'}</td>
            <td>${formatDate(key.created_at)}</td>
            <td>${key.first_login_at ? formatDate(key.first_login_at) : '-'}</td>
            <td>${key.expires_at ? formatDate(key.expires_at) : '-'}</td>
            <td>${key.login_count}</td>
            <td>
                <button class="action-btn btn-primary" onclick="showKeyDetailsModal(${JSON.stringify(key).replace(/"/g, '&quot;')})">
                    <i class="fas fa-eye"></i>
                </button>
                ${key.is_paused ? 
                    `<button class="action-btn btn-success" onclick="unpauseKey('${key.key_value}')">
                        <i class="fas fa-play"></i>
                    </button>` :
                    `<button class="action-btn btn-warning" onclick="pauseKey('${key.key_value}')">
                        <i class="fas fa-pause"></i>
                    </button>`
                }
                <button class="action-btn btn-secondary" onclick="resetHwid('${key.key_value}')">
                    <i class="fas fa-undo"></i>
                </button>
                <button class="action-btn btn-danger" onclick="deleteKey('${key.key_value}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function displayKeysPagination(currentPage, totalPages) {
    const pagination = document.getElementById('keysPagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Previous button
    if (currentPage > 1) {
        paginationHTML += `<button onclick="loadKeys(${currentPage - 1})">Anterior</button>`;
    }
    
    // Page numbers
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        paginationHTML += `<button class="${i === currentPage ? 'active' : ''}" onclick="loadKeys(${i})">${i}</button>`;
    }
    
    // Next button
    if (currentPage < totalPages) {
        paginationHTML += `<button onclick="loadKeys(${currentPage + 1})">Próximo</button>`;
    }
    
    pagination.innerHTML = paginationHTML;
}

function filterKeys() {
    const filter = document.getElementById('keyFilter').value.toLowerCase();
    const rows = document.querySelectorAll('#keysTableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
    });
}

// Key Actions
async function pauseKey(keyValue) {
    try {
        const data = await apiRequest(`/keys/${keyValue}/pause`, { method: 'POST' });
        showToast(data.message, 'success');
        loadKeys(currentPage);
        loadStats();
        closeModal();
    } catch (error) {
        console.error('Error pausing key:', error);
    }
}

async function unpauseKey(keyValue) {
    try {
        const data = await apiRequest(`/keys/${keyValue}/unpause`, { method: 'POST' });
        showToast(data.message, 'success');
        loadKeys(currentPage);
        loadStats();
        closeModal();
    } catch (error) {
        console.error('Error unpausing key:', error);
    }
}

async function resetHwid(keyValue) {
    if (!confirm(`Tem certeza que deseja resetar o HWID da chave ${keyValue}?`)) {
        return;
    }
    
    try {
        const data = await apiRequest(`/keys/${keyValue}/reset-hwid`, { method: 'POST' });
        showToast(data.message, 'success');
        loadKeys(currentPage);
        closeModal();
    } catch (error) {
        console.error('Error resetting HWID:', error);
    }
}

async function deleteKey(keyValue) {
    if (!confirm(`Tem certeza que deseja deletar a chave ${keyValue}? Esta ação não pode ser desfeita.`)) {
        return;
    }
    
    try {
        const data = await apiRequest(`/keys/${keyValue}`, { method: 'DELETE' });
        showToast(data.message, 'success');
        loadKeys(currentPage);
        loadStats();
        closeModal();
    } catch (error) {
        console.error('Error deleting key:', error);
    }
}

// Batch Actions
async function pauseAllKeys() {
    if (!confirm('Tem certeza que deseja pausar TODAS as chaves?')) {
        return;
    }
    
    try {
        const data = await apiRequest('/keys/pause-all', { method: 'POST' });
        showToast(data.message, 'success');
        loadKeys(currentPage);
        loadStats();
    } catch (error) {
        console.error('Error pausing all keys:', error);
    }
}

async function unpauseAllKeys() {
    if (!confirm('Tem certeza que deseja despausar TODAS as chaves?')) {
        return;
    }
    
    try {
        const data = await apiRequest('/keys/unpause-all', { method: 'POST' });
        showToast(data.message, 'success');
        loadKeys(currentPage);
        loadStats();
    } catch (error) {
        console.error('Error unpausing all keys:', error);
    }
}

async function deleteAllKeys() {
    if (!confirm('ATENÇÃO: Tem certeza que deseja deletar TODAS as chaves? Esta ação não pode ser desfeita!')) {
        return;
    }
    
    if (!confirm('Esta é sua última chance! Confirma a exclusão de TODAS as chaves?')) {
        return;
    }
    
    try {
        const data = await apiRequest('/keys', { method: 'DELETE' });
        showToast(data.message, 'success');
        loadKeys(currentPage);
        loadStats();
    } catch (error) {
        console.error('Error deleting all keys:', error);
    }
}

// Logs Functions
async function loadLogs(page = 1) {
    try {
        const data = await apiRequest(`/logs?page=${page}&per_page=20`);
        displayLogs(data.logs);
        displayLogsPagination(data.current_page, data.pages);
        currentLogsPage = data.current_page;
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

function displayLogs(logs) {
    const tbody = document.getElementById('logsTableBody');
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum log encontrado</td></tr>';
        return;
    }
    
    tbody.innerHTML = logs.map(log => `
        <tr>
            <td>${formatDate(log.timestamp)}</td>
            <td><code>${log.key_value || '-'}</code></td>
            <td><span class="action-badge">${log.action}</span></td>
            <td>${log.details || '-'}</td>
            <td>${log.ip_address || '-'}</td>
        </tr>
    `).join('');
}

function displayLogsPagination(currentPage, totalPages) {
    const pagination = document.getElementById('logsPagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Previous button
    if (currentPage > 1) {
        paginationHTML += `<button onclick="loadLogs(${currentPage - 1})">Anterior</button>`;
    }
    
    // Page numbers
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        paginationHTML += `<button class="${i === currentPage ? 'active' : ''}" onclick="loadLogs(${i})">${i}</button>`;
    }
    
    // Next button
    if (currentPage < totalPages) {
        paginationHTML += `<button onclick="loadLogs(${currentPage + 1})">Próximo</button>`;
    }
    
    pagination.innerHTML = paginationHTML;
}

// Utility Functions
function formatDate(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getStatusClass(status) {
    switch (status.toLowerCase()) {
        case 'em uso':
            return 'active';
        case 'não utilizada':
            return 'unused';
        case 'pausada':
            return 'paused';
        case 'expirada':
            return 'expired';
        default:
            return 'unused';
    }
}

function closeModal() {
    document.getElementById('keyModal').style.display = 'none';
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success':
            return 'check-circle';
        case 'error':
            return 'exclamation-circle';
        case 'warning':
            return 'exclamation-triangle';
        default:
            return 'info-circle';
    }
}

