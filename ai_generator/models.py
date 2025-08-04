from django.db import models
from django.utils import timezone
import os

def upload_to_generated_images(instance, filename):
    """Fonction pour définir le chemin d'upload des images générées"""
    return f'generated_images/{timezone.now().strftime("%Y/%m/%d")}/{filename}'

class GeneratedImage(models.Model):
    prompt = models.TextField(verbose_name="Prompt", help_text="Texte utilisé pour générer l'image")
    image = models.ImageField(upload_to=upload_to_generated_images, verbose_name="Image générée")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    generation_time = models.FloatField(null=True, blank=True, verbose_name="Temps de génération (secondes)")
    
    class Meta:
        verbose_name = "Image générée"
        verbose_name_plural = "Images générées"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Image pour: {self.prompt[:50]}{'...' if len(self.prompt) > 50 else ''}"
    
    def delete(self, *args, **kwargs):
        """Supprimer le fichier image lors de la suppression du modèle"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
