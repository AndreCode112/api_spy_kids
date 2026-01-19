import subprocess
import sys
import os
import argparse
import ctypes
import socket
import time

# =========================
# FUNÇÃO: VERIFICA ADMIN
# =========================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# =========================
# ELEVA PERMISSÃO (UAC)
# =========================
if not is_admin():
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        params,
        None,
        1
    )
    sys.exit(0)

# =========================
# FUNÇÃO: VERIFICA INTERNET
# =========================
def has_internet(host="8.8.8.8", port=53, timeout=3):
    """
    Testa se há conexão com a internet tentando abrir socket com DNS do Google.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

# =========================
# ARGUMENTOS
# =========================
parser = argparse.ArgumentParser(
    description="Cria uma tarefa no Agendador do Windows para iniciar um .exe junto com o sistema"
)

parser.add_argument(
    "-nt", "--nome-tarefa",
    required=True,
    help="Nome da tarefa no Agendador"
)

parser.add_argument(
    "-c", "--caminho-exe",
    required=True,
    help="Caminho completo para o arquivo .exe"
)

parser.add_argument(
    "-p", "--pasta-inicial",
    default="",
    help="Pasta inicial do programa (opcional)"
)

args = parser.parse_args()

NOME_TAREFA = args.nome_tarefa
CAMINHO_EXE = os.path.abspath(args.caminho_exe)
PASTA_INICIAL = os.path.abspath(args.pasta_inicial) if args.pasta_inicial else ""

# =========================
# VERIFICAÇÕES
# =========================
if not os.path.isfile(CAMINHO_EXE):
    print("❌ ERRO: O arquivo .exe não foi encontrado.")
    print(f"📄 Caminho informado: {CAMINHO_EXE}")
    sys.exit(1)

# =========================
# SCRIPT INTERMEDIÁRIO PARA INTERNET
# =========================
# Vamos criar um pequeno batch que aguarda internet antes de executar
BAT_PATH = os.path.join(os.environ["TEMP"], "start_app_with_internet.bat")

bat_content = f"""@echo off
:LOOP
ping -n 2 8.8.8.8 >nul
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto LOOP
)
cd /d "{PASTA_INICIAL}" 2>nul
start "" "{CAMINHO_EXE}"
exit
"""

with open(BAT_PATH, "w") as f:
    f.write(bat_content)

# =========================
# COMANDO SCHTASKS
# =========================
USUARIO_ATUAL = os.getlogin()

comando = [
    "schtasks",
    "/create",
    "/f",
    "/sc", "onlogon",       # Executa no login do usuário
    "/rl", "highest",       # Permissão máxima
    "/tn", NOME_TAREFA,
    "/tr", BAT_PATH,
    "/ru", USUARIO_ATUAL
]

# =========================
# EXECUÇÃO
# =========================
try:
    subprocess.run(
        comando,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    print("✅ Tarefa criada com sucesso!")
    print(f"📌 Nome da tarefa: {NOME_TAREFA}")
    print(f"🚀 Executável: {CAMINHO_EXE}")
    print("🔁 O programa será iniciado junto com o sistema, após conexão com a internet.")

except subprocess.CalledProcessError:
    print("❌ Erro ao criar a tarefa no Agendador.")
    sys.exit(1)
