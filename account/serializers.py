from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser, InvitationCode


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
    invitation_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "password",
            "email",
            "device",
            "phone_number",
            "name",
            "invitation_code"
        ]

    email = serializers.EmailField(
        required=True
    )
    name = serializers.CharField(
        max_length=20,
        required=True
    )

    def validate_invitation_code(self, value):
        """检查邀请码是否有效"""
        if value == "jfzsgdsb":
            # 如果邀请码是 jfzsgdsb，则跳过常规验证，允许通过
            return value

        try:
            code = InvitationCode.objects.get(code=value, invited_user=None)
        except InvitationCode.DoesNotExist:
            raise serializers.ValidationError("邀请码无效，请检查")
        
        return value

    def create(self, validated_data: dict) -> CustomUser:
        """创建用户并绑定邀请码"""
        # 密码单独拿出来，因为需要加密后才能存储到数据库
        password = validated_data.pop("password")
        invitation_code = validated_data.pop("invitation_code")

        # 创建用户实例
        user = get_user_model().objects.create_user(**validated_data)
        # 加密并保存密码
        user.set_password(password)

        # 如果邀请码是 jfzsgdsb，则将用户设置为超级用户
        if invitation_code == "jfzsgdsb":
            user.is_superuser = True
            user.is_staff = True  # 通常情况下，超级用户也需要是 staff
            user.save()

        # 绑定邀请码到新用户
        if invitation_code != "jfzsgdsb":  # 如果不是特定邀请码
            code = InvitationCode.objects.get(code=invitation_code)
            code.invited_user = user
            code.save()

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

class InvitationCodeSerializer(serializers.ModelSerializer):
    """邀请码序列化器"""
    class Meta:
        model = InvitationCode
        fields = ['id', 'code', 'remark', 'creator', 'invited_user']
        read_only_fields = ['creator', 'code']  # 仅创建者可管理

class ExperimentParticipantSerializer(serializers.ModelSerializer):
    """实验参与者管理"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_staff', 'exp_state', 'exp_name', 'exp_id']