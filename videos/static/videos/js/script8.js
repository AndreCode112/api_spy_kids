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
                console.log(`Novos vídeos detectados! Adicionando ${serverData.data.length} vídeos.`);

                const container = document.getElementById('video-list-container');
                
                if (container && serverData.html) {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(serverData.html, 'text/html');
                    const newGroups = doc.querySelectorAll('.date-group');

                    Array.from(newGroups).reverse().forEach(newGroup => {
                        const newDateText = newGroup.querySelector('.date-header').innerText.trim();
                        
                        const existingHeader = Array.from(document.querySelectorAll('.date-header'))
                            .find(h3 => h3.innerText.trim() === newDateText);
                        
                        if (existingHeader) {
                            const existingGroup = existingHeader.closest('.date-group');
                            const existingGrid = existingGroup.querySelector('.video-grid');
                            const newVideos = newGroup.querySelectorAll('.video-card');

                            Array.from(newVideos).reverse().forEach(videoCard => {
                                videoCard.style.animation = "fadeInHighlight 1s ease";
                                existingGrid.insertAdjacentElement('afterbegin', videoCard);
                            });
                        } else {
                            newGroup.style.animation = "fadeInHighlight 1s ease";
                            container.insertAdjacentElement('afterbegin', newGroup);
                        }
                    });
                }

                if (typeof updatePlaylistData === 'function') {
                    updatePlaylistData(serverData.data, false); 
                }
            } 
        }
    } catch (e) {
        console.error("Erro no monitoramento:", e);
    }
}