let pollingInterval = null;
const POLL_TIME_MS = 3000;

document.addEventListener('DOMContentLoaded', () => {
    startSmartPolling();
});

function startSmartPolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    pollingInterval = setInterval(checkAndLoadNewVideos, POLL_TIME_MS);
}

async function checkAndLoadNewVideos() {
    // 1. Descobrir qual o ID do vídeo mais recente que temos na memória
    // Assumindo que allVideosData está ordenado (novos primeiro) ou usamos reduce
    let lastKnownId = 0;
    
    // Tenta pegar da variável global se existir e tiver dados
    if (typeof allVideosData !== 'undefined' && allVideosData.length > 0) {
        // Encontra o maior ID na lista atual
        lastKnownId = Math.max(...allVideosData.map(v => v.id));
    } else {
        // Fallback: tenta pegar do atributo data-video-id do primeiro card no HTML
        const firstCard = document.querySelector('.video-card');
        if (firstCard) lastKnownId = parseInt(firstCard.dataset.videoId);
    }
    const params = new URLSearchParams(window.location.search);
    params.set('mode', 'update');
    params.set('last_id', lastKnownId); // Envia o ID pro Python decidir se processa

    try {
        const response = await fetch(`${window.location.pathname}?${params.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (response.ok) {
            const serverData = await response.json();

            // 3. Verifica o status retornado pelo Python
            if (serverData.status === 'updated') {
                console.log("Novos vídeos encontrados! Atualizando...");

                // A. Atualiza o Visual (HTML)
                const container = document.getElementById('video-list-container');
                if (container) {
                    container.innerHTML = serverData.html;
                    
                    // Pequeno efeito visual de "flash" para indicar atualização (opcional)
                    container.style.opacity = '0.5';
                    setTimeout(() => container.style.opacity = '1', 300);
                }

                // B. Atualiza os Dados do Player (CRUCIAL PARA O PLAY FUNCIONAR)
                if (typeof updatePlaylistData === 'function') {
                    // Passamos 'true' para substituir a lista antiga pela nova lista completa da página 1
                    updatePlaylistData(serverData.data, true);
                }
                
                // Notificação
                if (typeof showToast === 'function') {
                    showToast("Novos vídeos carregados!");
                }
            } else {
                console.log("Sistema atualizado. Nenhum vídeo novo.");
            }
        }
    } catch (e) {
        console.error("Erro no polling de vídeos:", e);
    }
}
<<<<<<< HEAD

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
=======
>>>>>>> unstable
