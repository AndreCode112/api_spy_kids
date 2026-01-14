// ==========================================
// 7. EDIÇÃO DE TÍTULO (MODAL)
// ==========================================

const editModal = document.getElementById('editTitleModal');
const titleInput = document.getElementById('newTitleInput');
const idInput = document.getElementById('editVideoId');

function openEditModal(videoId, currentTitle) {
    if (editModal) {
        // Popula os dados
        idInput.value = videoId;
        titleInput.value = currentTitle;
        
        // Abre o modal com animação
        editModal.style.display = 'flex';
        // Pequeno delay para permitir a transição de opacidade/CSS
        setTimeout(() => {
            editModal.classList.add('active');
            titleInput.focus();
        }, 10);
    }
}

function closeEditModal() {
    if (editModal) {
        editModal.classList.remove('active');
        setTimeout(() => {
            editModal.style.display = 'none';
        }, 300); // Tempo da transição CSS
    }
}

// Salvar via AJAX
function saveNewTitle() {
    const videoId = idInput.value;
    const newTitle = titleInput.value.trim();

    if (!newTitle) {
        alert("O título não pode ser vazio.");
        return;
    }

    // Fecha o modal imediatamente (UI otimista)
    closeEditModal();
    
    // Atualiza na tela (DOM) imediatamente
    // Procura o elemento de título no card do vídeo
    // NOTA: Certifique-se que no HTML o título tenha uma classe ou ID identificável
    // Exemplo: <div class="video-title" id="video-title-text-123">...</div>
    
    // Como seu HTML atual usa uma estrutura específica, vamos tentar atualizar:
    // Se você usava o ID `title-display-${videoId}` ou apenas a classe `.video-title` dentro do card
    const card = document.querySelector(`.video-card[data-video-id="${videoId}"]`);
    if (card) {
        const titleEl = card.querySelector('.video-title') || card.querySelector(`[id^="title-display-"]`);
        if (titleEl) {
            titleEl.textContent = newTitle;
        }
    }

    // Atualiza na memória do player (allVideosData)
    const videoInMemory = allVideosData.find(v => v.id == videoId);
    if (videoInMemory) {
        videoInMemory.title = newTitle;
    }

    // Envia para o Backend
    fetch(`/video/${videoId}/update_title/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ title: newTitle })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            console.log("Título salvo com sucesso");
        } else {
            alert("Erro ao salvar no servidor. Recarregue a página.");
        }
    })
    .catch(err => {
        console.error("Erro:", err);
        alert("Erro de conexão ao salvar título.");
    });
}

// Fechar modal ao clicar fora (Overlay)
if (editModal) {
    editModal.addEventListener('click', function(e) {
        if (e.target === editModal) {
            closeEditModal();
        }
    });
    
    // Salvar com Enter
    titleInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            saveNewTitle();
        }
    });
}