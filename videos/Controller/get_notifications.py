from videos.models import Notification
from rest_framework import status
from django.utils import timezone

class Getnotification:
    def __init__(self):
        self.StrErr: str = ''
        self.response: dict = {}
        self.status:int

    def Get_notification(self) -> bool:
        try:
            unread_notifications = Notification.objects.filter(is_read=False)
        
            data = []
            for notif in unread_notifications:
                data.append({
                    'id': notif.id,
                    'message': notif.message,
                    'type': notif.notification_type,
                    'timestamp': timezone.localtime(notif.created_at).strftime('%H:%M')
                })
                

            self.response = {'notifications': data}
            self.status = status.HTTP_200_OK 
            self.StrErr = ''
            return True 
        
        except Exception as e:
            self.StrErr =  'Erro ao tentar obter as novas notificações: ' + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False   
        

class mark_all_read_notification:
    def __init__(self):
        self.StrErr:str = ''
        self.status: int
        self.response:dict = {}

    def mark_all_notification(self) -> bool:
        try:
            Notification.objects.filter(is_read=False).update(is_read=True)
            self.response = {'status': 'success'}
            self.status = status.HTTP_200_OK
            self.StrErr = ''
            return True
        except Exception as e:
            self.StrErr = 'Erro ao marcar todas as notifciações: ' + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False
    