import socket
import os
from dto.infoDevice import DtoInfoDisp

class ConsumersDisp():
    def __init__(self, DtoInfoDisp: DtoInfoDisp):
        self.instanceInfoDisp:DtoInfoDisp = DtoInfoDisp
        self.strErr:str = '' 

    def get_info(self)-> bool:
        def getIpadress():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                self.instanceInfoDisp.ip_address = s.getsockname()[0]
                s.close()
            except Exception:
                self.instanceInfoDisp.ip_address = "127.0.0.1"

        try:
            self.instanceInfoDisp.hostname = socket.gethostname()
            self.instanceInfoDisp.device_name = os.getenv('COMPUTERNAME', 'Unknown Device')
            getIpadress()  
            self.instanceInfoDisp.status = "online"
            return True
        except Exception as e:
            self.strErr = 'Erro ao obter informações do dispositivo: ' + str(e)
            return False
    