from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PoseSource
from .serializers import PoseSourceSerializer
from rest_framework.permissions import IsAuthenticated
class PoseSourceUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = PoseSourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PoseSourceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = PoseSource.objects.filter(username=request.user)  # 过滤当前用户的视频
        serializer = PoseSourceSerializer(queryset, many=True)
        return Response(serializer.data)