const modal_Agendar_check_qtd_video_el = document.getElementById("modal_Agendar_check_qtd_video");
    const modal_Agendar_check_qtd_video_resultArea = document.getElementById("modal_Agendar_check_qtd_video_resultadoArea");

    function modal_Agendar_check_qtd_video_abrir() {
        modal_Agendar_check_qtd_video_el.style.display = "block";
        modal_Agendar_check_qtd_video_resultArea.style.display = "none";
    }

    function modal_Agendar_check_qtd_video_fechar() {
        modal_Agendar_check_qtd_video_el.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal_Agendar_check_qtd_video_el) {
            modal_Agendar_check_qtd_video_fechar();
        }
    }

    async function modal_Agendar_check_qtd_video_processar(deveSalvar) {
        const inicio = document.getElementById('modal_Agendar_check_qtd_video_hora_inicio').value;
        const fim = document.getElementById('modal_Agendar_check_qtd_video_hora_fim').value;

        if (!inicio || !fim) {
            alert("Preencha os horários.");
            return;
        }

        try {
            const response = await fetch('/api/calcular/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': modal_Agendar_check_qtd_video_getCookie('csrftoken')
                },
                body: JSON.stringify({ 
                    'hora_inicio': inicio,
                    'hora_fim': fim,
                    'salvar': deveSalvar
                })
            });

            const dados = await response.json();

            if (response.ok) {
                // Cores ajustadas para o tema dark
                const corMsg = deveSalvar ? '#10b981' : '#38bdf8'; // Verde Emerald ou Azul Sky
                
                const html = `
                    <div class="modal_Agendar_check_qtd_video_feedback" style="color: ${corMsg}; border: 1px solid ${corMsg}; box-shadow: 0 0 10px ${corMsg}33;">${dados.mensagem}</div>
                    
                    <div class="modal_Agendar_check_qtd_video_result_item">
                        <span>Carga horária:</span> 
                        <span class="modal_Agendar_check_qtd_video_result_value">${dados.duracao_diaria} h</span>
                    </div>
                    <div class="modal_Agendar_check_qtd_video_result_item">
                        <span>Vídeos (capacidade):</span> 
                        <span class="modal_Agendar_check_qtd_video_result_value">${dados.videos}</span>
                    </div>
                    <div class="modal_Agendar_check_qtd_video_result_item">
                        <span>Dias completos:</span> 
                        <span class="modal_Agendar_check_qtd_video_result_value">${dados.dias} dias</span>
                    </div>
                    <div class="modal_Agendar_check_qtd_video_result_item">
                        <span>Sobra último dia:</span> 
                        <span class="modal_Agendar_check_qtd_video_result_value">${dados.horas_no_ultimo_dia} h</span>
                    </div>
                `;
                
                document.getElementById('modal_Agendar_check_qtd_video_listaResultados').innerHTML = html;
                modal_Agendar_check_qtd_video_resultArea.style.display = "block";
                
            } else {
                alert("Erro: " + dados.error);
            }

        } catch (error) {
            console.error('Erro:', error);
            alert("Erro de conexão.");
        }
    }

    function modal_Agendar_check_qtd_video_getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }