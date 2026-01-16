from django.http import HttpRequest
from videos.models import Video
from itertools import groupby
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from rest_framework import status
from django.template.loader import render_to_string

class DashboardsFilterVideos:
    def __init__(self):
        self.StrErr:str = ''
        self.response:dict = {}
        self.route: str = ''
        self.status:int = status.HTTP_200_OK
        self.update_videos:bool = False

    def _execute(self, request: HttpRequest):
        try:
            videos_qs = Video.objects.all().order_by('-created_at')

            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            mode = request.GET.get('mode')

            if start_date_str:
                start_date = parse_date(start_date_str)
                if start_date:
                    videos_qs = videos_qs.filter(created_at__date__gte=start_date)

            if end_date_str:
                end_date = parse_date(end_date_str)
                if end_date:
                    videos_qs = videos_qs.filter(created_at__date__lte=end_date)
            
            if mode == 'update':
                client_last_id = int(request.GET.get('last_id', 0))

                new_videos_qs = videos_qs.filter(id__gt=client_last_id)

                if not new_videos_qs.exists():
                     self.response = {'status': 'uptodate'}
                     self.status = status.HTTP_200_OK
                     self.update_videos = True
                     return True

                server_latest_id = new_videos_qs.first().id
                page_obj = new_videos_qs 

                history_groups = []
                for date, group in groupby(page_obj, key=lambda x: x.created_at.date()):
                    history_groups.append({
                        'date': date,
                        'videos': list(group)
                    })
                
                videos_json_data = []
                for video in page_obj:
                    videos_json_data.append({
                        'id': video.id,
                        'url': video.get_video_url(),
                        'title': video.title or f"Vídeo #{video.id}",
                        'date': video.created_at.strftime('%Y-%m-%d'),
                    })

                context_html = {
                    'history_groups': history_groups,
                    'user': request.user
                }

                html_content = render_to_string('videos/video_list.html', context_html, request=request)

                self.response = {
                    'status': 'updated',
                    'html': html_content,
                    'data': videos_json_data, 
                    'latest_id': server_latest_id
                }
                
                self.status = status.HTTP_200_OK
                self.update_videos = True 
                return True
            
            total_items = videos_qs.count() or 1
            paginator = Paginator(videos_qs, total_items) 
            
            page_number = 1
            page_obj = paginator.get_page(page_number)
            
            history_groups = []
            for date, group in groupby(page_obj, key=lambda x: x.created_at.date()):
                history_groups.append({'date': date, 'videos': list(group)})

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
            self.status = 500
            return False