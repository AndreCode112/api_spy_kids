
let selectedVideos = new Set();

function toggleSelection(checkbox) {
    const card = checkbox.closest('.video-card');
    const id = checkbox.value;

    if (checkbox.checked) {
        selectedVideos.add(id);
        card.classList.add('selected');
    } else {
        selectedVideos.delete(id);
        card.classList.remove('selected');
    }

    updateBulkBar();
}

function updateBulkBar() {
    const bar = document.getElementById('bulk-actions-bar');
    const countSpan = bar.querySelector('.selected-count');
    
    countSpan.innerText = selectedVideos.size;

    if (selectedVideos.size > 0) {
        bar.classList.add('active');
    } else {
        bar.classList.remove('active');
    }
}

function clearSelection() {
    document.querySelectorAll('.video-checkbox').forEach(cb => {
        cb.checked = false;
        toggleSelection(cb); // Reseta visual
    });
    selectedVideos.clear();
    updateBulkBar();
}

// --- DELETE EM MASSA ---
async function executeBulkDelete() {
    if (!confirm(`Tem certeza que deseja excluir ${selectedVideos.size} vídeos?`)) return;

    const ids = Array.from(selectedVideos);

    try {
        const response = await fetch('/videos/delete_multi_videos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ action: 'delete', ids: ids })
        });

        const result = await response.json();

        if (response.ok) {
            ids.forEach(id => {
                const card = document.querySelector(`.video-card[data-video-id="${id}"]`);
                if (card) {
                    card.style.transform = 'scale(0)';
                    setTimeout(() => card.remove(), 300);
                }
            });
            
            showToast(`${result.deleted_count} vídeos excluídos com sucesso.`);
            clearSelection();
            
            if (typeof allVideosData !== 'undefined') {
                allVideosData = allVideosData.filter(v => !ids.includes(v.id.toString()));
            }

        } else {
            alert('Erro ao excluir: ' + result.error);
        }
    } catch (e) {
        console.error(e);
        alert('Erro de conexão ao tentar excluir.');
    }
}

function executeBulkDownload() {
    const ids = Array.from(selectedVideos);
    
    if (ids.length === 0) {
        alert("Selecione pelo menos um vídeo.");
        return;
    }

    showToast(`Preparando ZIP com ${ids.length} vídeos... O download iniciará em breve.`);

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/videos/download_multi_zip/'; 
    form.style.display = 'none';

    const csrfInput = document.createElement('input');
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = getCookie('csrftoken'); 
    form.appendChild(csrfInput);

    const idsInput = document.createElement('input');
    idsInput.name = 'ids';
    idsInput.value = JSON.stringify(ids);
    form.appendChild(idsInput);

    document.body.appendChild(form);
    form.submit();
    
    setTimeout(() => {
        document.body.removeChild(form);
        clearSelection(); 
    }, 2000);
}