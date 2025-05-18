from .models import AccelerometerInf,LocationInf,BlueToothInf,GyroInf,BatteryInf
from rest_framework import serializers

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationInf
        fields = ['longitude', 'latitude','timestamp','device','accuracy']

    longitude = serializers.FloatField(
        required=True
    )

    latitude = serializers.FloatField(
        required=True
    )

    accuracy = serializers.FloatField(
        required=True
    )

    device = serializers.CharField(
        max_length=150,
        required=False
    )

class BlueToothSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlueToothInf
        fields = ['connection_device','device','timestamp']
    
    connection_device = serializers.CharField(
        max_length=1500000,
        required=True
    )

    device = serializers.CharField(
        max_length=150,
        required=False
    )

    
class AccSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccelerometerInf
        fields = ['acc_x', 'acc_y','acc_z','timestamp','device']
    
    acc_x=serializers.FloatField(
        required=True
    )
    
    acc_y=serializers.FloatField(
        required=True
    )

    acc_z=serializers.FloatField(
        required=True
    )
    device = serializers.CharField(
        max_length=150,
        required=False
    )

class GyroSerializer(serializers.ModelSerializer):
    class Meta:
        model = GyroInf
        fields = ['x', 'y','z','timestamp','device']
    
    x=serializers.FloatField(
        required=True
    )
    
    y=serializers.FloatField(
        required=True
    )

    z=serializers.FloatField(
        required=True
    )
    device = serializers.CharField(
        max_length=150,
        required=False
    )

class BatterySerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryInf
        fields = ['battery_level', 'battery_status','timestamp','device']
    
    battery_level=serializers.FloatField(
        required=True
    )
    
    battery_status=serializers.CharField(
        max_length=150,
        required=True
    )
    device= serializers.CharField(required=False)

