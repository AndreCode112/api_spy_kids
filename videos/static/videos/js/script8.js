/**
 * Monitoramento de Novos Vídeos em Tempo Real
 */

let pollingInterval = null;
const CHECK_DELAY_MS = 10000; // Verifica a cada 10 segundos

// Inicia o monitoramento quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    startVideoPolling();
});

function startVideoPolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    pollingInterval = setInterval(checkForNewVideos, CHECK_DELAY_MS);
}

async function checkForNewVideos() {
    // 1. Descobrir qual o vídeo mais recente na tela atual
    // Estamos procurando o atributo data-video-id do primeiro card
    const firstVideoCard = document.querySelector('.video-card');
    const currentLatestId = firstVideoCard ? parseInt(firstVideoCard.dataset.videoId) : 0;

    // Preservar os filtros atuais da URL (datas, paginação, busca)
    const currentParams = new URLSearchParams(window.location.search);
    
    // Adicionar flag para checagem leve
    const checkParams = new URLSearchParams(currentParams);
    checkParams.set('check_update', 'true');

    try {
        // 2. Consultar o servidor (Check Leve)
        const response = await fetch(`${window.location.pathname}?${checkParams.toString()}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            const data = await response.json();
            const serverLatestId = data.latest_id;

            if (serverLatestId > currentLatestId) {
                await refreshVideoList(currentParams);
            }
        }
    } catch (error) {
        console.error("Erro ao verificar novos vídeos:", error);
    }
}

async function refreshVideoList(currentParams) {
    const container = document.getElementById('video-list-container');
    
    try {
        const response = await fetch(`${window.location.pathname}?${currentParams.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (response.ok) {
            const html = await response.text();
            
            container.innerHTML = html;
            
            const scriptTag = document.getElementById('updated-video-json');
            if (scriptTag) {
                try {
                    const newVideoData = JSON.parse(scriptTag.textContent);
                    
                    updatePlaylistData(newVideoData, true); 
                    
                    console.log("Playlist atualizada com sucesso. Total:", allVideosData.length);
                } catch (e) {
                    console.error("Erro ao ler JSON dos novos vídeos:", e);
                }
            }
            
            showToast("Lista de vídeos atualizada!");
        }
    } catch (error) {
        console.error("Erro ao atualizar a lista:", error);
    }
}

function showToast(message) {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.cssText = `
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 12px 24px;
        margin-top: 10px;
        border-radius: 8px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.1);
        animation: fadeIn 0.3s ease-out;
        font-family: sans-serif;
    `;
    toast.innerText = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

const style = document.createElement('style');
style.innerHTML = `
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
`;
document.head.appendChild(style);