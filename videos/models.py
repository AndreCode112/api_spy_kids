from django.db import models
from django.utils import timezone

class Video(models.Model):
    file = models.FileField(upload_to='videos/capturas/')
    created_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()
    processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    


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
    is_online = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    class Meta:
        ordering = ['-last_seen']

    
    def __str__(self):
        return self.hostname
    

class DeviceConfigAudio(models.Model):
    hostname = models.ForeignKey(
        Device,
        to_field='hostname',
        on_delete=models.CASCADE,
        related_name='audios'
    )

    audio = models.CharField(
        max_length=255,
        help_text="Nome do arquivo ou string de configuração do áudio."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['hostname', 'created_at']
        verbose_name = "Áudio do dispositivo"
        verbose_name_plural = "Áudios dos dispositivos"

    def __str__(self):
        return self.audio



class DeviceConfig(models.Model):
    hostname = models.OneToOneField(
        Device,
        to_field='hostname',
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='config'
    )

    tempo = models.PositiveIntegerField(
        default=10,
        help_text="Tempo em segundos para execução de comandos."
    )

    audio = models.ForeignKey(
        DeviceConfigAudio,
        on_delete=models.CASCADE,
        related_name='audios'
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuração de {self.hostname.hostname}"