from .models import Experiment,exp_history,Protocol, Survey, SurveyItem, Trigger
from rest_framework import serializers

class seeExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Experiment
        fields = ['exp_name','description','start_time','end_time','gps_frequency','acc_frequency','bt_frequency','gyro_frequency']

class exp_historySerializer(serializers.ModelSerializer):
    class Meta:
        model=exp_history
        fields = ['exp_id','exp_name','username','description','join_time','exit_time']

class ExperimentSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    class Meta:
        model = Experiment
        fields = '__all__'  

class SurveyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyItem
        fields = ["type", "label", "description", "question", "choices"]

class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = ["trigger_type", "regular_time_option", "specific_time"]

class SurveySerializer(serializers.ModelSerializer):
    items = SurveyItemSerializer(many=True)
    trigger = TriggerSerializer()

    class Meta:
        model = Survey
        fields = ["survey_name", "description", "trigger", "items"]

# 修改原有序列化器（serializers.py）
class ProtocolSerializer(serializers.ModelSerializer):
    surveys = SurveySerializer(many=True, required=False)
    protocol_id = serializers.IntegerField(source='id', read_only=True)  # 添加该字段

    class Meta:
        model = Protocol
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},  # 隐藏原始ID字段
            'creator': {'read_only': True}  # 自动填充创建者
        }

class ProtocolDetailSerializer(serializers.ModelSerializer):
    surveys = SurveySerializer(many=True)
    
    class Meta:
        model = Protocol
        # fields = [
        #     'id',
        #     'protocol_name',
        #     'creator',
        #     'gps_frequency',
        #     'bt_frequency',
        #     'surveys'  # 包含嵌套问卷数据
        # ]
        fields = '__all__'