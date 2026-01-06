from django.conf import settings
import os
import shutil
from rest_framework import status

class storageServerApi:
    def __init__(self):
        self.StrErr: str = ''
        self.status: int = 200
        self.response: dict = {}

    def _get_directory_size(self, start_path):
        """
        Função auxiliar para calcular tamanho de uma pasta recursivamente.
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        try:
                            total_size += os.path.getsize(fp)
                        except (OSError, PermissionError):
                            continue
        except Exception:
            return 0
        return total_size

    def _GetStorageInfo(self) -> bool:
        try:
            system_root = os.path.abspath(os.sep)
            
            total, used, free = shutil.disk_usage(system_root)
            
            gib_divisor = 1024 ** 3
            total_gb = total / gib_divisor
            used_gb = used / gib_divisor
            free_gb = free / gib_divisor
            
            percent_used = (used / total) * 100 if total > 0 else 0.0
            
            current_project_path = os.getcwd()
            videos_path = os.path.join(current_project_path, 'videos')
            
            videos_size = 0
            if os.path.exists(videos_path):
                videos_size = self._get_directory_size(videos_path)
                
            videos_size_gb = videos_size / gib_divisor
            
            self.response = {
                'success': True,
                'storage': {
                    'path_checked': system_root,     
                    'videos_path': videos_path,
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
            self.StrErr = f"Erro ao obter dados de armazenamento: {str(e)}"
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR    
            return False