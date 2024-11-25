# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dic.models import WordEntry
from .serializers import WordEntrySerializer

class GetWordInfoApi(APIView):
    permission_classes=[]
    def get(self, request):
        words = WordEntry.objects.all()
        serializer = WordEntrySerializer(words, many=True)
        return Response(serializer.data)