# videos/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta


class VideoGroup(models.Model):
    """Grupo de vídeos consolidados"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_duration = models.DurationField(default=timedelta())
    consolidated_path = models.FileField(upload_to='videos/consolidated/', null=True, blank=True)
    
    MAX_DURATION_MINUTES = 20  # Duração máxima do grupo em minutos
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Grupo {self.id} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"
    
    def can_add_video(self, video):
        """Verifica se o vídeo pode ser adicionado sem exceder 20 minutos"""
        new_total_duration = self.total_duration + video.duration
        max_duration = timedelta(minutes=self.MAX_DURATION_MINUTES)
        return new_total_duration <= max_duration
    
    def get_remaining_duration(self):
        """Retorna quanto tempo ainda pode ser adicionado ao grupo"""
        max_duration = timedelta(minutes=self.MAX_DURATION_MINUTES)
        return max_duration - self.total_duration


class Video(models.Model):
    """Vídeo individual recebido"""
    file = models.FileField(upload_to='videos/raw/')
    created_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()
    video_group = models.ForeignKey(
        VideoGroup, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='videos'
    )
    processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Video {self.id} - {self.created_at.strftime('%d/%m/%Y %H:%M:%S')}"
    
    @staticmethod
    def get_max_gap_minutes():
        """Gap máximo em minutos para considerar vídeos do mesmo grupo"""
        return 20  # 20 minutos - vídeos com gap maior serão separados
    


class Device(models.Model):
    """Registra dispositivos que estão enviando vídeos"""
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    
    hostname = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=255, default='Dispositivo')
    ip_address = models.GenericIPAddressField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='online')
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    heartbeat_interval = models.IntegerField(default=30, help_text="Intervalo em segundos")
    
    class Meta:
        ordering = ['-last_seen']
    
    def __str__(self):
        return f"{self.hostname} - {self.status}"
    
    @property
    def is_online(self):
        """Verifica se o dispositivo está online"""
        from django.utils import timezone
        from datetime import timedelta
        
        time_threshold = timezone.now() - timedelta(seconds=self.heartbeat_interval * 2)
        return self.last_seen > time_threshold
    
    def update_status(self):
        """Atualiza status baseado no último heartbeat"""
        self.status = 'online' if self.is_online else 'offline'
        self.save()


class ScreenCapture(models.Model):
    """Grava capturas de tela/vídeo dos dispositivos"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='captures')
    video = models.ForeignKey('Video', on_delete=models.SET_NULL, null=True, blank=True)
    capture_data = models.FileField(upload_to='captures/%Y/%m/%d/%H/')
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True, blank=True)
    file_size_mb = models.FloatField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.device.hostname} - {self.timestamp}"