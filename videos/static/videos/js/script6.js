  // Configuração de elementos
        const els = {
            container: document.getElementById('logsContainer'),
            loader: document.getElementById('loader'),
            empty: document.getElementById('emptyState'),
            inputs: {
                search: document.getElementById('searchInput'),
                client: document.getElementById('clientFilter'),
                limit: document.getElementById('limitFilter'),
            },
            modal: {
                self: document.getElementById('detailModal'),
                content: document.getElementById('modalContent'),
                clientBadge: document.getElementById('modalClient'),
                date: document.getElementById('modalDate'),
                card: document.querySelector('#detailModal > div')
            },
            refreshIcon: document.getElementById('refreshIcon')
        };

        // Função Principal de Busca
        async function fetchLogs() {
            // Estado de Loading
            els.container.style.opacity = '0.4';
            els.loader.classList.remove('hidden');
            els.refreshIcon.classList.add('animate-spin'); // Anima o botão refresh
            
            // Coletar valores
            const params = new URLSearchParams({
                search: els.inputs.search.value,
                client: els.inputs.client.value,
                limit: els.inputs.limit.value
            });

            try {
                // Chamada API (Ajuste a URL conforme seu setup Django)
                const response = await fetch(`/api/logs/list/?${params}`);
                
                if (!response.ok) throw new Error('Falha na rede');
                
                const data = await response.json();
                renderLogs(data.logs);

            } catch (error) {
                console.error('Erro:', error);
                els.container.innerHTML = `
                    <div class="text-center p-8 text-red-500 bg-red-50 rounded-lg border border-red-100">
                        <p class="font-bold">Erro ao carregar dados.</p>
                        <p class="text-sm text-red-400 mt-1">${error.message}</p>
                    </div>`;
            } finally {
                // Remove Loading
                els.container.style.opacity = '1';
                els.loader.classList.add('hidden');
                els.refreshIcon.classList.remove('animate-spin');
            }
        }

        // Renderização HTML
        function renderLogs(logs) {
            els.container.innerHTML = '';
            
            if (!logs || logs.length === 0) {
                els.empty.classList.remove('hidden');
                return;
            }
            els.empty.classList.add('hidden');

            const fragment = document.createDocumentFragment();

            logs.forEach((log, index) => {
                const div = document.createElement('div');
                // Estilos de cor baseados na origem
                const isServer = log.client.toLowerCase() === 'server';
                const badgeColor = isServer ? 'bg-slate-700' : 'bg-neutral-500';
                const borderColor = isServer ? 'border-slate-700' : 'border-neutral-500';

                // Delay da animação
                div.style.animationDelay = `${index * 0.03}s`; // 30ms de delay cascata
                
                div.className = `log-item bg-white p-4 rounded-xl border-l-[6px] ${borderColor} shadow-sm hover:shadow-md hover:translate-x-1 transition-all cursor-pointer group flex items-start gap-4 mb-3 border-y border-r border-slate-100`;

                div.innerHTML = `
                    <div class="flex flex-col items-end min-w-[85px] text-right pt-0.5 border-r border-slate-100 pr-4">
                        <span class="text-xs font-bold text-slate-700">${log.data}</span>
                        <span class="text-[11px] text-slate-400 font-mono mt-0.5">${log.hora}</span>
                    </div>

                    <div class="flex-1 min-w-0 flex flex-col gap-1">
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] uppercase tracking-wider font-bold text-white px-2 py-0.5 rounded-md ${badgeColor} shadow-sm">
                                ${log.client}
                            </span>
                            <span class="text-xs text-slate-400">ID #${log.id}</span>
                        </div>
                        <p class="text-sm text-slate-600 truncate font-mono mt-1 group-hover:text-slate-900 transition-colors select-none">
                            ${log.mensagem}
                        </p>
                    </div>

                    <div class="self-center pl-2 text-slate-300 group-hover:text-slate-600 transition-colors">
                        <i data-lucide="chevron-right-circle" class="w-5 h-5"></i>
                    </div>
                `;

                // Evento de Click para o Modal
                div.onclick = () => openModal(log);
                fragment.appendChild(div);
            });

            els.container.appendChild(fragment);
            lucide.createIcons();
        }

        // --- Lógica do Modal ---
        function openModal(log) {
            const isServer = log.client.toLowerCase() === 'server';
            
            // Preenche dados
            els.modal.content.textContent = log.mensagem; // textContent protege contra XSS
            els.modal.date.textContent = `${log.data} às ${log.hora}`;
            
            // Estiliza a badge do modal dinamicamente
            els.modal.clientBadge.textContent = log.client;
            els.modal.clientBadge.className = `ml-1 px-2 py-0.5 rounded text-xs font-bold text-white shadow-sm ${isServer ? 'bg-slate-700' : 'bg-neutral-500'}`;

            // Abre
            els.modal.self.classList.remove('hidden');
            // Timeout para permitir o render antes da transição CSS
            requestAnimationFrame(() => {
                els.modal.self.classList.remove('opacity-0');
                els.modal.card.classList.remove('scale-95');
                els.modal.card.classList.add('scale-100');
            });
        }

        function closeModal() {
            els.modal.self.classList.add('opacity-0');
            els.modal.card.classList.remove('scale-100');
            els.modal.card.classList.add('scale-95');
            
            setTimeout(() => {
                els.modal.self.classList.add('hidden');
            }, 300); // Espera a duração da transição
        }

        // Fechar ao clicar fora
        els.modal.self.addEventListener('click', (e) => {
            if (e.target === els.modal.self) closeModal();
        });

        // Fechar com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !els.modal.self.classList.contains('hidden')) {
                closeModal();
            }
        });

        // --- Listeners de Filtros ---
        
        // Debounce para busca (espera 400ms após parar de digitar)
        let debounceTimer;
        els.inputs.search.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(fetchLogs, 400);
        });

        // Selects acionam imediatamente
        els.inputs.client.addEventListener('change', fetchLogs);
        els.inputs.limit.addEventListener('change', fetchLogs);

        // --- Inicialização ---
        document.addEventListener('DOMContentLoaded', () => {
            lucide.createIcons();
            fetchLogs();
        });
