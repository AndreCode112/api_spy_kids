from rest_framework import status
from django.http import HttpRequest
from videos.models import Video
from datetime import timedelta
from .logs_notification import MensagensLogs
from videos.Dto.notifyDto import notifyDto
from videos.Dto.logDto import LogsDto
class uploadVideoExtenalServer:
    def __init__(self):
        self.strErr:str = ''
        self.status:int
        self.response:dict = {}

    def upload_video(self, request:HttpRequest) -> bool:
        try:
            file_name_server = request.POST.get('file_name_server')
            video_duration = request.POST.get('duration')

            if not file_name_server or not video_duration:
                raise ValueError("Campos obrigatórios não enviados")

            Video.objects.create(
                file_Server=file_name_server,
                duration=timedelta(seconds=int(video_duration)),
            )
            
            instanceMensagensLogs:MensagensLogs = MensagensLogs()
            if not instanceMensagensLogs.execute_notification('Um novo vídeo está disponível para visualização.', notifyDto.success):
                instanceMensagensLogs.execute_log_error(LogsDto.SERVER, 'Erro ao tentar registrar a notificação de vídeo recebido: ' + instanceMensagensLogs.strErr)

            self.strErr = ''
            self.status = status.HTTP_200_OK
            return True
        
        except Exception as e:
            self.strErr = "Erro ao tentar realizar o upload do video na nova api de upload: " + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False