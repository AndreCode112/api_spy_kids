import requests
from comuns.params import Tparams 


class LogApi:
    def __init__(self):
        self.StrErr: str = ''
        self.Tparams: Tparams = Tparams()
    
    def InsertLogServer(self, mensagem:str) -> bool:
        try:
            payload = {
                "mensagemErro": mensagem,
                'type_user': 'app'
            }

            response = requests.post(self.Tparams.APIINSERTLOGONSERVER, data=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            
            
            if not result.get("Sucesso", False):
                self.StrErr = 'Ouve um erro ao tentar salvar o Log no servidor, cheque os logs do servidor'
                return False

            return True

        except Exception as e:
            self.StrErr = "Erro ao realizar a requisição de um log do app: " + str(e)
            return False
        except requests.exceptions.RequestException as e:
            self.StrErr = "Erro ao realizar a requisição de um log do app: " + str(e)
            return False
            