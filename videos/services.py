# videos/services.py
from datetime import timedelta
from django.db.models import Q
from .models import Video, VideoGroup


class VideoGroupingService:
    """Serviço para agrupar vídeos baseado em proximidade temporal"""
    
    @staticmethod
    def find_compatible_group(video):
        """
        Encontra um grupo compatível para o vídeo baseado na data/hora.
        
        Regras:
        - Vídeos com gap menor que 20 MINUTOS são do mesmo grupo
        - Se gap for maior que 20 minutos, cria novo grupo
        - Grupo NÃO PODE ultrapassar 20 minutos de duração total
        """
        max_gap = timedelta(minutes=Video.get_max_gap_minutes())
        video_time = video.created_at
        
        # Busca grupos onde o vídeo pode se encaixar
        time_range_start = video_time - max_gap
        time_range_end = video_time + max_gap
        
        # Procura grupo que o vídeo se encaixe no intervalo
        compatible_groups = VideoGroup.objects.filter(
            Q(start_time__lte=video_time, end_time__gte=time_range_start) |
            Q(start_time__lte=time_range_end, end_time__gte=video_time)
        ).order_by('start_time')
        
        for group in compatible_groups:
            # PRIMEIRO: Verifica se o grupo pode receber mais vídeos (limite de 20min)
            if not group.can_add_video(video):
                continue
            
            # Verifica se não há gap muito grande com vídeos existentes do grupo
            group_videos = group.videos.all().order_by('created_at')
            
            if not group_videos.exists():
                return group
            
            # Verifica gap com o último vídeo do grupo
            last_video = group_videos.last()
            first_video = group_videos.first()
            
            gap_with_last = abs((video_time - last_video.created_at).total_seconds())
            gap_with_first = abs((video_time - first_video.created_at).total_seconds())
            
            if gap_with_last <= max_gap.total_seconds() or gap_with_first <= max_gap.total_seconds():
                # Verifica se não há gap grande entre vídeos consecutivos
                if VideoGroupingService._check_continuity(group_videos, video, max_gap):
                    return group
        
        return None
    
    @staticmethod
    def _check_continuity(group_videos, new_video, max_gap):
        """Verifica se adicionar o novo vídeo não quebra a continuidade do grupo"""
        all_videos = list(group_videos) + [new_video]
        all_videos.sort(key=lambda v: v.created_at)
        
        for i in range(len(all_videos) - 1):
            gap = all_videos[i + 1].created_at - all_videos[i].created_at
            if gap > max_gap:
                return False
        
        return True
    
    @staticmethod
    def create_group_for_video(video):
        """Cria um novo grupo para o vídeo"""
        group = VideoGroup.objects.create(
            start_time=video.created_at,
            end_time=video.created_at,
            total_duration=video.duration
        )
        return group
    
    @staticmethod
    def update_group_metadata(group):
        """Atualiza metadados do grupo após adicionar/remover vídeos"""
        videos = group.videos.all().order_by('created_at')
        
        if not videos.exists():
            group.delete()
            return None
        
        group.start_time = videos.first().created_at
        group.end_time = videos.last().created_at
        group.total_duration = sum(
            (v.duration for v in videos), 
            timedelta()
        )
        group.save()
        
        return group
    
    @staticmethod
    def process_video(video):
        """
        Processa um novo vídeo:
        1. Busca grupo compatível
        2. Se não encontrar, cria novo grupo
        3. Adiciona vídeo ao grupo
        4. Atualiza metadados do grupo
        """
        # Busca grupo compatível
        group = VideoGroupingService.find_compatible_group(video)
        
        # Se não encontrou, cria novo
        if not group:
            group = VideoGroupingService.create_group_for_video(video)
        
        # Adiciona vídeo ao grupo
        video.video_group = group
        video.processed = True
        video.save()
        
        # Atualiza metadados do grupo
        VideoGroupingService.update_group_metadata(group)
        
        return group