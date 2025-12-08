from django.conf import settings
import os
import shutil
from rest_framework import status

class storageServerApi:
    def __init__(self):
        self.StrErr: str = ''
        self.status: int = 200
        self.response: dict = {}

    def _GetStorageInfo(self) -> bool:
        try:
            media_path = settings.MEDIA_ROOT
            total, used, free = shutil.disk_usage(media_path)
            
            total_gb = total / (1024 ** 3)
            used_gb = used / (1024 ** 3)
            free_gb = free / (1024 ** 3)
            
            percent_used = (used / total) * 100 if total else 0.0
            
            videos_size = 0
            videos_path = os.path.join(media_path, 'videos')
            
            if os.path.exists(videos_path):
                for dirpath, dirnames, filenames in os.walk(videos_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.isfile(filepath):
                            videos_size += os.path.getsize(filepath)
            
            videos_size_gb = videos_size / (1024 ** 3)
            
            self.response ={
                'success': True,
                'storage': {
                    'total_gb': round(total_gb, 2),
                    'used_gb': round(used_gb, 2),
                    'free_gb': round(free_gb, 2),
                    'percent_used': round(percent_used, 2),
                    'videos_size_gb': round(videos_size_gb, 2),
                }
            }

            self.status = status.HTTP_200_OK
            self.StrErr = ''
            return True
        except Exception as e:
            self.StrErr = str(e)
            self.status =  status.HTTP_500_INTERNAL_SERVER_ERROR   
            return False