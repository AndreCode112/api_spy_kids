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

            if (serverData.status === 'updated' && serverData.html.trim() !== "") {
                console.log(`Novos vídeos recebidos. Processando...`);

                const container = document.getElementById('video-list-container');
                const parser = new DOMParser();
                const doc = parser.parseFromString(serverData.html, 'text/html');
                
                const newGroups = doc.querySelectorAll('.date-group');

                Array.from(newGroups).reverse().forEach(newGroup => {
                    const dateKey = newGroup.getAttribute('data-date-group');
                    
                    const existingGroup = document.querySelector(`.date-group[data-date-group="${dateKey}"]`);

                    if (existingGroup) {
                        const grid = existingGroup.querySelector('.video-grid');
                        const newVideos = newGroup.querySelectorAll('.video-card');

                        Array.from(newVideos).reverse().forEach(video => {
                            video.classList.add('new-video-anim'); 
                            grid.insertAdjacentElement('afterbegin', video);
                        });
                    } else {
                        newGroup.classList.add('new-video-anim');
                        container.insertAdjacentElement('afterbegin', newGroup);
                    }
                });

                if (typeof updatePlaylistData === 'function') {
                    updatePlaylistData(serverData.data, false);
                }
            }
        }
    } catch (e) {
        console.error("Erro no monitoramento:", e);
    }
}