from django.urls import path
from . import views

urlpatterns = [
    path('analytics/', views.analytics, name='analytics'),
    path('fetch/', views.fetch_weather, name='fetch_weather'),
]
