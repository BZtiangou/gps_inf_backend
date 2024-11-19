from rest_framework import serializers
from dict.models import WordEntry

class WordEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WordEntry
        fields = ['word', 'tag', 'translation']