from django.urls import path
from . import views

app_name = 'ai_generator'

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate_image, name='generate_image'),
    path('gallery/', views.ImageGalleryView.as_view(), name='gallery'),
    path('about/', views.about, name='about'),
]