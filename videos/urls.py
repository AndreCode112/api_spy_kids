from django.urls import path
from .views import (
     video_gallery, stream_video, storage_info, device_info_connected , device_type_create_update, saveVideoAPi,deleteVideoAPi,config_device_audio_api 
)
from django.contrib.auth.views import LogoutView
from .Controller.login_custom import CustomLoginView


urlpatterns = [
    path('', video_gallery, name='video_gallery'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'), 
    
    path('storage/info/',storage_info, name='storage_info'),
    path('device/info/', device_info_connected, name='device_info_current'),
    
    path('api/devices/status/', device_type_create_update , name='device_heartbeat'),
    path('api/video/upload/', saveVideoAPi , name='save_video_api'),
    path('api/config/device/<str:hostname>/', device_type_create_update , name='config_device_api'),
    path('api/config/device/<str:hostname>/audio/', config_device_audio_api , name='config_device_audio_api'),

    
    path('video/<int:video_id>/delete/', deleteVideoAPi , name='delete_video'),
    path('video/<int:video_id>/stream/', stream_video, name='stream_video'),
    
]


#rota para configuração de app:
  # 1-> tempo de captura
  # 2-> configuração audio
  # 3-> configuração video
  # 4-> configuração api
  # log de erros  