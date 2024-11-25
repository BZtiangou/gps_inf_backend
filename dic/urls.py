# urls.py
from django.urls import path
from .views import GetWordInfoApi

urlpatterns = [
    path('words/', GetWordInfoApi.as_view(), name='get-word-info'),
]