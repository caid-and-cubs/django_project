from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from .models import GeneratedImage
import torch
from diffusers import StableDiffusionPipeline
import io
import time
import json
from PIL import Image
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Variables globales pour le pipeline
pipe = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def initialize_pipeline():
    """Initialiser le pipeline Stable Diffusion"""
    global pipe
    if pipe is None:
        try:
            model_id = "CompVis/stable-diffusion-v1-4"
            logger.info(f"Initialisation du pipeline Stable Diffusion sur {device}")
            
            if device == "cuda":
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id, 
                    torch_dtype=torch.float16,
                    safety_checker=None,  # Désactiver pour éviter les erreurs
                    requires_safety_checker=False
                )
                pipe = pipe.to(device)
                pipe.enable_attention_slicing()  # Optimisation mémoire
            else:
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    safety_checker=None,
                    requires_safety_checker=False
                )
                pipe = pipe.to(device)
            
            logger.info("Pipeline initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du pipeline: {str(e)}")
            pipe = None
    return pipe

def home(request):
    """Vue principale avec le formulaire de génération"""
    recent_images = GeneratedImage.objects.all()[:6]  # Les 6 dernières images
    return render(request, 'ai_generator/home.html', {
        'recent_images': recent_images,
        'device': device,
        'cuda_available': torch.cuda.is_available()
    })

@csrf_exempt
def generate_image(request):
    """API pour générer une image à partir d'un prompt"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Récupérer le prompt
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return JsonResponse({'error': 'Le prompt ne peut pas être vide'}, status=400)
        
        if len(prompt) > 500:
            return JsonResponse({'error': 'Le prompt ne peut pas dépasser 500 caractères'}, status=400)
        
        # Initialiser le pipeline
        pipeline = initialize_pipeline()
        if pipeline is None:
            return JsonResponse({'error': 'Erreur lors de l\'initialisation du modèle'}, status=500)
        
        # Générer l'image
        start_time = time.time()
        logger.info(f"Génération d'image pour le prompt: {prompt}")
        
        with torch.no_grad():
            # Paramètres de génération
            generator = torch.Generator(device=device).manual_seed(42)  # Seed fixe pour la reproductibilité
            
            image = pipeline(
                prompt,
                num_inference_steps=20,  # Réduit pour accélérer
                guidance_scale=7.5,
                generator=generator,
                height=512,
                width=512
            ).images[0]
        
        generation_time = time.time() - start_time
        logger.info(f"Image générée en {generation_time:.2f} secondes")
        
        # Sauvegarder l'image
        img_io = io.BytesIO()
        image.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        # Créer le nom du fichier
        import uuid
        filename = f"generated_{uuid.uuid4().hex[:8]}.png"
        
        # Sauvegarder en base de données
        generated_image = GeneratedImage(
            prompt=prompt,
            generation_time=generation_time
        )
        generated_image.image.save(
            filename,
            ContentFile(img_io.getvalue()),
            save=True
        )
        
        return JsonResponse({
            'success': True,
            'image_url': generated_image.image.url,
            'generation_time': round(generation_time, 2),
            'prompt': prompt
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération: {str(e)}")
        return JsonResponse({'error': f'Erreur lors de la génération: {str(e)}'}, status=500)

class ImageGalleryView(ListView):
    """Vue pour afficher la galerie des images générées"""
    model = GeneratedImage
    template_name = 'ai_generator/gallery.html'
    context_object_name = 'images'
    paginate_by = 12
    
    def get_queryset(self):
        return GeneratedImage.objects.all().order_by('-created_at')

def about(request):
    """Vue à propos"""
    return render(request, 'ai_generator/about.html')
