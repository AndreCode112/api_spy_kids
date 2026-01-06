import sys
from Controller.infoOs import  DtoInfoDisp
from Controller.ServerApi import ServerRequestApi
from Controller.infoOs import ConsumersDisp
from Controller.logs import logs
from Controller.log_api import LogApi

def Send_offline_disp(signum, frame):
    try:
        instanceConsumersDisp: ConsumersDisp = ConsumersDisp(DtoInfoDisp)           
        if not instanceConsumersDisp.get_info():
            strErr = "Erro ao obter informações do dispositivo: " + instanceConsumersDisp.strErr    
            raise Exception(strErr)
        
        DtoInfoDisp.status = "offline"
        
        instanceServerRequestApi: ServerRequestApi = ServerRequestApi()
        if not instanceServerRequestApi._send_status_connected():
            strErr = "Erro ao enviar status offline: " + instanceServerRequestApi.strErr
            raise Exception(strErr)
        
        sys.exit(1)

    except Exception as e:
        strErr = "Erro ao enviar status offline: " + str(e)
        print(e)
        instanceLogApi: LogApi = LogApi()
        if not instanceLogApi.InsertLogServer(strErr):
            logs(strErr).log_messageTxt()
        sys.exit(1)

