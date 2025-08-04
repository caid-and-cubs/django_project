from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import GeneratedImage

@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ['prompt_preview', 'image_preview', 'created_at', 'generation_time']
    list_filter = ['created_at']
    search_fields = ['prompt']
    readonly_fields = ['image_preview', 'created_at', 'generation_time']
    ordering = ['-created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Information de l\'image', {
            'fields': ('prompt', 'image', 'image_preview')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'generation_time'),
            'classes': ('collapse',)
        }),
    )
    
    def prompt_preview(self, obj):
        """Afficher un aperçu du prompt"""
        if len(obj.prompt) > 100:
            return f"{obj.prompt[:100]}..."
        return obj.prompt
    prompt_preview.short_description = "Prompt"
    
    def image_preview(self, obj):
        """Afficher un aperçu de l'image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.image.url
            )
        return "Aucune image"
    image_preview.short_description = "Aperçu"
    
    def has_add_permission(self, request):
        """Empêcher l'ajout manuel d'images depuis l'admin"""
        return False
