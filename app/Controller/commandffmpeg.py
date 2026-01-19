from asyncio import log
import subprocess
from comuns.params import Tparams 
from dto.configDevice import DtoConfigDevice
from Controller.logs import logs


class CommandFFMPEG:
    def __init__(self):
        self.strErr: str = ''
        self.params = Tparams()
        self.lista_audios:list[str] =[]

    # def capture_video(self) -> bool:
    #     try:
    #         command = [
    #         'ffmpeg', '-y',
    #         '-f', 'gdigrab',
    #         '-framerate', '15',
    #         '-i', 'desktop',
    #         '-f', 'dshow',
    #         '-i', 'audio=' + DtoConfigDevice.audio,
    #         '-t', str(DtoConfigDevice.tempo),
    #         '-c:v', 'libx264',
    #         '-pix_fmt', 'yuv420p',
    #         '-preset', 'fast',
    #         '-c:a', 'aac',
    #         '-b:a', '128k',
    #         self.params.pathVideoUploadSave
    #     ]

    #         result = subprocess.run(command, capture_output=True, text=True)

    #         if result.returncode != 0:
    #             self.strErr = f"Erro no FFmpeg: {result.stderr}"
    #             return False
            
    #         self.strErr = ''
    #         return True
    #     except subprocess.CalledProcessError as e:
    #         self.strErr = f"Erro ao capturar vídeo: {e}"
    #         return False

    def capture_video(self) -> bool:
        try:
            command = [
                'ffmpeg', '-y',
                '-hide_banner',       
                '-loglevel', 'error',
                
                '-thread_queue_size', '4096', 
                '-f', 'gdigrab',
                '-framerate', '15',
                '-i', 'desktop'
            ]
            
            audio_input = f"audio={DtoConfigDevice.audio}" if DtoConfigDevice.audio else ''
            
            if audio_input:
                command.extend([
                    '-thread_queue_size', '4096', 
                    '-f', 'dshow',
                    '-i', audio_input
                ])

            command.extend([
                '-t', str(DtoConfigDevice.tempo),
                
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'ultrafast', 
                '-tune', 'zerolatency',
                '-c:a', 'aac',
            

                '-b:a', '128k',
                
                self.params.pathVideoUploadSave
            ])

            result =  subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode != 0:
                logs(self.strErr).log_messageTxt()
                return False
            
            self.strErr = ''
            return True

        except subprocess.CalledProcessError as e:
            self.strErr = f"Erro ao capturar vídeo (Process Error): {e}"
            return False
        except Exception as e:
            self.strErr = f"Erro inesperado ao iniciar captura de vídeo: {e}"
            return False
        
    def listar_dispositivos_audio(self)-> bool:
        try:
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
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            _, stderr = processo.communicate()

            
            for linha in stderr.splitlines():
                if '(audio)' in linha and '"' in linha:
                    nome = linha.split('"')[1]
                    self.lista_audios.append(nome)

            if len(self.lista_audios) > 0:
                DtoConfigDevice.audio_padrão = self.lista_audios[0]

                
            return True

        except Exception as e:
            self.strErr = f"Erro ao listar dispositivos de áudio: {e}"
            return False