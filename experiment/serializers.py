from .models import experiment,exp_history
from rest_framework import serializers

class seeExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model=experiment
        fields = ['exp_name','description','start_time','end_time','gps_frequency','acc_frequency','bt_frequency','gyro_frequency']

class exp_historySerializer(serializers.ModelSerializer):
    class Meta:
        model=exp_history
        fields = ['exp_id','exp_name','username','description','join_time','exit_time']

class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = experiment
        fields = '__all__'  # 或者列出所有你想要包含的字段