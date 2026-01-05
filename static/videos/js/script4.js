// ==========================================
// 8. PESQUISA (CTRL + P) & FILTRO DE DATA
// ==========================================
// ==========================================
// 8. PESQUISA AVANÇADA (SPOTLIGHT)
// ==========================================

const searchOverlay = document.getElementById('search-overlay');
const searchInput = document.getElementById('searchInput');
const resultsList = document.getElementById('search-results-list');

// Atalho CTRL+P e ESC
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'p') {
        e.preventDefault();
        toggleSearch();
    }
    if (e.key === 'Escape') {
        if (searchOverlay && searchOverlay.classList.contains('active')) {
            toggleSearch();
        }
    }
});

// Listener de Digitação
if (searchInput) {
    searchInput.addEventListener('input', function(e) {
        performSearch(e.target.value);
    });
}

function toggleSearch() {
    if (searchOverlay.classList.contains('active')) {
        // Fechar: Limpa input e esconde
        searchOverlay.classList.remove('active');
        setTimeout(() => { searchOverlay.style.display = 'none'; }, 200);
        searchInput.value = '';
        resultsList.innerHTML = '<div class="search-placeholder">Digite para buscar...</div>';
    } else {
        // Abrir
        searchOverlay.style.display = 'flex';
        // Pequeno delay para animação CSS
        setTimeout(() => { 
            searchOverlay.classList.add('active'); 
            searchInput.focus();
        }, 10);
    }
}

function performSearch(term) {
    const lowerTerm = term.toLowerCase().trim();
    resultsList.innerHTML = ''; // Limpa resultados anteriores

    if (!lowerTerm) {
        resultsList.innerHTML = '<div class="search-placeholder">Digite o nome do vídeo...</div>';
        return;
    }

    // Filtra no array global de dados (allVideosData)
    const filteredVideos = allVideosData.filter(video => {
        const title = (video.title || '').toLowerCase();
        const date = (video.date || '').toLowerCase();
        return title.includes(lowerTerm) || date.includes(lowerTerm);
    });

    if (filteredVideos.length === 0) {
        resultsList.innerHTML = '<div class="search-placeholder">Nenhum vídeo encontrado.</div>';
        return;
    }

    // Gera o HTML da lista
    filteredVideos.forEach(video => {
        const item = document.createElement('div');
        item.className = 'search-item';
        
        // Define ação ao clicar
        item.onclick = function() {
            // 1. Fecha a busca
            toggleSearch();
            
            // 2. Toca o vídeo (Isso vai abrir o modal do player)
            // Opcional: Se quiser que a playlist seja APENAS os resultados da busca, 
            // você pode setar currentPlaylist = filteredVideos aqui.
            playVideo(video.id); 
        };

        const thumb = video.thumbnail ? video.thumbnail : ''; 
        // Se não tiver thumbnail, usa um placeholder colorido ou ícone
        const thumbHTML = thumb 
            ? `<img src="${thumb}" class="search-item-thumb" alt="Thumb">`
            : `<div class="search-item-thumb" style="background:#333; display:flex; align-items:center; justify-content:center;">🎬</div>`;

        item.innerHTML = `
            ${thumbHTML}
            <div class="search-item-info">
                <span class="search-item-title">${video.title || 'Vídeo #' + video.id}</span>
                <span class="search-item-date">📅 ${video.created_at_formatted || video.date}</span>
            </div>
            <div style="font-size: 12px; color: #666;">↵ Enter</div>
        `;

        resultsList.appendChild(item);
    });
}
function filterVideos(searchTerm) {
    const term = searchTerm.toLowerCase();
    const cards = document.querySelectorAll('.video-card');
    let visibleCount = 0;
    
    cards.forEach(card => {
        // Busca no título e na data (se estiver visível no card)
        const titleContainer = card.querySelector('.video-title');
        const title = titleContainer ? titleContainer.textContent.toLowerCase() : '';
        
        // Se o termo estiver no título, mostra (flex), senão esconde (none)
        if (title.includes(term)) {
            card.style.display = 'flex';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    // Atualiza contador no modal
    const info = document.getElementById('searchResults');
    if (info) {
        info.textContent = term ? `${visibleCount} vídeos encontrados` : 'Digite para buscar...';
    }
}

// --- Lógica de Filtro de Data (Backend) ---

function filterByDate() {
    const start = document.getElementById('startDate').value;
    const end = document.getElementById('endDate').value;
    
    if (!start && !end) {
        alert("Selecione pelo menos uma data.");
        return;
    }

    // Monta a URL com parâmetros GET
    const url = new URL(window.location.href);
    if (start) url.searchParams.set('start_date', start);
    if (end) url.searchParams.set('end_date', end);
    
    // Reseta a paginação para a página 1 ao filtrar
    url.searchParams.set('page', 1);

    // Redireciona para recarregar a página com os dados filtrados
    window.location.href = url.toString();
}

function clearDateFilter() {
    // Remove os parâmetros de data da URL
    const url = new URL(window.location.href);
    url.searchParams.delete('start_date');
    url.searchParams.delete('end_date');
    window.location.href = url.toString();
}