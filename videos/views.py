from rest_framework.decorators import api_view
from .models import  Video
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from .Controller.open_video import ApiOpenVideo
from .Controller.api_video import ApiVideo
from .Controller.storage_server import storageServerApi
from .Controller.device_Info_Conected import deviceInfoConnectedApi
from .Controller.device_type import DeviceType
from .Controller.config_api_device import api_device_config
from .Controller.config_api_device import api_device_config




@login_required(login_url='/login/')
def video_gallery(request):
    videos = Video.objects.all().order_by('-created_at')
    
    context = {
        'videos': videos,
        'user': request.user
    }
    return render(request, 'videos/gallery.html', context)


@login_required(login_url='/login/')
def stream_video(request, video_id):
    instanceApiOpenVideo: ApiOpenVideo = ApiOpenVideo()
    if not instanceApiOpenVideo.open_video(video_id):
        return JsonResponse({
            'success': False,
            'message': instanceApiOpenVideo.strErr
        }, status=instanceApiOpenVideo.status)
    
    return instanceApiOpenVideo.response    





@login_required(login_url='/login/')
@require_http_methods(["GET"])
@api_view(['GET'])
def device_info_connected(request):
    instanceDeviceInfoConnectedApi: deviceInfoConnectedApi = deviceInfoConnectedApi()
    if not instanceDeviceInfoConnectedApi._GetDeviceInfo():
        return JsonResponse({
            'success': False,
            'message': instanceDeviceInfoConnectedApi.StrErr
        }, status=instanceDeviceInfoConnectedApi.status)
    
    return JsonResponse(instanceDeviceInfoConnectedApi.response, status=instanceDeviceInfoConnectedApi.status)




@login_required(login_url='/login/')
@require_http_methods(["GET"])
@api_view(['GET'])
def storage_info(request):
    instanceStorageServerApi: storageServerApi = storageServerApi()
    if not instanceStorageServerApi._GetStorageInfo():
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
        return JsonResponse({
            'success': False,
            'message': instanceApiVideo.StrErr
        }, status=instanceApiVideo.status)
    
    return JsonResponse({
        'success': True,
        'message': 'Vídeo deletado com sucesso'
    }, status=instanceApiVideo.status)





@require_http_methods(["POST"])
@api_view(['POST'])
def device_type_create_update(request):
    instanceDeviceType: DeviceType = DeviceType()
    if not instanceDeviceType.device_type_create_update(request):
        return JsonResponse({
            'success': False,
            'message': instanceDeviceType.strErr
        }, status=instanceDeviceType.status)
    
    return JsonResponse(instanceDeviceType.response, status=instanceDeviceType.status)



@require_http_methods(["GET"])
@api_view(['GET'])
def GetConfigDeviceApi(request, hostname):
    instanceApiDeviceConfig: api_device_config = api_device_config()
    if not instanceApiDeviceConfig.configure_device_api(hostname):
        return JsonResponse({
            'success': False,
            'message': instanceApiDeviceConfig.strErr
        }, status=instanceApiDeviceConfig.status)
    
    return JsonResponse(instanceApiDeviceConfig.response, status=instanceApiDeviceConfig.status)
 




@require_http_methods(["POST"])
@api_view(['POST'])
def saveVideoAPi(request):
    instanceApiVideo: ApiVideo = ApiVideo()
    if not instanceApiVideo._Post(request):
        return JsonResponse({
            'success': False,
            'message': instanceApiVideo.StrErr
        }, status=instanceApiVideo.status)
    
    return JsonResponse({
        'success': True,
        'message': 'Vídeo salvo com sucesso'
    }, status=instanceApiVideo.status)



@require_http_methods(["POST"])
@api_view(['POST'])
def config_device_audio_api(request, hostname):
    instanceApiDeviceConfigAudio: api_device_config = api_device_config()
    if not instanceApiDeviceConfigAudio.add_list_audios_device(request, hostname):
        return JsonResponse({
            'success': False,
            'message': instanceApiDeviceConfigAudio.strErr
        }, status=instanceApiDeviceConfigAudio.status)
    
    return JsonResponse(instanceApiDeviceConfigAudio.response, status=instanceApiDeviceConfigAudio.status)