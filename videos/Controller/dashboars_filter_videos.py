from django.http import HttpRequest
from videos.models import Video
from itertools import groupby
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from rest_framework import status

class DashboardsFilterVideos:
    def __init__(self):
        self.StrErr:str = ''
        self.response:dict = {}
        self.route: str = ''
        self.status:int
        self.update_videos:bool =False

    def _execute(self,request: HttpRequest):
        try:
            videos_qs = Video.objects.all().order_by('-created_at')

            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            check_update =  request.GET.get('check_update')

            if start_date_str:
                start_date = parse_date(start_date_str)
                if start_date:
                    videos_qs = videos_qs.filter(created_at__date__gte=start_date)

            if end_date_str:
                end_date = parse_date(end_date_str)
                if end_date:
                    videos_qs = videos_qs.filter(created_at__date__lte=end_date)
                    
            if check_update == 'true':
                latest_video = videos_qs.first()
                latest_id = latest_video.id if latest_video else 0
                self.response = {'latest_id': latest_id}
                self.status = status.HTTP_200_OK
                self.StrErr = ""
                self.update_videos = True
                return True
                
            paginator = Paginator(videos_qs, 20) 
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            history_groups = []
            for date, group in groupby(page_obj, key=lambda x: x.created_at.date()):
                history_groups.append({
                    'date': date,
                    'videos': list(group)
                })

            videos_json = []
            for video in page_obj:

                videos_json.append({
                    'id': video.id,
                    'url': video.get_video_url(),
                    'title': video.title or f"Vídeo #{video.id}",
                    'date': video.created_at.strftime('%Y-%m-%d'),
                })

            self.response = {
                'history_groups': history_groups,
                'videos_json': videos_json,
                'page_obj': page_obj,
                'user': request.user,
                'start_date_val': start_date_str, 
                'end_date_val': end_date_str,
            }

            self.route= 'videos/video_list.html' if request.headers.get('x-requested-with') == 'XMLHttpRequest' else 'videos/gallery.html' 
            self.status = status.HTTP_200_OK 
            return True
        except Exception as e:
            self.StrErr = 'Erro ao executar a rotina principal Dashboard: ' + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False