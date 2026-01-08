from django.db import models
from django.utils import timezone
from django.conf import settings
import os
import subprocess


# class Video(models.Model):
#     title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Título") # Novo
#     file = models.FileField(upload_to='videos/capturas/')
#     thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, null=True) # Novo
#     created_at = models.DateTimeField(default=timezone.now)
#     duration = models.DurationField()
#     processed = models.BooleanField(default=False)
    
#     class Meta:
#         ordering = ['-created_at']

#     def save(self, *args, **kwargs):
#         if not self.title:
#             self.title = f"Vídeo #{self.pk}" if self.pk else "Novo Vídeo"
            
#         super().save(*args, **kwargs)
        
#         # Gera thumbnail se não existir e o arquivo de vídeo existir
#         if self.file and not self.thumbnail:
#             self.generate_thumbnail()

#     def generate_thumbnail(self):
#         """Gera uma thumbnail usando FFmpeg"""
#         try:
#             video_path = self.file.path
#             base_name = os.path.basename(video_path)
#             thumb_name = os.path.splitext(base_name)[0] + '.jpg'
#             thumb_rel_path = os.path.join('videos', 'thumbnails', thumb_name)
#             thumb_full_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'thumbnails', thumb_name)

#             os.makedirs(os.path.dirname(thumb_full_path), exist_ok=True)

#             cmd = [
#                 'ffmpeg', '-y', '-i', video_path, 
#                 '-ss', '00:00:01.000', '-vframes', '1', 
#                 thumb_full_path
#             ]
#             subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#             # Salva o caminho no banco (sem chamar save() recursivamente)
#             self.thumbnail.name = thumb_rel_path
#             super().save(update_fields=['thumbnail'])
#         except Exception as e:
#             print(f"Erro ao gerar thumbnail: {e}")


class Video(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Título")
    file_Server = models.CharField(max_length=255, null=False, verbose_name="Nome do Arquivo no Servidor") 
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title if self.title else f"Vídeo #{self.pk}"


class ConfiguracaoParaCalculoGravacao(models.Model):
    tamanho_hd_gb = models.FloatField(default=10, verbose_name="Tamanho do HD (GB)")
    tamanho_video_mb = models.FloatField(default=13.1, verbose_name="Tamanho do Vídeo (MB)")
    duracao_video_min = models.FloatField(default=10, verbose_name="Duração do Vídeo (min)")

    hora_inicio = models.TimeField(verbose_name="Início da Gravação", default="08:30")
    hora_fim = models.TimeField(verbose_name="Fim da Gravação", default="20:00")

    def __str__(self):
        return f"Configuração (HD: {self.tamanho_hd_gb}GB | {self.hora_inicio} - {self.hora_fim})"


class CompiledVideo(models.Model):
    file = models.FileField(upload_to='videos/compilados/')
    created_at = models.DateTimeField(auto_now_add=True)
    source_videos = models.ManyToManyField(Video, related_name='compiled_in')
    total_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"Compilado {self.id} - {self.created_at}"


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
    
class Notification(models.Model):
    TYPES = (
        ('info', 'Informação'),
        ('success', 'Sucesso'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
    )

    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.notification_type}: {self.message}"
    

class Log(models.Model):
    CLIENT_CHOICES = (
        ('server', 'Server'),
        ('app', 'App'),
        ('server_ftp', 'Server_FTP'),
    )

    client = models.CharField(
        max_length=10,
        choices=CLIENT_CHOICES,
        help_text="Origem do erro: server ou app"
    )

    mensagem_erro = models.TextField(
        help_text="Descrição detalhada do erro"
    )

    data_erro = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Log de Erro"
        verbose_name_plural = "Logs de Erro"
        ordering = ['-data_erro']

    def __str__(self):
        return f"[{self.client.upper()}] {self.data_erro:%d/%m/%Y %H:%M}"