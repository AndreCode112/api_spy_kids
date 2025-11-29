# videos/urls.py - Adicione estas URLs às existentes

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VideoViewSet, VideoGroupViewSet,
    CustomLoginView, video_gallery, delete_video, stream_video, storage_info, device_info_current, heartbeat
)
from django.contrib.auth.views import LogoutView

router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'groups', VideoGroupViewSet, basename='videogroup')

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # Autenticação
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('storage/info/',storage_info, name='storage_info'),
    path('device/info/', device_info_current, name='device_info_current'),
    path('api/devices/heartbeat/', heartbeat , name='device_heartbeat'),

    # Interface de visualização
    path('', video_gallery, name='video_gallery'),
    path('video/<int:video_id>/delete/', delete_video, name='delete_video'),
    path('video/<int:video_id>/stream/', stream_video, name='stream_video'),
    
]