from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.conf import settings
from .models import GeneratedImage
import os
import time
import json
from PIL import Image
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Variables globales pour le pipeline
pipe = None
device = "cpu"  # Default to CPU for Vercel compatibility

def can_generate_ai():
    """Vérifier si la génération IA est activée et possible"""
    return getattr(settings, 'ENABLE_AI_GENERATION', False)

def initialize_pipeline():
    """Initialiser le pipeline Stable Diffusion"""
    global pipe, device
    
    if not can_generate_ai():
        logger.warning("AI generation is disabled")
        return None
        
    if pipe is None:
        try:
            import torch
            from diffusers import StableDiffusionPipeline
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_id = "CompVis/stable-diffusion-v1-4"
            logger.info(f"Initialisation du pipeline Stable Diffusion sur {device}")
            
            if device == "cuda":
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id, 
                    torch_dtype=torch.float16,
                    safety_checker=None,
                    requires_safety_checker=False
                )
                pipe = pipe.to(device)
                pipe.enable_attention_slicing()
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

def create_demo_image(prompt):
    """Créer une image de démonstration quand l'IA n'est pas disponible"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Créer une image de démonstration
    img = Image.new('RGB', (512, 512), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Ajouter du texte
    try:
        # Essayer de charger une police
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Texte centré
    text_lines = [
        "🎨 Mode Démonstration",
        "",
        "Prompt:",
        f'"{prompt[:50]}{"..." if len(prompt) > 50 else ""}"',
        "",
        "L'IA n'est pas disponible",
        "sur cette instance"
    ]
    
    y_offset = 150
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (512 - text_width) // 2
        draw.text((x, y_offset), line, fill='#6c757d', font=font)
        y_offset += 35
    
    # Sauvegarder en bytes
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    
    return img_io

def home(request):
    """Vue principale avec le formulaire de génération"""
    recent_images = GeneratedImage.objects.all()[:6]
    return render(request, 'ai_generator/home.html', {
        'recent_images': recent_images,
        'device': device,
        'cuda_available': False,  # Always False on Vercel
        'ai_enabled': can_generate_ai(),
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
        
        start_time = time.time()
        logger.info(f"Génération d'image pour le prompt: {prompt}")
        
        if can_generate_ai():
            # Générer avec l'IA
            pipeline = initialize_pipeline()
            if pipeline is None:
                return JsonResponse({'error': 'Erreur lors de l\'initialisation du modèle'}, status=500)
            
            import torch
            with torch.no_grad():
                generator = torch.Generator(device=device).manual_seed(42)
                
                image = pipeline(
                    prompt,
                    num_inference_steps=20,
                    guidance_scale=7.5,
                    generator=generator,
                    height=512,
                    width=512
                ).images[0]
            
            # Sauvegarder l'image
            img_io = io.BytesIO()
            image.save(img_io, format='PNG', quality=95)
            img_io.seek(0)
        else:
            # Mode démonstration
            img_io = create_demo_image(prompt)
        
        generation_time = time.time() - start_time
        logger.info(f"Image générée en {generation_time:.2f} secondes")
        
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
            'prompt': prompt,
            'demo_mode': not can_generate_ai()
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ai_enabled'] = can_generate_ai()
        return context

def about(request):
    """Vue à propos"""
    return render(request, 'ai_generator/about.html', {
        'ai_enabled': can_generate_ai()
    })
