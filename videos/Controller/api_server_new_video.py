from rest_framework import status
from django.http import HttpRequest
from videos.models import Video
from datetime import timedelta
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

            self.strErr = ''
            self.status = status.HTTP_200_OK
            return True
        
        except Exception as e:
            self.strErr = "Erro ao tentar realizar o upload do video na nova api de upload: " + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False