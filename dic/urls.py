# urls.py
from django.urls import path
from .views import GetWordInfoApi,RandomUnfamiliarWordApi,UpdateWordFamiliarityApi,RandomfamiliarWordApi

urlpatterns = [
    path('words/', GetWordInfoApi.as_view(), name='get-word-info'),
    path('unfamiliar/', RandomUnfamiliarWordApi.as_view(), name='random-unfamiliar-word'),
    path('updateword/', UpdateWordFamiliarityApi.as_view(), name='update-word-familiarity'),
    path('familiar/', RandomfamiliarWordApi.as_view(), name='random-familiar-word'),
]