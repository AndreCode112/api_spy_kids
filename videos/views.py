import json
import shutil
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Device, Video, VideoGroup
from .serializers import VideoSerializer, VideoGroupSerializer
from .services import VideoGroupingService
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import mimetypes
import os
from django.views.decorators.csrf import csrf_exempt



class VideoViewSet(viewsets.ModelViewSet):
    """
    API para gerenciar vídeos.
    
    POST /api/videos/ - Upload de novo vídeo
    GET /api/videos/ - Lista todos os vídeos
    GET /api/videos/{id}/ - Detalhes de um vídeo
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def create(self, request, *args, **kwargs):
        """Upload de vídeo com processamento automático de agrupamento"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Salva o vídeo
        video = serializer.save()
        
        # Processa agrupamento
        group = VideoGroupingService.process_video(video)
        
        # Retorna resposta com informações do grupo
        return Response({
            'video': VideoSerializer(video).data,
            'group': VideoGroupSerializer(group).data,
            'message': f'Vídeo adicionado ao grupo {group.id}'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def unprocessed(self, request):
        """Lista vídeos não processados"""
        videos = Video.objects.filter(processed=False)
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocessa agrupamento de um vídeo específico"""
        video = self.get_object()
        
        # Remove do grupo atual se existir
        old_group = video.video_group
        video.video_group = None
        video.processed = False
        video.save()
        
        # Atualiza grupo antigo
        if old_group:
            VideoGroupingService.update_group_metadata(old_group)
        
        # Reprocessa
        new_group = VideoGroupingService.process_video(video)
        
        return Response({
            'video': VideoSerializer(video).data,
            'new_group': VideoGroupSerializer(new_group).data,
            'message': 'Vídeo reprocessado com sucesso'
        })


class VideoGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para visualizar grupos de vídeos.
    
    GET /api/groups/ - Lista todos os grupos
    GET /api/groups/{id}/ - Detalhes de um grupo com seus vídeos
    """
    queryset = VideoGroup.objects.all()
    serializer_class = VideoGroupSerializer
    
    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """Lista grupos por data específica"""
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'error': 'Parâmetro "date" é obrigatório (formato: YYYY-MM-DD)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            groups = VideoGroup.objects.filter(start_time__date=date)
            serializer = self.get_serializer(groups, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Resumo estatístico de um grupo"""
        group = self.get_object()
        videos = group.videos.all()
        
        return Response({
            'group_id': group.id,
            'total_videos': videos.count(),
            'total_duration_seconds': group.total_duration.total_seconds(),
            'start_time': group.start_time,
            'end_time': group.end_time,
            'time_span_minutes': (group.end_time - group.start_time).total_seconds() / 60,
            'videos': VideoSerializer(videos, many=True).data
        })


class CustomLoginView(LoginView):
    """View customizada de login"""
    template_name = 'videos/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('video_gallery')


@login_required(login_url='/login/')
def video_gallery(request):
    """Página principal com galeria de vídeos estilo Netflix"""
    videos = Video.objects.all().order_by('-created_at')
    groups = VideoGroup.objects.all().order_by('-created_at')
    
    context = {
        'videos': videos,
        'groups': groups,
        'user': request.user
    }
    return render(request, 'videos/gallery.html', context)


@login_required(login_url='/login/')
@require_http_methods(["DELETE"])
def delete_video(request, video_id):
    """API para deletar vídeo"""
    try:
        video = get_object_or_404(Video, id=video_id)
  
        group = video.video_group
        
        if video.file:
            video.file.delete()

        video.delete()
        
        if group:
            from .services import VideoGroupingService
            VideoGroupingService.update_group_metadata(group)
        
        return JsonResponse({
            'success': True,
            'message': 'Vídeo deletado com sucesso'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required(login_url='/login/')
def stream_video(request, video_id):
    """Stream de vídeo com suporte a range requests"""
    video = get_object_or_404(Video, id=video_id)
    
    try:
        video_file = video.file.open('rb')
        content_type, _ = mimetypes.guess_type(video.file.name)
        
        response = FileResponse(video_file, content_type=content_type or 'video/mp4')
        response['Accept-Ranges'] = 'bytes'
        
        return response
    except Exception as e:
        raise Http404("Vídeo não encontrado")
    



@login_required(login_url='/login/')
def storage_info(request):
    """Retorna informações de armazenamento do servidor"""
    try:
        # Pega informações do disco onde está o MEDIA_ROOT
        from django.conf import settings
        media_path = settings.MEDIA_ROOT
        
        # Estatísticas do disco
        total, used, free = shutil.disk_usage(media_path)
        
        # Converte para GB
        total_gb = total / (1024 ** 3)
        used_gb = used / (1024 ** 3)
        free_gb = free / (1024 ** 3)
        
        # Calcula percentual usado
        percent_used = (used / total) * 100
        
        # Calcula espaço usado pelos vídeos especificamente
        videos_size = 0
        videos_path = os.path.join(media_path, 'videos')
        
        if os.path.exists(videos_path):
            for dirpath, dirnames, filenames in os.walk(videos_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.isfile(filepath):
                        videos_size += os.path.getsize(filepath)
        
        videos_size_gb = videos_size / (1024 ** 3)
        
        return JsonResponse({
            'success': True,
            'storage': {
                'total_gb': round(total_gb, 2),
                'used_gb': round(used_gb, 2),
                'free_gb': round(free_gb, 2),
                'percent_used': round(percent_used, 2),
                'videos_size_gb': round(videos_size_gb, 2),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    


@login_required(login_url='/login/')
def device_info_current(request):
    """
    Retorna informações sobre o primeiro dispositivo registrado no banco.
    Não utiliza mais o IP do cliente para busca.
    """
    try:
        # Obtém o primeiro device registrado
        device = Device.objects.order_by('id').first()

        if device:
            device.update_status()

            data = {
                'found': True,
                'device': {
                    'id': device.id,
                    'hostname': device.hostname,
                    'device_name': device.device_name,
                    'ip_address': device.ip_address,
                    'status': device.status,
                    'is_online': device.is_online,
                    'last_seen': device.last_seen.isoformat(),
                    'created_at': device.created_at.isoformat(),
                    'captures_count': device.captures.count(),
                    'last_capture': (
                        device.captures.first().timestamp.isoformat()
                        if device.captures.exists() else None
                    ),
                }
            }
        else:
            data = {
                'found': False,
                'message': 'Nenhum dispositivo registrado no sistema.'
            }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    
    
@csrf_exempt
def heartbeat(request):
    """Registra/atualiza heartbeat de um dispositivo"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)    
    try:
        data = json.loads(request.body.decode("utf-8"))  # <── AQUI

        hostname = data.get('hostname')
        ip_address = data.get('ip_address')
        device_name = data.get('device_name', 'Dispositivo')
        status_recebido = data.get('status', 'online')

        if not hostname or not ip_address:
            return JsonResponse(
                {'error': 'hostname e ip_address são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )

        device, created = Device.objects.get_or_create(
            hostname=hostname,
            defaults={
                'ip_address': ip_address,
                'device_name': device_name
            }
        )

        device.ip_address = ip_address
        device.device_name = device_name
        if status_recebido in ['online', 'offline']:
            device.status = status_recebido
        else:
            device.status = 'online'
        device.save()

        return JsonResponse({
            'success': True,
            'device_id': device.id,
            'message': 'Heartbeat registrado com sucesso',
            'next_heartbeat': device.heartbeat_interval
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)