// ==========================================
// 1. VARIÁVEIS GLOBAIS
// ==========================================
let allVideosData = [];
let currentPlaylist = [];
let currentVideoIndex = 0;

// ==========================================
// 2. INICIALIZAÇÃO
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    // 1. Cria o Loader no HTML dinamicamente se não existir
    if (!document.getElementById('global-loader')) {
        const loaderHTML = `
            <div id="global-loader">
                <div class="big-spinner"></div>
                <div class="loader-text">Carregando Vídeo...</div>
            </div>`;
        document.body.insertAdjacentHTML('beforeend', loaderHTML);
    }

    // 2. Carrega dados
    const dataScript = document.getElementById('initial-video-data') || document.getElementById('video-data');
    if (dataScript) {
        try {
            allVideosData = JSON.parse(dataScript.textContent);
            allVideosData.sort((a, b) => a.id - b.id);
        } catch (e) {
            console.error("Erro JSON:", e);
        }
    }

    // 3. Listener para Auto-Next
    const player = document.getElementById('videoPlayer');
    if (player) {
        player.onended = function() {
            playNext();
        };
        
        // Listener de erro para não travar a tela preta
        player.onerror = function() {
            toggleLoader(false);
            alert("Erro ao carregar o vídeo.");
        };
    }
});

// ==========================================
// 3. LÓGICA DE REPRODUÇÃO (CORE)
// ==========================================

function playVideo(videoId, dateFilter) {
    if (dateFilter) {
        currentPlaylist = allVideosData.filter(v => v.date === dateFilter);
    } else {
        currentPlaylist = allVideosData;
    }
    
    currentVideoIndex = currentPlaylist.findIndex(v => v.id === videoId);
    
    if (currentVideoIndex === -1) {
        currentPlaylist = allVideosData;
        currentVideoIndex = currentPlaylist.findIndex(v => v.id === videoId);
    }

    if (currentVideoIndex !== -1) {
        prepareAndPlay(); // Nova função principal
    }
}

function playDate(dateFilter) {
    currentPlaylist = allVideosData.filter(v => v.date === dateFilter);
    if (currentPlaylist.length > 0) {
        currentVideoIndex = 0;
        prepareAndPlay();
    } else {
        alert("Nenhum vídeo nesta data.");
    }
}

/**
 * Função Mágica: Mostra loader -> Carrega -> Abre Modal -> Fullscreen -> Play
 */
function prepareAndPlay() {
    const player = document.getElementById('videoPlayer');
    if (!player || currentPlaylist.length === 0) return;

    const video = currentPlaylist[currentVideoIndex];
    
    // 1. Mostra Loader e trava interação
    toggleLoader(true);

    // 2. Define a fonte
    player.src = video.url;
    
    // Ajusta velocidade (se houver preferência salva ou padrão)
    const speedSelect = document.getElementById('speedRate');
    if (speedSelect) player.playbackRate = parseFloat(speedSelect.value);

    // 3. Evento único: Dispara quando o vídeo tem dados suficientes para o primeiro frame
    player.onloadeddata = function() {
        // Remove o loader
        toggleLoader(false);

        // Abre o Modal
        openModal();

        // Atualiza Títulos
        updatePlayerInfo(video);

        // Tenta Fullscreen e Play
        // Nota: Fullscreen requer "gesto do usuário". Como viemos de um clique,
        // geralmente funciona, mas se a net for lenta, o navegador pode bloquear.
        requestFullScreen(player);
        
        player.play().catch(e => console.log("Play auto bloqueado:", e));

        // Limpa o evento para não disparar se o usuário fizer seek (avançar/voltar)
        player.onloadeddata = null; 
    };
    
    // Força o carregamento
    player.load(); 
}

function playNext() {
    if (currentVideoIndex < currentPlaylist.length - 1) {
        currentVideoIndex++;
    } else {
        currentVideoIndex = 0; // Loop
    }
    // No playNext, talvez não queira fullscreen de novo se já estiver, 
    // mas a função lida bem com isso.
    prepareAndPlay();
}

function playPrev() {
    if (currentVideoIndex > 0) {
        currentVideoIndex--;
        prepareAndPlay();
    }
}

// ==========================================
// 4. AUXILIARES DE UI
// ==========================================

function updatePlayerInfo(video) {
    const title = document.getElementById('playerTitle');
    const counter = document.getElementById('playerCounter');
    
    if (title) title.textContent = video.title || `Vídeo #${video.id}`;
    if (counter) counter.textContent = `${currentVideoIndex + 1} / ${currentPlaylist.length}`;
}

