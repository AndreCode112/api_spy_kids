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
