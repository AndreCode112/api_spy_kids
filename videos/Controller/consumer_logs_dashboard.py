
from django.http import HttpRequest
from videos.models import Log
from django.db.models import Q
from rest_framework import status
from django.utils import timezone

class ConsumerDashboardLog:
    def __init__(self):
        self.StrErr:str = ''
        self.status: int
        self.response:dict = {}

    def _consumer(self, request: HttpRequest) -> bool:
        try:
            search = request.GET.get('search', '')
            client = request.GET.get('client', 'all')
            limit = request.GET.get('limit', '100') 
            
            logs = Log.objects.all()

            if client != 'all':
                logs = logs.filter(client=client)
            
            if search:
                logs = logs.filter(
                    Q(mensagem_erro__icontains=search) | 
                    Q(client__icontains=search)
                )

            if limit != 'all':
                try:
                    limit_int = int(limit)
                    logs = logs[:limit_int]
                except ValueError:
                    logs = logs[:100] 
            
            
            data = []
            for log in logs:
                data.append({
                    'id': log.id,
                    'client': log.client,
                    'mensagem': log.mensagem_erro,
                    'data': timezone.localtime(log.data_erro).strftime('%d/%m/%Y'),
                    'hora': timezone.localtime(log.data_erro).strftime('%H:%M:%S'),
                    'badge_color': 'bg-slate-700' if log.client == 'server' else 'bg-neutral-500',
                    'border_color': 'border-slate-700' if log.client == 'server' else 'border-neutral-500',
                })
            
            self.response = {'logs': data}
            self.status = status.HTTP_200_OK
            return True

        except Exception as e:
            self.StrErr = 'Erro ao obter consumers do dashboard de logs: ' + str(e)
            self.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return False