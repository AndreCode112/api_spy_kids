from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .Controller.open_video import ApiOpenVideo
from .Controller.api_video import ApiVideo
from .Controller.storage_server import storageServerApi
from .Controller.device_Info_Conected import deviceInfoConnectedApi
from .Controller.device_type import DeviceType
from .Controller.config_api_device import api_device_config
from .Controller.api_add_string_audio import api_add_string_audio
from .Controller.logs_notification import MensagensLogs
from .Controller.get_notifications import Getnotification, mark_all_read_notification
from .Controller.edit_title_video import editVideoTitle
from .Controller.dashboars_filter_videos import DashboardsFilterVideos
from .Controller.consumer_logs_dashboard import ConsumerDashboardLog
from .Controller.agendar_calcular_videos_in_hd import AgendarCalcularQtdVideosInHD

from .Dto.logDto import LogsDto
from .Dto.notifyDto import notifyDto


def custom_page_not_found_view(request, exception):
    return render(request, "videos/404.html", status=404)



@login_required(login_url='/login/')
def video_gallery(request):
    instanceDashboardsFilterVideos:DashboardsFilterVideos = DashboardsFilterVideos()
    if not instanceDashboardsFilterVideos._execute(request):
        mensagem_erro = instanceDashboardsFilterVideos.StrErr 
        instanceMensagensLogs = MensagensLogs()
        
        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Falha ao carregar o dashboard principal. Verifique os logs.', notifyDto.error):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr
        return JsonResponse({
            'message': mensagem_erro
        }, status=instanceDashboardsFilterVideos.status)

    return render(request, instanceDashboardsFilterVideos.route, instanceDashboardsFilterVideos.response)


@login_required(login_url='/login/')
def dashboard_logs(request):
    return render(request, 'videos/logs_dashboard.html')


@login_required(login_url='/login/')
@require_http_methods(["POST"])
def update_video_title(request, video_id):
    instanceeditVideoTitle: editVideoTitle =  editVideoTitle()
    if not instanceeditVideoTitle._edit_title(request, video_id):
        mensagem_erro = instanceeditVideoTitle.StrErr + ' ' + ' id_video: ' + video_id 
        instanceMensagensLogs = MensagensLogs()
        
        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Ocorreu um erro ao tentar editar o título do vídeo. Verifique o log para mais detalhes.', notifyDto.warning):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        return JsonResponse(instanceeditVideoTitle.response, instanceeditVideoTitle.status)

    return JsonResponse(instanceeditVideoTitle.response, instanceeditVideoTitle.status)
    

@login_required(login_url='/login/')
def stream_video(request, video_id):
    instanceApiOpenVideo: ApiOpenVideo = ApiOpenVideo()
    if not instanceApiOpenVideo.open_video(video_id):
        mensagem_erro = instanceApiOpenVideo.strErr + ' ' + ' id_video: ' + video_id 
        instanceMensagensLogs = MensagensLogs()
        
        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Falha ao executar o vídeo. Tente novamente mais tarde.', notifyDto.warning):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        return JsonResponse({
            'success': False,
            'message': mensagem_erro
        }, status=instanceApiOpenVideo.status)
    
    return instanceApiOpenVideo.response    


@login_required(login_url='/login/')
@require_http_methods(["GET"])
@api_view(['GET'])
def device_info_connected(request):
    instanceDeviceInfoConnectedApi: deviceInfoConnectedApi = deviceInfoConnectedApi()
    if not instanceDeviceInfoConnectedApi._GetDeviceInfo():
        mensagem_erro = instanceDeviceInfoConnectedApi.StrErr
        instanceMensagensLogs = MensagensLogs()
        
        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Não foi possível obter as informações do dispositivo conectado', notifyDto.error):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        return JsonResponse({
            'success': False,
            'message': mensagem_erro
        }, status=instanceDeviceInfoConnectedApi.status)
    
    return JsonResponse(instanceDeviceInfoConnectedApi.response, status=instanceDeviceInfoConnectedApi.status)


