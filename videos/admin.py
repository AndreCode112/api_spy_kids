from django.contrib import admin
from .models import Device


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
