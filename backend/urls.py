"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.urls import path
def trigger_error(request):
    division_by_zero = 1 / 0
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('account.urls'), name='account'),  
    path('survey/', include('survey.urls'), name='survery'),
    path('exp/', include('experiment.urls'), name='experiment'),
    path('sensor/', include('sensor.urls'), name='sensor'),  
    path('analysis/', include('analysis.urls'), name='analysis'),  
    path('pose/', include('pose.urls'), name='pose'),  
    path('dic/', include('dic.urls'), name='dic'),  
    path('ad/', include('ad.urls'), name='ad'),  

    path('sentry-debug/', trigger_error),
]
