import json
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from videos.models import Video
from rest_framework import status


class editVideoTitle:
    def __init__(self):
        self.StrErr:str = ''
        self.response:dict = {}
        self.status:int
    def _edit_title(self, request: HttpRequest, video_id:int) -> bool:
        try:
            data = json.loads(request.body)
            new_title = data.get('title')
            
            video = get_object_or_404(Video, id=video_id)
            video.title = new_title
            video.save()
            
            self.response = {'status': 'success', 'title': video.title}
            self.status = status.HTTP_200_OK

            return True 
        except Exception as e:
            self.StrErr = str(e)
            self.response = {'status': 'error', 'message': str(e)},
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
