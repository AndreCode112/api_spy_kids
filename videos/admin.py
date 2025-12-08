from django.contrib import admin
from .models import Device, Video, DeviceConfig


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
    is_online.boolean = True  # Adiciona ícone ✔/✘
    is_online.short_description = "Online?"



@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'duration',  'processed')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ("Informações do Vídeo", {
            "fields": ("file", "duration", "processed")
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


    