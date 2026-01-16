from videos.models import Video
from django.conf import settings
import requests
from rest_framework import status
from django.http import HttpRequest
import json

class multipleDeleteApi:
    def __init__(self):
        self.status:int
        self.strErr:str = ''
        self.response:dict = {}
        self.errors:list = []
        
    def _Delete_multi_videos(self,request: HttpRequest)-> bool:
        try:
            success_count:int = 0
            data = json.loads(request.body)
            video_ids = data.get('ids', [])
            
            if len(video_ids) <=0:
                self.strErr = "Lista de videos para deletar esta vazia"
                self.status = status.HTTP_400_BAD_REQUEST
                return False

            videos = Video.objects.filter(id__in=video_ids)  

            for video in videos:
                url_request = video.url_php_server + 'api_deletar_video.php'
                headers = {'Referer': settings.DOMAIN, 'User-Agent': 'DjangoBackend/1.0'}
                params = {'file': video.file_Server}
                
                resp = requests.delete(url_request, params=params, headers=headers, timeout=5)
                
                if resp.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]:
                    video.delete()
                    success_count += 1
                else:
                    self.errors.append(f"Erro ID {video.id}: Status {resp.status_code}")
            
            self.response = {
                'deleted_count': success_count,
                'errors': self.errors,
                'total_requested': len(video_ids)
            }
            self.status = status.HTTP_200_OK
            self.StrErr =""
            return True

        except Exception as e:
            self.StrErr = f"Erro ao tentar excluir multiplos videos: {str(e)}"
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
