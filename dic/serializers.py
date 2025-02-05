from rest_framework import serializers
from dic.models import WordEntry

class WordEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WordEntry
        fields = ['id','word', 'tag', 'translation']