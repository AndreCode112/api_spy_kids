from django.contrib import admin
from .models import Device, Video, DeviceConfig, Notification, DeviceConfigAudio, Log, ConfiguracaoParaCalculoGravacao




@admin.register(ConfiguracaoParaCalculoGravacao)
class ConfiguracaoParaCalculoGravacaoAdmin(admin.ModelAdmin):
    list_display = (
        "tamanho_hd_gb", 
        "tamanho_video_mb",
        "duracao_video_min", 
        "hora_inicio", 
        "hora_fim"
   )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'message',  
        'notification_type', 
        'is_read', 
        'created_at' 
    )


@admin.register(Log)
class Log(admin.ModelAdmin):
    list_display = (
    'client', 
    'mensagem_erro',
    'data_erro'
)



@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        'hostname',
        'device_name',
        'ip_address',
        'status',
        'is_online',
        'last_seen',
        'created_at',
    )
    
    list_filter = (
        'status',
        'created_at',
    )
    
    search_fields = (
        'hostname',
        'device_name',
        'ip_address',
    )
    
    readonly_fields = (
        'last_seen',
        'created_at',
        'status',
        'is_online',
    )

    ordering = ('-last_seen',)

    def save_model(self, request, obj, form, change):
        """Atualiza o status automaticamente ao salvar."""
        obj.update_status()
        super().save_model(request, obj, form, change)


    def is_online(self, obj):
        """Exibe status visual no admin."""
        return obj.is_online
    is_online.boolean = True
    is_online.short_description = "Online?"



@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'duration', 'url_php_server')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ("Informações do Vídeo", {
            "fields": ("file_Server", "duration", "url_php_server"),
        }),
        ("Datas", {
            "fields": ("created_at",),
        }),
    )


@admin.register(DeviceConfig)
class DeviceConfigAdmin(admin.ModelAdmin):
    list_display = (
        'hostname',
        'tempo',
        'audio',
        'updated_at',
    )

    list_filter = (
        'updated_at',
        'tempo',
    )

    search_fields = (
        'hostname__hostname',
        'audio',
    )

    readonly_fields = (
        'updated_at',
    )

    fieldsets = (
        ("Configuração do Dispositivo", {
            "fields": ("hostname", "tempo", "audio")
        }),
        ("Auditoria", {
            "fields": ("updated_at",),
            "classes": ("collapse",),
        }),
    )

    ordering = ('-updated_at',)



@admin.register(DeviceConfigAudio)
class DeviceConfigAudioAdmin(admin.ModelAdmin):
    list_display = (
        'hostname_display',
        'audio',
        'created_at',
    )

    list_filter = (
        'hostname',
        'created_at',
    )

    search_fields = (
        'hostname__hostname',
        'audio',
    )

    ordering = ('hostname__hostname', 'created_at')

    # Exibir o hostname real (string), não "object"
    def hostname_display(self, obj):
        return obj.hostname.hostname
    hostname_display.short_description = 'Hostname'



