from django.urls import path
from .views import ImagePredictAPIView

urlpatterns = [
    path('predict/', ImagePredictAPIView.as_view(), name='image-predict'),
]