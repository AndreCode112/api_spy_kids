

from django.http import HttpRequest
from rest_framework import status
from videos.models import Device, DeviceConfigAudio


class api_add_string_audio:
    def __init__(self):
        self.strErr:str = ''
        self.status:int
        self.response:dict = {}

    def add_string_audio_api(self, request:HttpRequest , Hostname:str) -> bool:
        try:
            if Hostname == "":
                self.strErr = 'Parâmetros Hostname é obrigatório'
                self.status = status.HTTP_400_BAD_REQUEST
                return False
            
            device = Device.objects.filter(hostname=Hostname).first()


            data = request.data
            Audios:list = data.get('audios', [])


            for audio in Audios:
                AudioExists = DeviceConfigAudio.objects.filter(
                    hostname=device,
                    audio=audio
                ).exists()

                if not AudioExists:
                    DeviceConfigAudio.objects.create(
                        hostname=device,
                        audio=audio
                    )


            self.response = {
                'success': True,
                'message': 'Lista de áudios adicionada e verificada com sucesso'
            }

            self.strErr = ''
            self.status = status.HTTP_200_OK
            return True

        except Device.DoesNotExist:
            self.strErr = 'Dispositivo não encontrado.'
            self.status = status.HTTP_404_NOT_FOUND
            return False
        
        except Exception as e:
            self.strErr = 'Erro ao adicionar a string de áudio: ' + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
        

        
            
