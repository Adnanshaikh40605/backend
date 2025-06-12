from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('railway/', views.railway_health, name='railway_health'),
    path('railway-html/', views.railway_health_html, name='railway_health_html'),
    path('detailed/', views.detailed_health, name='detailed_health'),
] 