@login_required(login_url='/login/')
@require_http_methods(["GET"])
@api_view(['GET'])
def storage_info(request):
    instanceStorageServerApi: storageServerApi = storageServerApi()
    if not instanceStorageServerApi._GetStorageInfo():
        mensagem_erro = instanceStorageServerApi.StrErr
        instanceMensagensLogs = MensagensLogs()
        
        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Erro ao obter informações referentes ao armazenamento do servidor', notifyDto.error):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        return JsonResponse({
            'success': False,
            'message': instanceStorageServerApi.StrErr
        }, status=instanceStorageServerApi.status)
    
    return JsonResponse(instanceStorageServerApi.response, status=instanceStorageServerApi.status)


@login_required(login_url='/login/')
@require_http_methods(["DELETE"])
@api_view(['DELETE'])
def deleteVideoAPi(request, video_id):
    instanceApiVideo: ApiVideo = ApiVideo()
    if not instanceApiVideo._Delete(request, video_id):
        instanceMensagensLogs = MensagensLogs()

        mensagem_erro = instanceApiVideo.StrErr
        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Não foi possível Deletar o video com id: ' + video_id , notifyDto.error):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr


        return JsonResponse({
            'success': False,
            'message': mensagem_erro
        }, status=instanceApiVideo.status)
    
    return JsonResponse({
        'success': True,
        'message': 'Vídeo deletado com sucesso'
    }, status=instanceApiVideo.status)



@login_required(login_url='/login/')
def check_notifications(request):
    instanceGetNotification: Getnotification = Getnotification()
    if not instanceGetNotification.Get_notification():
        mensagem_erro = instanceGetNotification.StrErr
        instanceMensagensLogs = MensagensLogs()

        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr
   
           return JsonResponse({
            'success': False,
            'message': mensagem_erro
        }, status=instanceGetNotification.status)
           
    return JsonResponse(instanceGetNotification.response)



@require_http_methods(["POST"])
@api_view(['POST'])
def device_type_create_update(request):
    instanceDeviceType: DeviceType = DeviceType()
    if not instanceDeviceType.device_type_create_update(request):
        mensagem_erro = instanceDeviceType.strErr
        instanceMensagensLogs = MensagensLogs()
        
        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('não foi possivel definir status do dispositivo conectado.', notifyDto.error):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        return JsonResponse({
            'success': False,
            'message': mensagem_erro
        }, status=instanceDeviceType.status)
    
    return JsonResponse(instanceDeviceType.response, status=instanceDeviceType.status)



@require_http_methods(["GET"])
@api_view(['GET'])
def GetConfigDeviceApi(request, hostname):
    instanceApiDeviceConfig: api_device_config = api_device_config()
    if not instanceApiDeviceConfig.configure_device_api(hostname):
        instanceMensagensLogs = MensagensLogs()
        mensagem_erro = instanceApiDeviceConfig.strErr

        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Não foi possível recuperar as configurações do dispositivo. Verifique o log para mais detalhes.', notifyDto.error):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        
        return JsonResponse({
            'success': False,
            'message': mensagem_erro
        }, status=instanceApiDeviceConfig.status)
    
    return JsonResponse(instanceApiDeviceConfig.response, status=instanceApiDeviceConfig.status)
 




@require_http_methods(["POST"])
@api_view(['POST'])
def saveVideoAPi(request):
    instanceApiVideo: ApiVideo = ApiVideo()
    if not instanceApiVideo._Post(request):
        instanceMensagensLogs = MensagensLogs()
        mensagem_erro = instanceApiVideo.StrErr

        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Foi detectada uma tentativa falha de um dispositivo ao salvar um vídeo. Verifique o log para mais detalhes', notifyDto.warning):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr


        return JsonResponse({
            'success': False,
            'message': mensagem_erro
        }, status=instanceApiVideo.status)
    
    return JsonResponse({
        'success': True,
        'message': 'Vídeo salvo com sucesso'
    }, status=instanceApiVideo.status)



