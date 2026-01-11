# cs2_stats/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.player_search, name='player_search'),
    path('player/<str:steam_id>/', views.player_profile, name='player_profile'),
]