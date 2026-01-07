from videos.models import ConfiguracaoParaCalculoGravacao
import json
from django.http import HttpRequest
from rest_framework import status
from datetime import datetime, timedelta

class AgendarCalcularQtdVideosInHD:
    def __init__(self):
        self.StrErr:str = ''
        self.Status:int
        self.response:dict = {}

    def _calcular_tempo_hd(self, tamanho_hd_gb, tamanho_video_mb, duracao_video_min, horas_gravacao_por_dia):
        hd_mb = tamanho_hd_gb * 1024

        qtd_videos = hd_mb // tamanho_video_mb

        tempo_total_min = qtd_videos * duracao_video_min
        tempo_total_horas = tempo_total_min / 60

        dias = int(tempo_total_horas // horas_gravacao_por_dia) if  horas_gravacao_por_dia > 0 else 0 

        return {
            "videos": int(qtd_videos),
            "horas_totais": round(tempo_total_horas, 2),
            "dias": dias,
        }

    def Execute(self,request:HttpRequest) -> bool:
            try:
                data = json.loads(request.body)
                
                inicio_str = data.get('hora_inicio') 
                fim_str = data.get('hora_fim')    
                salvar_no_banco = data.get('salvar', False)  

                config, created = ConfiguracaoParaCalculoGravacao.objects.get_or_create(pk=1)

                if salvar_no_banco:
                    config.hora_inicio = inicio_str
                    config.hora_fim = fim_str
                    config.save()
                    mensagem = "Horário salvo e calculado!"
                else:
                    mensagem = "Simulação realizada (não salvo)."

                fmt = '%H:%M'
                t_inicio = datetime.strptime(inicio_str, fmt)
                t_fim = datetime.strptime(fim_str, fmt)

                diff = t_fim - t_inicio if t_fim >= t_inicio else (t_fim + timedelta(days=1)) - t_inicio

                horas_dia = diff.total_seconds() / 3600

                resultado = self._calcular_tempo_hd(
                    tamanho_hd_gb=config.tamanho_hd_gb,
                    tamanho_video_mb=config.tamanho_video_mb,
                    duracao_video_min=config.duracao_video_min,
                    horas_gravacao_por_dia=horas_dia
                )
                
                resultado['duracao_diaria'] = round(horas_dia, 2)
                resultado['mensagem'] = mensagem
                
                self.response = resultado
                self.Status =  status.HTTP_200_OK
                self.StrErr = ''
                return True

            except Exception as e:
                 self.StrErr = "Erro ao tentar realizar o calculo de Quantidade de videos que cabem no hd: " + str(e)
                 self.Status =  status.HTTP_500_INTERNAL_SERVER_ERROR
                 return False
            