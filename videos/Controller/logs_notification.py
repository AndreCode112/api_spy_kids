
from videos.models import Notification, Log


class MensagensLogs:
    def __init__(self):
         self.strErr:str = ''
    def execute_notification(self, menssagem:str, type_menssagem:str) -> bool:
        try:
            Notification.objects.create(
                message=menssagem,
                notification_type=type_menssagem
            )

        # ('info', 'Informação'),
        # ('success', 'Sucesso'),
        # ('warning', 'Aviso'),
        # ('error', 'Erro'),

            return True
        except Exception as e:
            self.strErr = 'Erro ao gravar Notificação: ' + str(e)
            return False
    def execute_log_error(self, clientType: str, mensagem:str) ->bool:
        try:
            Log.objects.create(
                client=clientType,
                mensagem_erro=mensagem
            )
            return True
        except Exception as e:
            self.strErr = 'Erro ao gravar o log: ' + e
            return False
            

        