@require_http_methods(["POST"])
@api_view(['POST'])
def config_device_audio_api(request, hostname):
    instanceApiAddStringAudio: api_add_string_audio = api_add_string_audio()
    if not instanceApiAddStringAudio.add_string_audio_api(request, hostname):
        instanceMensagensLogs = MensagensLogs()
        mensagem_erro = instanceApiAddStringAudio.strErr

        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Foi detectada uma tentativa falha ao adicionar os áudios presentes no dispositivo. Verifique o log para mais detalhes', notifyDto.warning):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        return JsonResponse({
            'success': False,
            'message': mensagem_erro
        }, status=instanceApiAddStringAudio.status)
    
    return JsonResponse(instanceApiAddStringAudio.response, status=instanceApiAddStringAudio.status)
   




@login_required(login_url='/login/')
@require_http_methods(["POST"])
def mark_all_read(request):
    instance_mark_all_read_notification: mark_all_read_notification = mark_all_read_notification()
    if not instance_mark_all_read_notification.mark_all_notification():
        instanceMensagensLogs = MensagensLogs()
        mensagem_erro = instance_mark_all_read_notification.StrErr

        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Falha ao marcar todas as notificações como lidas. Consulte os logs para mais detalhes.', notifyDto.warning):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr
          
          
        return JsonResponse({
            'message': mensagem_erro
        }, status=instance_mark_all_read_notification.status)



    return JsonResponse(instance_mark_all_read_notification.response)



@login_required(login_url='/login/')
@require_http_methods(["POST"])
def api_agendar_calcular_qtd_videos_in_hd(request):
    instanceAgendarCalcularQtdVideosInHD: AgendarCalcularQtdVideosInHD =  AgendarCalcularQtdVideosInHD()
    if not instanceAgendarCalcularQtdVideosInHD.Execute(request):
        instanceMensagensLogs = MensagensLogs()
        mensagem_erro = instanceAgendarCalcularQtdVideosInHD.StrErr

        if not instanceMensagensLogs.execute_log_error(LogsDto.SERVER, mensagem_erro):
           mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

        if not instanceMensagensLogs.execute_notification('Não foi possível calcular quantos vídeos cabem no espaço disponível.', notifyDto.error):
            mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr
          
        return JsonResponse({
            'message': mensagem_erro
        }, status=instanceAgendarCalcularQtdVideosInHD.Status)
    
    return JsonResponse(instanceAgendarCalcularQtdVideosInHD.response)





@login_required(login_url='/login/')
@require_http_methods(["GET"])
def Get_consumer_logs(request):
    instanceConsumerDashboardLog:ConsumerDashboardLog = ConsumerDashboardLog()
    if not instanceConsumerDashboardLog._consumer(request):
        return JsonResponse({
            'message': instanceConsumerDashboardLog.StrErr
        }, status=instanceConsumerDashboardLog.status)
    
    return JsonResponse(instanceConsumerDashboardLog.response,  status=instanceConsumerDashboardLog.status)


@csrf_exempt
@require_http_methods(["POST"])
def InsertLogsApiApp(request):
    instanceMensagensLogs = MensagensLogs()
    mensagem_app = request.POST.get('mensagemErro', '') 
    mensagem_erro:str = ''

    if not mensagem_app:
        mensagem_erro = 'Falha ao recuperar a mensagem de erro do aplicativo'

    if not instanceMensagensLogs.execute_log_error(LogsDto.APP, mensagem_erro):
        mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

    if not instanceMensagensLogs.execute_notification('Foi identificado um erro no fluxo de execução do aplicativo. Consulte os logs para mais detalhes', notifyDto.warning):
        mensagem_erro +=  ' - ' + instanceMensagensLogs.strErr

    if mensagem_erro:
        return JsonResponse({'Sucesso': False, 'mensagem': mensagem_erro})

    return JsonResponse({'Sucesso': True, 'mensagem': ''})