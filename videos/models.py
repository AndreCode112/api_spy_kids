from django.db import models
from django.utils import timezone

class Video(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Título")
   
    file_Server = models.CharField(max_length=255, null=False, verbose_name="Nome do Arquivo no Servidor") 
    url_php_server = models.URLField(default='https://rcamgeo.com.br/api/') 

    created_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title if self.title else f"Vídeo #{self.pk}"
    
            
    def get_video_url(self):
        base_url = "https://rcamgeo.com.br/api/api_get_videos.php"
        return f"{base_url}?file={self.file_Server}"


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