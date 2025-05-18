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
        fields = ['id', 'type', 'label', 'description', 'question', 'choices']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
            'type': {'required': False},
            'label': {'required': False},
        }

    def validate(self, attrs):
        # 创建时需要必填字段
        if self.instance is None and not attrs.get('type'):
            raise serializers.ValidationError({"type": "该字段在创建时是必填项"})
        return attrs

class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = ['id', 'trigger_type', 'distance', 'regular_time_option', 'specific_time']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False}
        }

class SurveySerializer(serializers.ModelSerializer):
    items = SurveyItemSerializer(many=True)
    trigger = TriggerSerializer()

    class Meta:
        model = Survey
        fields = ['id', 'survey_name', 'description', 'trigger', 'items']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False}
        }

    def update(self, instance, validated_data):
        # 处理触发器更新
        trigger_data = validated_data.pop('trigger', {})
        Trigger.objects.filter(id=instance.trigger.id).update(**trigger_data)
        
        # 处理问卷项更新
        items_data = validated_data.pop('items', [])
        self._handle_items(instance, items_data)
        
        return super().update(instance, validated_data)

    def _handle_items(self, survey, items_data):
        existing_items = {item.id: item for item in survey.items.all()}
        seen_ids = set()

        # 更新或创建项目
        for item_data in items_data:
            item_id = item_data.get('id')
            if item_id and item_id in existing_items:
                item = existing_items[item_id]
                for key, value in item_data.items():
                    setattr(item, key, value)
                item.save()
                seen_ids.add(item_id)
            else:
                SurveyItem.objects.create(survey=survey, **item_data)

        # 删除未包含的项目
        for item_id in existing_items:
            if item_id not in seen_ids:
                existing_items[item_id].delete()
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
# class ProtocolSerializer(serializers.ModelSerializer):
#     surveys = SurveySerializer(many=True, required=False,allow_empty=True)
#     protocol_id = serializers.IntegerField(source='id', read_only=True)  # 添加该字段

#     class Meta:
#         model = Protocol
#         fields = '__all__'
#         extra_kwargs = {
#             'id': {'read_only': True},  # 隐藏原始ID字段
#             'creator': {'read_only': True}  # 自动填充创建者
#         }

class ProtocolSerializer(serializers.ModelSerializer):
    surveys = SurveySerializer(many=True, required=False)

    class Meta:
        model = Protocol
        fields = '__all__'
        extra_kwargs = {
            'creator': {'read_only': True}
        }

    def update(self, instance, validated_data):
        surveys_data = validated_data.pop('surveys', None)
        
        # 更新基础字段
        instance = super().update(instance, validated_data)

        # 处理问卷更新
        if surveys_data is not None:
            self._handle_surveys(instance, surveys_data)
        
        return instance

    def _handle_surveys(self, protocol, surveys_data):
        existing_surveys = {s.id: s for s in protocol.surveys.all()}
        seen_ids = set()

        # 更新或创建问卷
        for survey_data in surveys_data:
            survey_id = survey_data.get('id')
            if survey_id and survey_id in existing_surveys:
                survey = existing_surveys[survey_id]
                SurveySerializer().update(survey, survey_data)
                seen_ids.add(survey_id)
            else:
                trigger_data = survey_data.pop('trigger')
                items_data = survey_data.pop('items')
                trigger = Trigger.objects.create(**trigger_data)
                survey = Survey.objects.create(protocol=protocol, trigger=trigger, **survey_data)
                SurveyItem.objects.bulk_create([
                    SurveyItem(survey=survey, **item_data) for item_data in items_data
                ])

        # 删除未包含的问卷
        for survey_id in existing_surveys:
            if survey_id not in seen_ids:
                existing_surveys[survey_id].delete()

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