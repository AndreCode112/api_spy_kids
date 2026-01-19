from datetime import timedelta
from django.utils import timezone
from videos.models import Device, Video
from rest_framework import status


class check_is_online:
    def __init__(self):
        self.strErr:str = ""
        self.status:bool

    def run(self) -> bool:
        try:
            ultimo_video = (
                Video.objects
                .order_by('-created_at')
                .only('created_at')
                .first()
            )

            if not ultimo_video:
                self.status = status.HTTP_200_OK
                return True
            
            diff = timezone.now() - ultimo_video.created_at
            is_online = diff <= timedelta(minutes=30)
            
            device = Device.objects.order_by('id').first()
            if device:
                device.is_online = True if is_online else False
                device.status = 'online' if is_online else 'offline'
                device.save()
                
            self.status = status.HTTP_200_OK 
            return True
            
        except Exception as e:
            self.strErr = "Erro ao verificar status do dispositivo: " + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False

