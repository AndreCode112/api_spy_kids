import subprocess
import requests
import time
import socket
import os
import json
import sys
import signal
from datetime import datetime

# --- CONFIGURAÇÕES ---
# Altere para o IP onde seu Django está rodando
API_BASE_URL = "http://127.0.0.1:8000" 
UPLOAD_URL = f"{API_BASE_URL}/api/videos/"
HEARTBEAT_URL = f"{API_BASE_URL}/api/devices/status/"

# Nome do arquivo temporário
VIDEO_FILENAME = "video.temp.mp4"

# Configuração do Dispositivo (Captura automática)
HOSTNAME = socket.gethostname()
try:
    # Tenta pegar o IP da rede local
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP_ADDRESS = s.getsockname()[0]
    s.close()
except Exception:
    IP_ADDRESS = "127.0.0.1"

DEVICE_NAME = f"Workstation-{HOSTNAME}"

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def send_heartbeat(status_code="online"):
    """Envia sinal de vida para a API."""
    payload = {
        "hostname": HOSTNAME,
        "ip_address": IP_ADDRESS,
        "device_name": DEVICE_NAME,
        # Nota: Sua API atual força 'online' no backend, 
        # mas estamos enviando a intenção aqui.
        "status": status_code 
    }
    
    try:
        response = requests.post(HEARTBEAT_URL, json=payload, timeout=5)
        if response.status_code == 200:
            log(f"❤️ Heartbeat enviado ({status_code})")
        else:
            log(f"⚠️ Erro no heartbeat: {response.text}")
    except Exception as e:
        log(f"❌ Falha ao conectar com API (Heartbeat): {e}")

def record_screen():
    """Executa o comando FFmpeg para gravar a tela."""
    log("🎥 Iniciando gravação de 60 segundos...")
    
    # O comando exato solicitado, adaptado para lista de argumentos do Python
    # NOTA: O nome do áudio deve existir na máquina, caso contrário o FFmpeg falhará.
    command = [
        'ffmpeg', '-y', # -y para sobrescrever arquivo se existir
        '-f', 'gdigrab',
        '-framerate', '30',
        '-i', 'desktop',
        '-f', 'dshow',
        '-i', 'audio=Grupo de microfones (Tecnologia Intel® Smart Sound para microfones digitais)',
        '-t', '60',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        '-c:a', 'aac',
        '-b:a', '128k',
        VIDEO_FILENAME
    ]

    try:
        # Executa o comando e aguarda finalizar. 
        # capture_output=True esconde o log verboso do ffmpeg, remova para debugar
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            log(f"❌ Erro no FFmpeg: {result.stderr}")
            return False
            
        log("✅ Gravação concluída.")
        return True
    except Exception as e:
        log(f"❌ Erro ao executar gravação: {e}")
        return False

def upload_video():
    """Faz o upload do vídeo gravado para o Django."""
    if not os.path.exists(VIDEO_FILENAME):
        log("⚠️ Arquivo de vídeo não encontrado para upload.")
        return

    log("🚀 Iniciando upload para API...")
    
    try:
        with open(VIDEO_FILENAME, 'rb') as video_file:
            # Enviando duration "00:01:00" hardcoded pois o comando é fixo em 60s
            # Se seu Serializer exigir duration, isso ajuda.
            files = {'file': video_file}
            data = {'duration_seconds': 60} 
            
            response = requests.post(UPLOAD_URL, files=files, data=data, timeout=120)
            
            if response.status_code == 201:
                log("✅ Upload realizado com sucesso!")
                # Tenta mostrar em qual grupo caiu (baseado na resposta da sua API)
                try:
                    resp_json = response.json()
                    group_id = resp_json.get('group', {}).get('id', 'N/A')
                    log(f"🔗 Vídeo associado ao Grupo ID: {group_id}")
                except:
                    pass
            else:
                log(f"❌ Erro no upload: {response.status_code} - {response.text}")

    except Exception as e:
        log(f"❌ Erro de conexão no upload: {e}")

def cleanup():
    """Remove o arquivo temporário."""
    if os.path.exists(VIDEO_FILENAME):
        try:
            os.remove(VIDEO_FILENAME)
            log("🧹 Arquivo temporário limpo.")
        except Exception as e:
            log(f"⚠️ Erro ao limpar arquivo: {e}")

def graceful_exit(signum, frame):
    """Função chamada quando o script é interrompido (Ctrl+C)."""
    log("\n🛑 Encerrando aplicação...")
    # Tenta avisar a API que está ficando offline
    # Nota: Veja a observação abaixo sobre o Backend Django
    send_heartbeat("offline") 
    cleanup()
    sys.exit(0)

# --- LOOP PRINCIPAL ---

if __name__ == "__main__":
    # Registra o handler para Ctrl+C
    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    log(f"🤖 Cliente de Captura Iniciado em {HOSTNAME} ({IP_ADDRESS})")
    log("Pressione Ctrl+C para parar.")

    try:
        while True:
            # 1. Avisa que está online
            send_heartbeat("online")

            # 2. Grava o vídeo
            success = record_screen()

            if success:
                time.sleep(3)

                upload_video()

                cleanup()
            else:
                time.sleep(10)

    except Exception as e:
        log(f"🔥 Erro crítico no loop principal: {e}")
        send_heartbeat("offline")
        cleanup()