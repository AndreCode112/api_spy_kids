 let videoToDelete = null;
        let storageData = null;

        // Scroll effect on header
        window.addEventListener('scroll', () => {
            const header = document.querySelector('.header');
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });

        // Open device info modal
        async function openDeviceInfo() {
            const modal = document.getElementById('deviceModal');
            const overlay = document.getElementById('overlay');
            
            modal.classList.add('active');
            overlay.classList.add('active');
            
            // Load device info
            await loadDeviceInfo();
        }

        async function UpdateDeviceInfor() {
            await loadDeviceInfo();
        }

        // Close device info modal
        function closeDeviceInfo() {
            const modal = document.getElementById('deviceModal');
            const overlay = document.getElementById('overlay');
            
            modal.classList.remove('active');
            overlay.classList.remove('active');
        }

        // Load device information
        async function loadDeviceInfo() {
            const content = document.getElementById('deviceContent');
            
            try {
                const response = await fetch('/device/info/');
                const data = await response.json();
                
                if (data.found) {
                    content.innerHTML = renderDeviceCard(data.device);
                } else {
                    content.innerHTML = `
                        <div class="device-error">
                            ℹ️ Nenhum dispositivo foi encontrado. Verifique se há dispositivos cadastrados.<br>
                        </div>
                    `;
                }
            } catch (error) {
                content.innerHTML = `
                    <div class="device-error">
                        ⚠️ Erro ao carregar informações do dispositivo
                    </div>
                `;
            }
        }

        // Render device card
        function renderDeviceCard(device) {
            const lastSeen = new Date(device.last_seen);
            const createdAt = new Date(device.created_at);
            const lastCapture = device.last_capture ? new Date(device.last_capture) : null;
            
            
            const formatDate = (date) => {
                return date.toLocaleString('pt-BR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
            };

            const statusClass = device.is_online ? 'online' : 'offline';
            const statusText = device.is_online ? 'Online' : 'Offline';

            return `
                <div class="device-card">
                    <div class="device-header">
                        <div>
                            <div class="device-name">${device.device_name}</div>
                            <div class="timestamp">
                                <span class="timestamp-icon">🖥️</span>
                                <span>${device.hostname}</span>
                            </div>
                        </div>
                        <div class="status-badge ${statusClass}">
                            <span class="status-dot"></span>
                            ${statusText}
                        </div>
                    </div>

                    <div class="device-grid">
                        <div class="info-item">
                            <div class="info-label">IP Address</div>
                            <div class="info-value">${device.ip_address}</div>
                        </div>

                        <div class="info-item">
                            <div class="info-label">ID do Dispositivo</div>
                            <div class="info-value">#${device.id}</div>
                        </div>

                        <div class="info-item">
                            <div class="info-label">Registrado em</div>
                            <div class="info-value small">${formatDate(createdAt)}</div>
                        </div>

                        <div class="info-item">
                            <div class="info-label">Capturas</div>
                            <div class="info-value">${device.captures_count}</div>
                        </div>
                    </div>

                    <div class="divider"></div>

                    <div class="device-grid">
                        <div class="info-item">
                            <div class="info-label">🕐 Último Acesso</div>
                            <div class="info-value small">${formatDate(lastSeen)}</div>
                        </div>

                        ${lastCapture ? `
                            <div class="info-item">
                                <div class="info-label">📹 Última Captura</div>
                                <div class="info-value small">${formatDate(lastCapture)}</div>
                            </div>
                        ` : `
                            <div class="info-item">
                                <div class="info-label">📹 Última Captura</div>
                                <div class="info-value small">Nenhuma</div>
                            </div>
                        `}
                    </div>

                    <div class="divider"></div>

                    <div class="info-item" style="grid-column: 1 / -1;">
                        <div class="info-label">Status Atual</div>
                        <div class="info-value small" style="color: ${device.is_online ? '#4caf50' : '#f44336'};">
                            ${device.is_online ? '✅ Dispositivo ativo e enviando dados' : '❌ Dispositivo inativo'}
                        </div>
                    </div>
                </div>
            `;
        }

        // Open settings panel
        async function openSettings() {
            const panel = document.getElementById('settingsPanel');
            const overlay = document.getElementById('overlay');
            
            panel.classList.add('active');
            overlay.classList.add('active');
            
            // Load storage info
            await loadStorageInfo();
        }

        // Close settings panel
        function closeSettings() {
            const panel = document.getElementById('settingsPanel');
            const overlay = document.getElementById('overlay');
            
            panel.classList.remove('active');
            overlay.classList.remove('active');
        }

        // Load storage information
        async function loadStorageInfo() {
            const loadingIndicator = document.getElementById('loadingIndicator');
            loadingIndicator.style.display = 'inline-block';

            try {
                const response = await fetch('/storage/info/');
                const data = await response.json();

                if (data.success) {
                    storageData = data.storage;
                    updateStorageUI(storageData);
                } else {
                    console.error('Error loading storage info:', data.error);
                }
            } catch (error) {
                console.error('Error fetching storage info:', error);
            } finally {
                loadingIndicator.style.display = 'none';
            }
        }

        // Update storage UI
        function updateStorageUI(storage) {
            // Update text values
            document.getElementById('totalStorage').textContent = storage.total_gb;
            document.getElementById('usedStorage').textContent = storage.used_gb;
            document.getElementById('freeStorage').textContent = storage.free_gb;
            document.getElementById('percentText').textContent = Math.round(storage.percent_used) + '%';

            // Update progress bar
            const progressBar = document.getElementById('progressBar');
            setTimeout(() => {
                progressBar.style.width = storage.percent_used + '%';
            }, 100);

            // Update circular progress
            const circle = document.getElementById('progressCircle');
            const circumference = 408.407; // 2 * PI * 65
            const offset = circumference - (storage.percent_used / 100) * circumference;
            
            setTimeout(() => {
                circle.style.strokeDashoffset = offset;
            }, 100);
        }

      

        // Confirm delete
        function confirmDelete(videoId) {
            videoToDelete = videoId;
            document.getElementById('overlay').classList.add('active');
            document.getElementById('confirmDialog').classList.add('active');
        }

        // Cancel delete
        function cancelDelete() {
            videoToDelete = null;
            document.getElementById('overlay').classList.remove('active');
            document.getElementById('confirmDialog').classList.remove('active');
        }

        // Execute delete
        async function executeDelete() {
            if (!videoToDelete) return;

            try {
                const response = await fetch(`/video/${videoToDelete}/delete/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    }
                });

                const data = await response.json();

                if (data.success) {
                    // Remove card with animation
                    const card = document.querySelector(`[data-video-id="${videoToDelete}"]`);
                    card.style.animation = 'fadeOut 0.3s ease';
                    setTimeout(() => {
                        card.remove();
                        
                        // Check if empty
                        const grid = document.querySelector('.video-grid');
                        if (grid && grid.children.length === 0) {
                            location.reload();
                        }
                    }, 300);
                } else {
                    alert('Erro ao excluir vídeo: ' + data.message);
                }
            } catch (error) {
                alert('Erro ao excluir vídeo');
            }

            cancelDelete();
        }

        // Get CSRF token
        function getCookie(name) {
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

        // Close modal on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeVideo();
                cancelDelete();
                closeSettings();
                closeDeviceInfo();
            }
        });

        // Close modal on click outside
        document.getElementById('videoModal').addEventListener('click', (e) => {
            if (e.target.id === 'videoModal') {
                closeVideo();
            }
        });

        document.getElementById('overlay').addEventListener('click', (e) => {
            if (e.target.id === 'overlay') {
                cancelDelete();
                closeSettings();
                closeDeviceInfo();
            }
        });