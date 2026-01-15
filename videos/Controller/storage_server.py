import os
from rest_framework import status
import subprocess

class storageServerApi:
    def __init__(self):
        self.StrErr: str = ''
        self.status: int = 200
        self.response: dict = {}

    def _get_directory_size(self, start_path):
        """Calcula tamanho da pasta videos recursivamente"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        try:
                            total_size += os.path.getsize(fp)
                        except Exception:
                            continue
        except Exception:
            return 0
        return total_size

    def _GetStorageInfo(self) -> bool:
        try:
            TOTAL_QUOTA_GB = 5
            
            cmd = "du -s -B 1 /tmp ~/.[!.]* ~/* | awk '{s+=$1}END{print s}'"
            
            try:
                result = subprocess.check_output(cmd, shell=True, text=True)
                used_bytes = int(result.strip())
            except Exception as e:
                self.StrErr = f"Erro ao calcular uso via shell: {e}"
                used_bytes = 0

            gib_divisor = 1024 ** 3
            used_gb = used_bytes / gib_divisor
            
            total_gb = TOTAL_QUOTA_GB
            
            free_gb = total_gb - used_gb
            
            percent_used = (used_gb / total_gb) * 100 if total_gb > 0 else 0.0

            videos_path = os.path.join(os.getcwd(), 'videos')
            videos_size = 0
            
            if os.path.exists(videos_path):
                videos_size = self._get_directory_size(videos_path)
                
            videos_size_gb = videos_size / gib_divisor
            
            self.response = {
                'success': True,
                'storage': {
                    'environment': 'PythonAnywhere (512MB Plan)',
                    'total_quota_gb': round(total_gb, 3),
                    'used_gb': round(used_gb, 3),
                    'free_gb': round(free_gb, 3),
                    'percent_used': round(percent_used, 1),
                    'videos_size_gb': round(videos_size_gb, 3),
                }
            }

            self.status = status.HTTP_200_OK
            self.StrErr = ''
            return True

        except Exception as e:
            self.StrErr = f"Erro crítico no storage info: {str(e)}"
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR    
            return False