function toggleLoader(show) {
    const loader = document.getElementById('global-loader');
    if (loader) {
        if (show) loader.classList.add('active');
        else loader.classList.remove('active');
    }
}

function openModal() {
    const modal = document.getElementById('videoModal');
    if (modal) {
        modal.classList.add('active');
        modal.style.display = 'flex';
    }
}
function closeVideo() {
    const player = document.getElementById('videoPlayer');
    const modal = document.getElementById('videoModal');
    
    // 1. Verificação de Segurança do Fullscreen
    // Verifica se REALMENTE existe um elemento em tela cheia antes de tentar sair
    const isFullScreen = document.fullscreenElement || 
                         document.webkitFullscreenElement || 
                         document.mozFullScreenElement || 
                         document.msFullscreenElement;

    if (isFullScreen) {
        try {
            if (document.exitFullscreen) {
                document.exitFullscreen().catch(err => console.log("Fullscreen exit handled silently"));
            } else if (document.webkitExitFullscreen) { /* Safari */
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { /* IE11 */
                document.msExitFullscreen();
            }
        } catch (e) {
            // Ignora erros se o navegador já tiver saído do modo tela cheia
            console.warn("Tentativa de sair do fullscreen ignorada:", e);
        }
    }

    // 2. Parar o Vídeo e Limpar Memória
    if (player) {
        player.pause();
        // Remove o atributo src completamente para parar o download de dados
        player.removeAttribute('src'); 
        player.load(); 
    }

    // 3. Fechar Visualmente
    if (modal) {
        modal.classList.remove('active');
        // Pequeno delay para garantir que a animação de fade-out ocorra se houver CSS para isso
        // Se não, o display none funciona imediatamente
        setTimeout(() => {
            modal.style.display = 'none';
        }, 100); 
    }
    
    // 4. Garante que o spinner de carregamento suma
    toggleLoader(false);
}
// ==========================================
// 5. FULLSCREEN API
// ==========================================
function requestFullScreen(element) {
    // Tenta entrar em fullscreen (cross-browser)
    try {
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) { /* Safari */
            element.webkitRequestFullscreen();
        } else if (element.msRequestFullscreen) { /* IE11 */
            element.msRequestFullscreen();
        }
    } catch(e) {
        console.log("Fullscreen bloqueado ou não suportado:", e);
    }
}

// ==========================================
// 6. FUNÇÕES EXTRA (Paginação, Edição, Speed)
// ==========================================

function changeSpeed(rate) {
    const player = document.getElementById('videoPlayer');
    if (player) player.playbackRate = parseFloat(rate);
}

function loadMoreVideos(pageNumber) {
    const btn = document.getElementById('btn-load-more');
    if(btn) { btn.innerText = "Carregando..."; btn.disabled = true; }

    fetch(`?page=${pageNumber}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(r => r.text())
    .then(html => {
        const c = document.getElementById('video-list-container');
        if(c) c.insertAdjacentHTML('beforeend', html);
        if(btn && btn.parentElement) btn.parentElement.remove();
    })
    .catch(e => console.error(e));
}

function updatePlaylistData(newVideos, replaceAll = false) {
    if (!Array.isArray(newVideos)) return;

    if (replaceAll) {
        allVideosData = newVideos;
    } else {
        const existingIds = new Set(allVideosData.map(v => v.id));
        const uniqueNewVideos = newVideos.filter(v => !existingIds.has(v.id));
        
        allVideosData = uniqueNewVideos.concat(allVideosData);
    }
    
    allVideosData.sort((a, b) => b.id - a.id);
}

function toggleEdit(id) {
    const d = document.getElementById(`title-display-${id}`);
    const i = document.getElementById(`title-input-${id}`);
    if (d && i) { d.style.display = 'none'; i.style.display = 'block'; i.focus(); }
}

function saveTitle(id) {
    const i = document.getElementById(`title-input-${id}`);
    const d = document.getElementById(`title-display-${id}`);
    if (!i || !d) return;
    const t = i.value;
    i.style.display = 'none'; d.textContent = t; d.style.display = 'block';
    
    // Atualiza memória local também
    const v = allVideosData.find(v => v.id === id);
    if(v) v.title = t;

    fetch(`/video/${id}/update_title/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ title: t })
    });
}

function getCookie(name) {
    let v = null;
    if (document.cookie && document.cookie !== '') {
        const c = document.cookie.split(';');
        for (let i = 0; i < c.length; i++) {
            const x = c[i].trim();
            if (x.substring(0, name.length + 1) === (name + '=')) {
                v = decodeURIComponent(x.substring(name.length + 1));
                break;
            }
        }
    }
    return v;
}