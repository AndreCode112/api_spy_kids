

from videos.models import Device
from rest_framework import status

class deviceInfoConnectedApi:
    def __init__(self):
        self.StrErr: str = ''
        self.status: int
        self.response: dict = {}

    def _GetDeviceInfo(self) -> bool:    
        try:
            device: Device= Device.objects.order_by('id').first()
            self.response = {
                'found': True,
                'device': {
                    'id': device.id,
                    'hostname': device.hostname,
                    'device_name': device.device_name,
                    'ip_address': device.ip_address,
                    'status': device.status,
                    'is_online': device.is_online,
                    'last_seen': device.last_seen.isoformat(),
                    'created_at': device.created_at.isoformat(),
                    'updated_at': device.updated_at.isoformat(),
                }
            } if len(device) else {} 

            self.status = status.HTTP_200_OK
            self.StrErr = ''
            return True

        except Exception as e:  
            self.StrErr = str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
        
        except Device.DoesNotExist:
            self.StrErr = 'Nenhum dispositivo registrado'
            self.status = status.HTTP_404_NOT_FOUND
            return False