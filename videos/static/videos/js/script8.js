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
    let lastKnownId = 0;
    
    if (typeof allVideosData !== 'undefined' && allVideosData.length > 0) {
        lastKnownId = Math.max(...allVideosData.map(v => v.id));
    } else {
        const firstCard = document.querySelector('.video-card');
        if (firstCard) lastKnownId = parseInt(firstCard.dataset.videoId);
    }
    const params = new URLSearchParams(window.location.search);
    params.set('mode', 'update');
    params.set('last_id', lastKnownId); 

    try {
        const response = await fetch(`${window.location.pathname}?${params.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (response.ok) {
            const serverData = await response.json();

            if (serverData.status === 'updated') {
                console.log("Novos vídeos encontrados! Atualizando...");

                const container = document.getElementById('video-list-container');
                if (container) {
                    container.innerHTML = serverData.html;
                    
                    container.style.opacity = '0.5';
                    setTimeout(() => container.style.opacity = '1', 300);
                }

                if (typeof updatePlaylistData === 'function') {
                    updatePlaylistData(serverData.data, true);
                }
                
            } 
        }
    } catch (e) {
        console.error("Erro no monitoramento de novos vídeos:", e);
    }
}