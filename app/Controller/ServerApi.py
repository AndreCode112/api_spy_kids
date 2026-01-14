import os
import subprocess
import requests
from comuns.params import Tparams
from Controller.infoOs import DtoInfoDisp
from dto.configDevice import DtoConfigDevice
from Controller.logs import logs

class ServerRequestApi:
    def __init__(self):
        self.strErr:str = ''
        self.Tparams: Tparams = Tparams()

    def _upload_video(self) -> bool:
        try:

            if not os.path.exists(self.Tparams.pathVideoUploadSave):
                self.strErr = 'Arquivo de vídeo não encontrado.'
                return False
            

            with open(self.Tparams.pathVideoUploadSave, 'rb') as video_file:
                files = {'file': video_file}
                data = {'duration_seconds': DtoConfigDevice.tempo} 
                
                response = requests.post(self.Tparams.UPLOAD_URL, files=files, data=data, timeout=120)
                
                if response.status_code != 200:
                    self.strErr = f"Erro no upload: {response.status_code} - {response.text}"
                    return False
                    
            self.strErr = ''
            return True
        except Exception as e:
            self.strErr = f"Erro ao enviar vídeo: {e}"
            return False    
        

    def _upload_video_external_server(self) -> bool:
        try:

            if not os.path.exists(self.Tparams.pathVideoUploadSave):
                self.strErr = 'Arquivo de vídeo não encontrado.'
                return False

            with open(self.Tparams.pathVideoUploadSave, "rb") as f:
                files = {
                    "arquivo": (os.path.basename(self.Tparams.pathVideoUploadSave), f)
                }

                response = requests.post(self.Tparams.UPLOAD_EXTERNALSERVER_URL, files=files)

            json_response = response.json()
            status = json_response.get("sucesso", False)
            if not status:
                self.strErr = f"Erro no upload para servidor externo: {json_response.get('message', 'Sem mensagem de erro')}"
                return False
            
            file_name_server = json_response.get("arquivo", "")

            if not file_name_server:
                self.strErr = "Nome do arquivo no servidor não retornado. cheque os logs do server externo."
                return False

            data = {
                "file_name_server": file_name_server,
                "duration": DtoConfigDevice.tempo
            }
            response = requests.post(
                self.Tparams.UPLOAD_URL,
                data=data,
                timeout=10,
            )
            self.strErr = ''
            return True
        
        except Exception as e:
            self.strErr = f"Erro ao enviar vídeo para servidor externo: {e}"
            return False

    def _send_status_connected(self) -> bool:
        try:
            payload = {
                "hostname": DtoInfoDisp.hostname,
                "ip_address": DtoInfoDisp.ip_address,
                "device_name": DtoInfoDisp.device_name,
                "status": DtoInfoDisp.status 
            }
    
            response = requests.post(self.Tparams.CONNECTIONINFO_URL, json=payload, timeout=10)
            
            if response.status_code != 200:
                self.strErr = f"Erro ao enviar status: {response.status_code} - {response.text}"
                return False
            
            self.strErr = ''
            return True
        except Exception as e:
            self.strErr = f"Erro de conexão ao enviar status: {e}"
            return False
        
    def _getConfigServer(self)-> bool:
        try:
            route = self.Tparams.APIGETCONFIGDEVICE_URL + DtoInfoDisp.hostname + "/"
            response = requests.get(route, timeout=10)
            
            if response.status_code != 200:
                self.strErr = f"Erro ao obter configuração: {response.status_code} - {response.text}"
                return False
            
            config_data = response.json()

            
            if (config_data.get('tempo', 0) <= 0) or (config_data.get('audio', '') == ''):
                self.strErr = 'Configuração vazias recebida do servidor, Verifique o cadastro para o hostname: ' + DtoInfoDisp.hostname
                logs(self.strErr).log_messageTxt()
                
            tempo_video = config_data.get('tempo', DtoConfigDevice.tempo)
            audio_config = config_data.get('audio', DtoConfigDevice.audio_padrão)    

            DtoConfigDevice.tempo = tempo_video
            DtoConfigDevice.audio = audio_config

            self.strErr = ''
            return True
        except Exception as e:
            self.strErr = f"Erro de conexão ao obter configuração: {e}"
            return False
        

    def _send_audio_config(self, Listaudio:list) -> bool:
        try:
            if len(Listaudio) <=0:
                self.strErr = 'Lista de áudios está vazia.'
                return False 

            payload = {
                "audios": Listaudio
            }
    

            route = self.Tparams.APICONFIGDEVICEAUDIO_URL + DtoInfoDisp.hostname + "/"
            response = requests.post(route, json=payload, timeout=10)

            
            if response.status_code != 200:
                self.strErr = f"Erro ao enviar configuração de áudio: {response.status_code} - {response.text}"
                return False
            
            self.strErr = ''
            return True
        except Exception as e:
            self.strErr = f"Erro de conexão ao enviar configuração de áudio: {e}"
            return False
