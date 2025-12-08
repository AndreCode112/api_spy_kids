

from django.http import HttpRequest
from rest_framework import status
from videos.models import Device


class DeviceType:
    def __init__(self):
        self.strErr: str = ''
        self.status: int
        self.response: dict = {}
    
    def device_type_create_update(self, request:HttpRequest) -> bool:
        try:
            data: dict = request.data
            hostname = data.get('hostname')
            ip_address = data.get('ip_address')
            device_name = data.get('device_name', 'Dispositivo')
            status_recebido = data.get('status', 'online')

            if not hostname or not ip_address:
                self.strErr = 'hostname e ip_address são obrigatórios'
                self.status = status.HTTP_400_BAD_REQUEST
                return False
            
            device, created = Device.objects.get_or_create(
                hostname=hostname,
                defaults={
                    'ip_address': ip_address,
                    'device_name': device_name
                }
            )

            device.ip_address = ip_address
            device.device_name = device_name
            if status_recebido in ['online', 'offline']:
                device.status = status_recebido
            
            device.is_online = (status_recebido == 'online')
            device.save()

            self.response = {
                'success': True,    
                'device_id': device.id,
                'created': created,
                'message': 'Status do dispositivo atualizado com sucesso'
            }

            self.strErr = ''
            self.status = status.HTTP_200_OK
            return True 
        
        
        except Exception as e:
            self.strErr = 'Erro interno no servidor: ' +  str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
        
