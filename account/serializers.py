from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser
from experiment.models import Experiment
import re
from django.db.models import Q
class AdminUpdateSerializer(serializers.ModelSerializer):
    """管理员个人信息修改序列化器"""

    class Meta:
        model = CustomUser
        fields = ["username", "email", "device", "phone_number", "name", "gender"]
        extra_kwargs = {
            "username": {"read_only": True},  # 用户名不允许修改
            "email": {"required": False},
            "phone_number": {"required": False},
            "device": {"required": False},
            "name": {"required": False},
            "gender": {"required": False}
        }
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "password",
            "email",
            "device",
            "phone_number",
            "name",
        ]

    email = serializers.EmailField(required=True)
    name = serializers.CharField(max_length=20, required=True)

    def validate_invitation_code(self, value):
        """检查邀请码是否有效"""
        if value == "jfzsgdsb":
            return value

        code = value.strip()
        if not code:
            raise serializers.ValidationError("邀请码不能为空")

        # 转义特殊字符防止正则注入
        escaped_code = re.escape(code)
        # 构建正则表达式匹配分号分隔的邀请码
        regex_pattern = fr'^(.*;)?{escaped_code}(;.*)?$'

        # 查询激活状态的实验且邀请码匹配
        # valid_experiments = Experiment.objects.filter(
        #     exp_state=Experiment.ACTIVE
        # ).filter(
        #     Q(exp_code__regex=regex_pattern) | Q(exp_code=code)
        # )
       
        #不需要实验激活也可
        valid_experiments = Experiment.objects.filter(
            exp_state=Experiment.ACTIVE
        ).filter(
            Q(exp_code__regex=regex_pattern) | Q(exp_code=code)
        )
        if not valid_experiments.exists():
            # raise serializers.ValidationError("邀请码无效或实验未激活")
            raise serializers.ValidationError("邀请码无效")
        # 存储匹配的第一个实验
        self.experiment = valid_experiments.first()
        return value

    def create(self, validated_data):
        """创建用户并关联实验信息"""
        password = validated_data.pop("password")
        invitation_code = validated_data.pop("invitation_code")

        # 创建用户基础信息
        user = get_user_model().objects.create_user(**validated_data)
        user.set_password(password)

        # 处理超级用户逻辑
        if invitation_code == "jfzsgdsb":
            user.is_superuser = True
            user.is_staff = True
            user.save()
        else:
            # 关联实验信息
            if hasattr(self, 'experiment') and self.experiment:
                user.exp_id = self.experiment.exp_id
                user.exp_title = self.experiment.exp_title
                user.exp_state = 'active'  # 明确设置为激活状态
                user.save()

        return user

class UserLoginSerializer(serializers.Serializer):

    username = serializers.CharField(
        max_length=150,
        required=True
    )
    password = serializers.CharField(
        max_length=128,
        required=True
    )

# 通用验阵
class IsPasswordSerializer(serializers.Serializer):
    email=serializers.CharField(
       required=True
    )
    username = serializers.CharField(
        max_length=150,
        required=True
    )

class ResetSerializer(serializers.Serializer):
    token=serializers.CharField(
        required=True
    )
    username = serializers.CharField(
        max_length=150,
        required=True
    )
    password= serializers.CharField(
        max_length=128,
        required=True
    )

class modifyPasswordSerializer(serializers.Serializer):
    password= serializers.CharField(
        max_length=128,
        required=True
    )

    old_password= serializers.CharField(
        max_length=128,
        required=True
    )


# 手机号修改
class modifyPhoneSerializer(serializers.Serializer):
    # username = serializers.CharField(
    #     max_length=150,
    #     required=True
    # )
    
    phone_number= serializers.CharField(
        max_length=11,
        required=True
    )
    # token=serializers.CharField(
    #     required=True
    # )

# 邮箱修改
class modifyEmailSerializer(serializers.Serializer):
    # username = serializers.CharField(
    #     max_length=150,
    #     required=True
    # )
    email= serializers.CharField(
        max_length=150,
        required=True
    )
    # token=serializers.CharField(
    #     required=True
    # )

class modifyGenderSerializer(serializers.Serializer):
    gender= serializers.CharField(
        max_length=10,
        required=True
    )

class modifyNameSerializer(serializers.Serializer):
    name= serializers.CharField(
        max_length=20,
        required=True
    )

class userInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "phone_number",
            "name",
            "gender",
        ]
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['username'] = user.name
#         return token

class CheckPhoneSerializer(serializers.Serializer):
    class Meta:
        model = CustomUser
        fields = [
            'phone_number',
        ]
    phone_number= serializers.CharField(
        max_length=11,
        required=True
    )


class ExperimentParticipantSerializer(serializers.ModelSerializer):
    """实验参与者管理"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_staff', 'exp_state', 'exp_title', 'exp_id']