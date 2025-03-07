from .models import Experiment,exp_history,Protocol, Survey, SurveyItem, Trigger
from rest_framework import serializers
import re

class seeExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Experiment
        fields = ['exp_title','description','start_time','end_time','gps_frequency','acc_frequency','bt_frequency','gyro_frequency']

class exp_historySerializer(serializers.ModelSerializer):
    class Meta:
        model=exp_history
        fields = ['exp_id','exp_title','username','description','join_time','exit_time']

class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = '__all__'
    

class SurveyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyItem
        fields = ["type", "label", "description", "question", "choices"]
    def validate_question(self, value):
        """清洗问题中的转义字符"""
        cleaned = re.sub(r'[\n\t]+', ' ', value).strip()
        return cleaned if cleaned else value

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
class SurveyUpdateSerializer(serializers.Serializer):
    protocol_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    surveys = SurveySerializer(many=True)

    def validate_protocol_id(self, value):
        if not Protocol.objects.filter(pk=value).exists():
            raise serializers.ValidationError("协议不存在")
        return value

    def update(self, instance, validated_data):
        # 在实际项目中需要添加事务处理
        return self._handle_survey_update(instance, validated_data)

    def _handle_survey_update(self, protocol, data):
        # 删除原有问卷和关联数据
        Survey.objects.filter(protocol=protocol).delete()
        
        for survey_data in data.get('surveys', []):
            self._create_survey(protocol, survey_data)
        
        protocol.protocol_name = data.get('name', protocol.protocol_name)
        protocol.save()
        return protocol

    def _create_survey(self, protocol, survey_data):
        trigger_data = survey_data.pop('trigger')
        items_data = survey_data.pop('items')

        # 创建触发器
        trigger = Trigger.objects.create(**trigger_data)

        # 创建问卷
        survey = Survey.objects.create(
            protocol=protocol,
            trigger=trigger,
            **survey_data
        )

        # 创建问卷项
        for item_data in items_data:
            SurveyItem.objects.create(survey=survey, **item_data)

        return survey
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

# 先不动
class ProtocolListSerializer(serializers.ModelSerializer):
    surveys = SurveySerializer(many=True)
    
    class Meta:
        model = Protocol
        fields = [
            'id',
            'protocol_name',
            'creator',
            'gps_frequency',
            'bt_frequency',
            'surveys'  # 包含嵌套问卷数据
        ]
        # fields = '__all__'



# 实验部分
class UserExperimentSerializer(serializers.ModelSerializer):
    """
    用户实验列表序列化器
    """
    class Meta:
        model = Experiment
        # fields = ['exp_id', 'exp_title','exp_state','protocol_name','exp_staff','exp_code']
        fields = '__all__'