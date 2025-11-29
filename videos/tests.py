# videos/tests.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Video, VideoGroup
from .services import VideoGroupingService


class VideoGroupingTestCase(TestCase):
    """Testes para lógica de agrupamento de vídeos"""
    
    def create_video(self, minutes_offset=0, duration_seconds=300):
        """Helper para criar vídeos de teste"""
        base_time = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        created_at = base_time + timedelta(minutes=minutes_offset)
        
        video = Video.objects.create(
            file='test_video.mp4',
            created_at=created_at,
            duration=timedelta(seconds=duration_seconds)
        )
        return video
    
    def test_first_video_creates_group(self):
        """Primeiro vídeo deve criar um novo grupo"""
        video = self.create_video()
        group = VideoGroupingService.process_video(video)
        
        self.assertIsNotNone(group)
        self.assertEqual(video.video_group, group)
        self.assertTrue(video.processed)
        self.assertEqual(group.videos.count(), 1)
    
    def test_close_videos_same_group(self):
        """Vídeos próximos (< 20min) devem ficar no mesmo grupo"""
        video1 = self.create_video(minutes_offset=0)
        video2 = self.create_video(minutes_offset=10)
        video3 = self.create_video(minutes_offset=18)
        
        group1 = VideoGroupingService.process_video(video1)
        group2 = VideoGroupingService.process_video(video2)
        group3 = VideoGroupingService.process_video(video3)
        
        self.assertEqual(group1.id, group2.id)
        self.assertEqual(group2.id, group3.id)
        self.assertEqual(group1.videos.count(), 3)
    
    def test_distant_videos_different_groups(self):
        """Vídeos distantes (> 20min) devem criar grupos separados"""
        video1 = self.create_video(minutes_offset=0)
        video2 = self.create_video(minutes_offset=30)  # 30 minutos depois
        
        group1 = VideoGroupingService.process_video(video1)
        group2 = VideoGroupingService.process_video(video2)
        
        self.assertNotEqual(group1.id, group2.id)
        self.assertEqual(group1.videos.count(), 1)
        self.assertEqual(group2.videos.count(), 1)
    
    def test_video_fills_gap(self):
        """Vídeo intermediário deve juntar ao grupo correto"""
        video1 = self.create_video(minutes_offset=0)
        video3 = self.create_video(minutes_offset=50)
        video2 = self.create_video(minutes_offset=25)  # Intermediário
        
        group1 = VideoGroupingService.process_video(video1)
        group3 = VideoGroupingService.process_video(video3)
        group2 = VideoGroupingService.process_video(video2)
        
        # Todos devem estar no mesmo grupo
        self.assertEqual(group1.id, group2.id)
        self.assertEqual(group2.id, group3.id)
        self.assertEqual(group1.videos.count(), 3)
    
    def test_group_respects_max_duration(self):
        """Grupo não deve ultrapassar 20 minutos de duração total"""
        # Cria 3 vídeos de 7 minutos cada (21 minutos total)
        video1 = self.create_video(minutes_offset=0, duration_seconds=420)  # 7min
        video2 = self.create_video(minutes_offset=5, duration_seconds=420)  # 7min
        video3 = self.create_video(minutes_offset=10, duration_seconds=420) # 7min
        
        group1 = VideoGroupingService.process_video(video1)
        group2 = VideoGroupingService.process_video(video2)
        group3 = VideoGroupingService.process_video(video3)
        
        # Primeiros dois vídeos no mesmo grupo (14 minutos)
        self.assertEqual(group1.id, group2.id)
        
        # Terceiro vídeo deve criar novo grupo (ultrapassaria 20min)
        self.assertNotEqual(group2.id, group3.id)
        
        # Verifica duração do primeiro grupo
        group1.refresh_from_db()
        self.assertEqual(group1.total_duration.total_seconds(), 840)  # 14 minutos
        
    def test_multiple_groups_by_duration_limit(self):
        """Múltiplos grupos devem ser criados quando atingir limite de duração"""
        # Cria 6 vídeos de 4 minutos cada, todos próximos no tempo
        videos = []
        for i in range(6):
            video = self.create_video(minutes_offset=i*2, duration_seconds=240)  # 4min cada
            videos.append(video)
        
        groups = []
        for video in videos:
            group = VideoGroupingService.process_video(video)
            groups.append(group)
        
        # Deve criar 2 grupos (cada um com 5 vídeos = 20min)
        unique_groups = set(g.id for g in groups)
        self.assertEqual(len(unique_groups), 2)
        
        # Verifica que cada grupo tem no máximo 20 minutos
        for group_id in unique_groups:
            group = VideoGroup.objects.get(id=group_id)
            self.assertLessEqual(group.total_duration.total_seconds(), 1200)  # <= 20min
        """Metadados do grupo devem ser atualizados corretamente"""
        video1 = self.create_video(minutes_offset=0, duration_seconds=300)
        video2 = self.create_video(minutes_offset=10, duration_seconds=240)
        
        group1 = VideoGroupingService.process_video(video1)
        group2 = VideoGroupingService.process_video(video2)
        
        # Recarrega o grupo do banco
        group = VideoGroup.objects.get(id=group1.id)
        
        # Verifica duração total
        expected_duration = timedelta(seconds=540)  # 300 + 240
        self.assertEqual(group.total_duration, expected_duration)
        
        # Verifica start e end time
        self.assertEqual(group.start_time, video1.created_at)
        self.assertEqual(group.end_time, video2.created_at)
    
    def test_multiple_groups_same_day(self):
        """Deve criar múltiplos grupos no mesmo dia com gaps grandes"""
        # Manhã
        video1 = self.create_video(minutes_offset=0)  # 10:00
        video2 = self.create_video(minutes_offset=15)  # 10:15
        
        # Tarde (4 horas depois)
        video3 = self.create_video(minutes_offset=240)  # 14:00
        video4 = self.create_video(minutes_offset=255)  # 14:15
        
        group1 = VideoGroupingService.process_video(video1)
        group2 = VideoGroupingService.process_video(video2)
        group3 = VideoGroupingService.process_video(video3)
        group4 = VideoGroupingService.process_video(video4)
        
        # Vídeos da manhã no mesmo grupo
        self.assertEqual(group1.id, group2.id)
        
        # Vídeos da tarde no mesmo grupo
        self.assertEqual(group3.id, group4.id)
        
        # Grupos diferentes entre manhã e tarde
        self.assertNotEqual(group1.id, group3.id)
        
        # Dois grupos com 2 vídeos cada
        self.assertEqual(VideoGroup.objects.count(), 2)
        self.assertEqual(group1.videos.count(), 2)
        self.assertEqual(group3.videos.count(), 2)