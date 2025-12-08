import mimetypes
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from videos.models import Video
from rest_framework import status

class ApiOpenVideo:
    def __init__(self):
        self.strErr:str = ''
        self.status:int
        self.response:dict = {}

    def open_video(self, video_id: int) -> bool:
        try:
            video = get_object_or_404(Video, id=video_id)
            video_file = video.file.open('rb')
            content_type, _ = mimetypes.guess_type(video.file.name)
            
            self.response = FileResponse(video_file, content_type=content_type or 'video/mp4')
            self.response['Accept-Ranges'] = 'bytes'
            
            self.strErr = ''
            self.status = status.HTTP_200_OK
            return True
    
        except Exception as e:
            self.strErr = 'Erro ao abrir o vídeo: ' + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
        
        except Video.DoesNotExist:
            self.strErr = 'Vídeo não encontrado.'
            self.status = status.HTTP_404_NOT_FOUND
            return False