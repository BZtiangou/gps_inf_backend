from .models import gps_cluster,bt_cluster
from sensor.models import LocationInf
from rest_framework import serializers

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationInf
        fields = [
            'longitude', 'latitude','label',
        ]
    longitude = serializers.FloatField(required=True)
    latitude = serializers.FloatField(required=True)
    label =  serializers.CharField(max_length=20, required=True)


class UpdateBTLabelSerializer(serializers.Serializer):
    class Meta:
        model = bt_cluster
        fields = [
            'bt_device',
            'label',
        ]
    bt_device = serializers.CharField(max_length=17, required=True)
    label = serializers.CharField(max_length=255, required=True)


class get_GpsclusterSerializers(serializers.ModelSerializer):
    class Meta:
        model = gps_cluster
        fields = [
            'username',
            'cluster_name',
            'latitude',
            'longitude',
            'timestamp',
        ]

class getBTlabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = bt_cluster
        fields = [
            'bt_device',
            'label',
        ]

