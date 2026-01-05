// ==========================================
// SISTEMA DE NOTIFICAÇÕES & TOASTS
// ==========================================

let unreadCount = 0;
// Armazena os IDs das notificações já exibidas para evitar duplicatas visuais
let displayedNotificationIds = new Set(); 

document.addEventListener('DOMContentLoaded', function() {
    // 1. Garante que o container de Toasts exista no DOM
    if (!document.getElementById('toast-container')) {
        const toastHTML = `<div id="toast-container"></div>`;
        document.body.insertAdjacentHTML('beforeend', toastHTML);
    }

    // 2. Inicia o monitoramento de notificações
    startNotificationPolling();
});

/**
 * Inicia o ciclo de verificação (Polling)
 */
function startNotificationPolling() {
    checkNotifications(); // Verifica imediatamente
    setInterval(checkNotifications, 10000); // Verifica a cada 10 segundos
}

/**
 * Consulta a API em busca de novas notificações
 */
function checkNotifications() {
    fetch('/api/notifications/check/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => {
        if (res.status === 401 || res.status === 403) return null;
        return res.json();
    })
    .then(data => {
        if (data && data.notifications && data.notifications.length > 0) {
            let newItemsCount = 0;

            data.notifications.forEach(notif => {
                // VERIFICAÇÃO DE DUPLICIDADE:
                // Só processa se este ID ainda não estiver na lista local
                if (!displayedNotificationIds.has(notif.id)) {
                    
                    // Adiciona ao Set para não processar novamente no próximo polling
                    displayedNotificationIds.add(notif.id);
                    
                    // Mostra o Toast flutuante
                    showToast(notif.message, notif.type);
                    
                    // Adiciona ao Painel Lateral
                    addNotificationToPanel(notif);

                    newItemsCount++;
                }
            });

            // Atualiza o contador apenas se houver novos itens reais
            if (newItemsCount > 0) {
                updateBadge(newItemsCount);
            }
        }
    })
    .catch(() => {}); 
}

/**
 * Adiciona um card ao Painel Lateral
 */
function addNotificationToPanel(notif) {
    const list = document.getElementById('notif-list');
    const emptyState = list.querySelector('.empty-notif');
    
    if (emptyState) emptyState.remove();

    const icons = { success: '✔', error: '✖', warning: '⚠', info: 'ℹ' };
    
    const card = document.createElement('div');
    card.className = `notif-card ${notif.type}`;
    // Adiciona o ID ao elemento para referência futura se necessário
    card.dataset.id = notif.id; 
    
    card.innerHTML = `
        <div class="notif-icon">${icons[notif.type] || 'ℹ'}</div>
        <div class="notif-content">
            <span class="notif-message">${notif.message}</span>
            <span class="notif-time">${notif.timestamp}</span>
        </div>
    `;
    
    list.prepend(card);
}

/**
 * Atualiza o contador vermelho (Badge) no sino
 */
function updateBadge(newCount) {
    unreadCount += newCount; // Soma aos que já existem
    const badge = document.getElementById('notif-badge');
    const headerCount = document.getElementById('header-count');
    
    if (badge) {
        badge.innerText = unreadCount > 99 ? '99+' : unreadCount;
        badge.classList.add('active');
    }
    if (headerCount) {
        headerCount.innerText = `${unreadCount} novas`;
    }
}

/**
 * Abre/Fecha o painel
 */
function toggleNotificationPanel() {
    const panel = document.getElementById('notification-panel');
    const badge = document.getElementById('notif-badge');
    
    if (panel.classList.contains('active')) {
        panel.classList.remove('active');
    } else {
        panel.classList.add('active');
    }
}

/**
 * AÇÃO DO LIXO: Limpa Frontend E avisa Backend
 */
function clearAllNotifications() {
    const list = document.getElementById('notif-list');
    
    // 1. Limpeza Visual (Frontend)
    list.innerHTML = `
        <div class="empty-notif">
            <span class="empty-icon">🗑</span>
            <p>Histórico limpo.</p>
        </div>`;
    
    unreadCount = 0;
    updateBadge(0);
    
    // Limpa nosso controle de duplicatas para permitir novas notificações futuras
    displayedNotificationIds.clear();

    // 2. Avisa o Backend que foi lido (POST Request)
    // Você precisará criar esta rota no Django: path('api/notifications/mark-read-all/', ...)
    fetch('/api/notifications/mark-read-all/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Importante para POST no Django
        }
    })
    .then(response => {
        if (response.ok) {
            unreadCount = 0;
        }
    })
    .catch(err => console.error("Erro ao notificar servidor:", err));
}

/**
 * Exibe notificação flutuante (Toast)
 */
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = { success: '✔', error: '✖', warning: '⚠', info: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || 'ℹ'}</div>
        <div class="toast-content">
            <span class="toast-message">${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hiding');
        toast.addEventListener('transitionend', () => toast.remove());
    }, 5000);
}

// Função auxiliar para pegar o CSRF Token do Django (Necessário para o POST do Clear)
function getCookie(name) {
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