

import os
import signal
import sys
from comuns.params import Tparams
from Controller.infoOs import ConsumersDisp, DtoInfoDisp
from Controller.commandffmpeg import CommandFFMPEG
from Controller.ServerApi import ServerRequestApi
from Controller.Sendoffilinedisp import Send_offline_disp
from Controller.logs import logs
from Controller.log_api import LogApi
from time import sleep

if __name__ == "__main__":
    signal.signal(signal.SIGINT, Send_offline_disp)
    signal.signal(signal.SIGTERM, Send_offline_disp)


    try:
        instanceConsumersDisp: ConsumersDisp = ConsumersDisp(DtoInfoDisp)
        if not instanceConsumersDisp.get_info():
            raise Exception(instanceConsumersDisp.strErr)

        instanceServerRequestApi: ServerRequestApi = ServerRequestApi()
        if not instanceServerRequestApi._send_status_connected():
            raise Exception(instanceServerRequestApi.strErr)

        instanceCommandFFMPEG: CommandFFMPEG = CommandFFMPEG()
        if not instanceCommandFFMPEG.listar_dispositivos_audio():
            raise Exception(instanceCommandFFMPEG.strErr)

        if not instanceServerRequestApi._send_audio_config(
            instanceCommandFFMPEG.lista_audios
        ):
            raise Exception(instanceServerRequestApi.strErr)

        if not instanceServerRequestApi._getConfigServer():
            raise Exception(instanceServerRequestApi.strErr)

        while True:
            if not instanceCommandFFMPEG.capture_video():
                raise Exception(instanceCommandFFMPEG.strErr)

            #upload do servidor princiapl

            # if not instanceServerRequestApi._upload_video():
            #     raise Exception(instanceServerRequestApi.strErr)

            #upload do arquivo para server externo. 
            if not instanceServerRequestApi._upload_video_external_server():
                raise Exception(instanceServerRequestApi.strErr)

            sleep(3)

            if os.path.exists(Tparams.pathVideoUploadSave):
                os.remove(Tparams.pathVideoUploadSave)

    except Exception as e:
        mensagem_erro:str = f"Erro fatal na rotina de captura/envio de vídeo: {e}" 
        instanceLogApi: LogApi =  LogApi()
        if not instanceLogApi.InsertLogServer(mensagem_erro):
            logs(mensagem_erro).log_messageTxt()
        sys.exit(1)