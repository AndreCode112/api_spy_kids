from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework import status
from videos.models import Video
from datetime import timedelta

from .logs_notification import MensagensLogs
from videos.Dto.notifyDto import notifyDto
from videos.Dto.logDto import LogsDto



class ApiVideo:
    def __init__(self):
        self.StrErr: str = ''
        self.status: int 

    def _Post(self, request:HttpRequest) -> bool:
        try:
            video_file = request.FILES.get('file')
            duracao = request.POST.get('duration_seconds')

            if not video_file:
                self.status = status.HTTP_400_BAD_REQUEST
                self.StrErr = 'Nenhum arquivo enviado'
                return False
            
            if not duracao:
                self.status = status.HTTP_400_BAD_REQUEST
                self.StrErr = 'Duração do vídeo não fornecida'
                return False
            

            Savevideo = Video.objects.create(
                file=video_file,
                duration=timedelta(seconds=int(duracao)),
                processed=False
            )
            Savevideo.save()

            instanceMensagensLogs:MensagensLogs = MensagensLogs()
            if not instanceMensagensLogs.execute_notification('Um novo vídeo está disponível para visualização.', notifyDto.success):
                instanceMensagensLogs.execute_log_error(LogsDto.SERVER, 'Erro ao tentar registrar a notificação de vídeo recebido: ' + instanceMensagensLogs.strErr)    

            self.status = status.HTTP_200_OK
            self.StrErr = ''
            return True 
        except Exception as e:
            self.StrErr = str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
        
    def _Delete(self, request, video_id):
        """API para deletar vídeo"""
        try:
            video = get_object_or_404(Video, id=video_id)
            
            if video.file:
                video.file.delete()
            video.delete()

            self.status = status.HTTP_200_OK
            self.StrErr = ''
            return True
        except Exception as e:
            self.StrErr = str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False

