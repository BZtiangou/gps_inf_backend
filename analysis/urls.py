from django.urls import path
from .apis import updateLabelApi,get_gps_cluster,updateBTlabelApi,getBTLabelApi,adminGetBTClusterApi,adminGetGPSClusterApi
from .apis import  getGpsName
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


urlpatterns = [
    path("token_obtain/", TokenObtainPairView.as_view(), name="obtain"),
    path("token_refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("token_verify/", TokenVerifyView.as_view(), name="verify"),
    path("updateLabel/",updateLabelApi.as_view(),name="updateLabel"),
    path("get_gpscluster/",get_gps_cluster.as_view(),name="get_gps_cluster"),
    path("updateBTlabel/",updateBTlabelApi.as_view(),name="updateBTlabel"),
    path("getBTLabel/",getBTLabelApi.as_view(),name="getBTLabel"),
    path("getGpsName/",getGpsName.as_view(),name="getGpsName"),
    path("adminGetBTCluster/",adminGetBTClusterApi.as_view(),name="adminGetBTCluster"),
    path("adminGetGPSCluster/",adminGetGPSClusterApi.as_view(),name="adminGetGPSCluster"),
]
