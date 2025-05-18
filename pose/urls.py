from django.urls import path
from .apis import PoseSourceUploadView,PoseSourceListView

urlpatterns = [
    path('upload/', PoseSourceUploadView.as_view(), name='pose_source_upload'),
    path('list/', PoseSourceListView.as_view(), name='pose_source_list'),
]
