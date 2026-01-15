from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework import status
from videos.models import Video
from datetime import timedelta

from .logs_notification import MensagensLogs
from videos.Dto.notifyDto import notifyDto
from videos.Dto.logDto import LogsDto
import requests
from django.http import StreamingHttpResponse
from django.conf import settings

class ApiVideo:
    def __init__(self):
        self.StrErr: str = ''
        self.status: int 
        self.response:dict = {}

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
        
    def _Delete(self, video_id):
        """API para deletar vídeo"""
        try:
            video = get_object_or_404(Video, id=video_id)

            url_request =video.url_php_server + 'api_deletar_video.php'

            headers = {
                'Referer': settings.DOMAIN,
                'User-Agent': 'DjangoBackend/1.0'
            }
            
            params = {'file': video.file_Server}
            
            resp = requests.delete(url_request, params=params, headers=headers)
            
            if not resp.status_code == 200:
                self.StrErr ="erro ao tentar realizar a request para deletar o video selecionado"
                self.status =  status.HTTP_400_BAD_REQUEST
                return False

            
            if video.file:
                video.file.delete()
                
            video.delete()

            self.status = status.HTTP_200_OK
            self.StrErr = ''
            return True
        except Exception as e:
            self.StrErr = "Erro ao tentar deletar o video: " + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
        
        except Video.DoesNotExist:
            self.StrErr = "Video não encontrado na base do servidor"
            self.status = status.HTTP_404_NOT_FOUND
            return False
        
    def stream_generator_api_download_video(self, request):
        try:
            for chunk in request.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        except Exception as e:
            self.StrErr = "Erro durante stream: {e}" 

    def _downloadVideo(self, video_id:int):
        try:
            video = get_object_or_404(Video, id=video_id)
            php_api_url = video.url_php_server + 'api_download_videos.php'  

            headers = {
                'Referer': settings.DOMAIN, # Certifique-se que settings.DOMAIN está correto
                'User-Agent': 'DjangoBackend/1.0'
            }
            
            filename_app:str = video.file_Server

            params = {
                'file': filename_app
            }
            
            resp_externa = requests.get(php_api_url, 
                                   params=params,
                                   headers=headers,
                                   stream=True, 
                                   timeout=10)

            if resp_externa.status_code != 200 and resp_externa.status_code != 206:
                self.StrErr = f"Erro no servidor de arquivos: {resp_externa.status_code}"
                self.status = status.HTTP_400_BAD_REQUEST
                return False                

            content_type = resp_externa.headers.get('Content-Type', 'application/octet-stream')
            
            response = StreamingHttpResponse(
                self.stream_generator_api_download_video(resp_externa), 
                content_type=content_type
            )
            
            response['Content-Disposition'] = f'attachment; filename="{video.file_Server}"'
            
            if 'Content-Length' in resp_externa.headers:
                response['Content-Length'] = resp_externa.headers['Content-Length']

            self.response = response
            self.status = status.HTTP_200_OK
            
            return True

        except requests.exceptions.RequestException as e:
            self.StrErr = f"O servidor de arquivos está indisponível: {e}"
            self.status = status.HTTP_503_SERVICE_UNAVAILABLE
            return False
        
        except Video.DoesNotExist:
            self.StrErr = "Video não encontrado na base do servidor"
            self.status = status.HTTP_404_NOT_FOUND
            return False