import subprocess
def listar_dispositivos_audio():
    comando = [
        'ffmpeg',
        '-hide_banner',
        '-list_devices', 'true',
        '-f', 'dshow',
        '-i', 'dummy'
    ]

    processo = subprocess.Popen(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )

    _, stderr = processo.communicate()

    dispositivos = []

    for linha in stderr.splitlines():
        if '(audio)' in linha and '"' in linha:
            nome = linha.split('"')[1]
            dispositivos.append(nome)

    return dispositivos


if __name__ == "__main__":
    dispositivos = listar_dispositivos_audio()
    print(dispositivos)