import requests
from django.http import StreamingHttpResponse
from django.conf import settings
from datetime import datetime
from stream_zip import stream_zip, ZIP_64
import json
from videos.models import Video 
from django.http import HttpRequest
from rest_framework import status


class multipleDownloadVideos:
    def __init__(self):
        self.strErr:str =''
        self.status:int
        self.response:dict = {}
    
    def zipped_files_generator(self, video_ids):
        videos = Video.objects.filter(id__in=video_ids)
        for video in videos:
            url_request = video.url_php_server + 'api_download_videos.php'
            params = {'file': video.file_Server}
            headers = {'Referer': settings.DOMAIN, 'User-Agent': 'DjangoBackend/1.0'}
            
            try:
                r = requests.get(url_request, params=params, headers=headers, stream=True, timeout=15)
                
                if r.status_code == 200:
                    filename = f"{video.title or video.id}.mp4".replace('/', '_').replace('\\', '_')
                    
                    yield (
                        filename, 
                        datetime.now(), 
                        0o600, 
                        ZIP_64, 
                        r.iter_content(chunk_size=8192) 
                    )
            except Exception:
                continue

    def downloadListVideos(self, request:HttpRequest) -> bool:
        try:
            video_ids_str = request.POST.get('ids', '[]')
            video_ids = json.loads(video_ids_str)
            
            if not video_ids:
                self.strErr = 'Nenhum vídeo foi selecionado para download'
                self.status = status.HTTP_400_BAD_REQUEST
                return False
            
            self.response = StreamingHttpResponse(
                stream_zip(self.zipped_files_generator(video_ids)), 
                content_type='application/zip'
            )
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            self.response['Content-Disposition'] = f'attachment; filename="videos_spykids_{timestamp}.zip"'
            
            self.strErr =''
            self.status = status.HTTP_200_OK
            
            return True
        
        except Exception as e:
            self.strErr = "foi detectado um erro ao tentar zipar os arquivos para download: " + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR    
            return False