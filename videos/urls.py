from django.urls import path
from .views import (
     video_gallery, stream_video, storage_info, device_info_connected , device_type_create_update, saveVideoAPi,deleteVideoAPi,config_device_audio_api, GetConfigDeviceApi, update_video_title, check_notifications, Get_consumer_logs, dashboard_logs, mark_all_read, InsertLogsApiApp
)
from django.contrib.auth.views import LogoutView
from .Controller.login_custom import CustomLoginView


urlpatterns = [
    path('', video_gallery, name='video_gallery'),
    path('logs/', dashboard_logs, name='log_dashboard'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'), 
    
    path('storage/info/',storage_info, name='storage_info'),
    path('device/info/', device_info_connected, name='device_info_current'),
    
    path('video/<int:video_id>/delete/', deleteVideoAPi , name='delete_video'),
    path('video/<int:video_id>/stream/', stream_video, name='stream_video'),
    path('video/<int:video_id>/update_title/', update_video_title, name='update_video_title'),

    path('api/devices/status/', device_type_create_update , name='device_heartbeat'),
    path('api/video/upload/', saveVideoAPi , name='save_video_api'),
    path('api/config/device/<str:hostname>/', GetConfigDeviceApi , name='config_device_api'),
    path('api/config/device/audio/<str:hostname>/', config_device_audio_api , name='config_device_audio_api'),
    path('api/notifications/check/', check_notifications, name='check_notifications'),
    path('api/notifications/mark-read-all/', mark_all_read, name='mark_all_read'),
    path('api/logs/',InsertLogsApiApp, name='api_logs'),
    path('api/logs/list/', Get_consumer_logs, name='api_logs_list'),
]

handler404 = 'videos.views.custom_page_not_found_view'