from datetime import datetime
import os
from comuns.params import Tparams

class logs:
    def __init__(self, strErr: str = ''):
        self.strErr = strErr
        self.params = Tparams()
    
    def log_messageTxt(self):
        try:
            if not os.path.exists(self.params.pathFileLogs):
                os.makedirs(os.path.dirname(self.params.pathFileLogs), exist_ok=True)

            data_today= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.strErr = f"[{data_today}] - {self.strErr}"
            with open(self.params.pathFileLogs, 'a') as file:
                file.write(self.strErr + '\n')

            if os.path.exists(self.params.pathVideoUploadSave):
                os.remove(self.params.pathVideoUploadSave)

            self.strErr = ''
            
        except Exception as e:
            self.strErr = f"Erro ao gravar log em arquivo: {e}"
            print(self.strErr)