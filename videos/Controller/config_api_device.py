from rest_framework import status
from videos.models import DeviceConfig, Device

class api_device_config:
    def __init__(self):
        self.strErr:str = ''
        self.status:int
        self.response:dict = {}

    def configure_device_api(self, Hostname:str) -> bool:
        try:
            if Hostname == "":
                self.strErr = 'Parametro Hostname é obrigatório'
                self.status = status.HTTP_400_BAD_REQUEST
                return False
            
            device = Device.objects.filter(hostname=Hostname).first()
 
            config_device = DeviceConfig.objects.filter(hostname=device).first()

            self.response = {
                'tempo': config_device.tempo if config_device else 600,
                'audio': config_device.audio.audio if config_device else '',
            }

            self.strErr = ''
            self.status = status.HTTP_200_OK
            return True

        except Exception as e:
            self.strErr = 'Erro ao configurar o dispositivo: ' + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
        
        except Device.DoesNotExist:
            self.strErr = 'Dispositivo não encontrado.'
            self.status = status.HTTP_404_NOT_FOUND
            return False
        
        except DeviceConfig.DoesNotExist:
            self.strErr = 'Configuração do dispositivo não encontrada.'
            self.status = status.HTTP_404_NOT_FOUND
            return False
        
