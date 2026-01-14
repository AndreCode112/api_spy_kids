import shutil
import subprocess
import sys
import os

def verificar_e_instalar(nome_comando, winget_id):
    """
    Verifica se um programa está no PATH. Se não estiver, tenta instalar via Winget.
    
    :param nome_comando: O comando que você digita no terminal (ex: 'ffmpeg')
    :param winget_id: O ID do pacote no repositório do Winget (ex: 'Gyan.FFmpeg')
    """
    
    print(f"🔍 Verificando se '{nome_comando}' está instalado...")

    # shutil.which procura o executável nas variáveis de ambiente do sistema
    caminho = shutil.which(nome_comando)

    if caminho:
        print(f"✅ Sucesso! '{nome_comando}' já está instalado em: {caminho}")
        return True
    else:
        print(f"❌ '{nome_comando}' não encontrado. Iniciando instalação via Winget...")
        
        try:
            # Comando do winget para instalar silenciosamente e aceitar termos
            # -e: Exato (para não instalar programa errado com nome parecido)
            # --accept-...: Aceita os termos de licença automaticamente
            
            cmd = [
                "winget", "install", 
                "-e", "--id", winget_id,
                "--accept-package-agreements",
                "--accept-source-agreements"
            ]
            
            # Roda o comando e espera terminar
            resultado = subprocess.run(cmd, shell=True)

            if resultado.returncode == 0:
                print(f"\n✅ Instalação do {nome_comando} concluída!")
                print("⚠️  IMPORTANTE: Você pode precisar fechar e abrir este terminal/VSCode")
                print("    para que o Windows reconheça o novo comando.")
                return True
            else:
                print(f"\n❌ Erro ao instalar. O Winget retornou código: {resultado.returncode}")
                return False

        except FileNotFoundError:
            print("\n❌ Erro: O comando 'winget' não foi encontrado.")
            print("Verifique se você está no Windows 10/11 atualizado.")
            return False

if __name__ == "__main__":
    # --- CONFIGURAÇÃO ---
    PROGRAMA = "ffmpeg"
    ID_WINGET = "FFmpeg (Essentials Build)"  # Esse é o ID oficial do FFmpeg 'Essentials'
    # --------------------

    verificar_e_instalar(PROGRAMA, ID_WINGET)