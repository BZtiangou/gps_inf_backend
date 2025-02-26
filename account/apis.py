from .models import CustomUser
from .serializers import modifyPhoneSerializer,modifyEmailSerializer,modifyPasswordSerializer,UserLoginSerializer,UserSerializer,IsPasswordSerializer,ResetSerializer,modifyNameSerializer
from .serializers import modifyGenderSerializer,userInfoSerializer,CheckPhoneSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.utils import timezone
from base import email_inf
from rest_framework.permissions import IsAdminUser
from .models import CustomUser, InvitationCode
from .serializers import InvitationCodeSerializer, ExperimentParticipantSerializer
from .serializers import AdminUpdateSerializer
import random
import string

class GetUserInfoByNameApi(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        # 从请求体中获取 name 字段
        name = request.data.get("name")
        
        if not name:
            return Response({"message": "Name field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 根据提供的姓名查找用户
            user = CustomUser.objects.get(name=name)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found with the given name"}, status=status.HTTP_400_BAD_REQUEST)

        # 序列化用户信息
        seri = userInfoSerializer(user)
        return Response(seri.data)

class AdminUpdateProfileApi(APIView):
    """
    管理员修改个人信息 API（使用 `POST` 方法）
    仅 `is_staff=True` 或 `is_superuser=True` 的用户可以修改个人信息
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        """管理员修改个人信息"""
        user = request.user

        if not user.is_staff and not user.is_superuser:
            return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

        # 过滤空值，确保只更新提供的字段
        update_fields = {key: value for key, value in request.data.items() if value}
        if not update_fields:
            return Response({"message": "No fields provided for update"}, status=status.HTTP_400_BAD_REQUEST)

        # 进行部分更新
        serializer = AdminUpdateSerializer(user, data=update_fields, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdminLoginApi(APIView):
    permission_classes = []

    def post(self, request: Request) -> Response:
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = get_user_model().objects.get(username=serializer.validated_data["username"])
        except ObjectDoesNotExist:
            return Response({"message": "User not registered"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(serializer.validated_data["password"]):
            return Response({"message": "User login failed, please check your account password"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.is_staff:  # 假设管理员的标识是 is_staff 字段
            refresh: RefreshToken = RefreshToken.for_user(user)  # 生成refresh token
            return Response({
                "username": user.username,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "expire": refresh.access_token.payload["exp"] - refresh.access_token.payload["iat"],
            })
        else:
            return Response({"message": "User is not an admin"}, status=status.HTTP_401_UNAUTHORIZED)


class getUserInfoApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        user = get_object_or_404(CustomUser, username=username)
        seri=userInfoSerializer(user)
        return Response(seri.data)

class AllUserNameApi(APIView):
    permission_classes = [IsAdminUser]  # 确保只有管理员可以访问
    def get(self, request):
        users = CustomUser.objects.all()
        # usernames = [user.username for user in users]
        # return Response(usernames)
        serializer = userInfoSerializer(users, many=True)  
        return Response(serializer.data)  

class adminGetUserInfoApi(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        username = request.data.get('username')
        user = get_object_or_404(CustomUser, username=username)
        seri=userInfoSerializer(user)
        return Response(seri.data)

#注册api
class UserRegisterApi(APIView):
    permission_classes = []
    def post(self, request: Request) -> Response:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registration succeeded"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserLoginApi(APIView):
    permission_classes = []
    def post(self, request: Request) -> Response:
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = get_user_model().objects.get(username=serializer.validated_data["username"])
        except ObjectDoesNotExist:
            return Response({"message": "User not registered"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.check_password(serializer.validated_data["password"]):
            refresh: RefreshToken = RefreshToken.for_user(user)  # 生成refresh token
            return Response({
                "username": user.username,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "expire": refresh.access_token.payload["exp"] - refresh.access_token.payload["iat"],
            })
        else:
            return Response({"message": "User login failed, please check your account password"})

# 检查手机号码是否正确
class checkphoneApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = CheckPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        username = request.user.username

        try:
            user = get_user_model().objects.get(phone_number=phone_number, username=username)
            return Response("Accept", status=status.HTTP_200_OK)
        except get_user_model().DoesNotExist:
            return Response("手机号码不存在", status=status.HTTP_400_BAD_REQUEST)



# 令牌发送api 通用api
class Is_PasswordApi(APIView):
    permission_classes = []
    def post(self, request: Request) -> Response:
        serializer = IsPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if get_user_model().objects.get(username=serializer.validated_data["username"]) == None:
            return Response("用户不存在",status=status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.get(username=serializer.validated_data["username"])
        if user.email == serializer.validated_data["email"]:
            token_value = get_random_string(length=6)
            user.token = token_value
            user.token_expires = timezone.now() + timezone.timedelta(minutes=2)  # 设置2分钟后过期
            user.save()
            send_mail(
                '重置密码',
                message=f'您正在尝试找回密码或者修改其他验证信息，您的令牌是{token_value}',
                from_email=email_inf.EMAIL_FROM,
                recipient_list=[user.email],
            )
            return Response({
                "Token email has been sent to your reserved mailbox, please check!"
            })
        else:
            return Response("The mailbox is incorrect or does not exist",status=status.HTTP_400_BAD_REQUEST)


# 后续感觉需要添加验证码等防爆破
class ResetPasswordApi(APIView):
    permission_classes = []
    def post(self, request: Request) -> Response:
        serializer = ResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            if serializer.validated_data['token'] == user.token and user.token_expires and timezone.now() <= user.token_expires:
                user = get_user_model().objects.get(username=serializer.validated_data['username'])
                # 更新密码前，先使用 set_password 方法加密密码
                user.set_password(serializer.validated_data['password'])
                user.save()
                return Response({
                    f"Your password has been changed successfully. Please log in again"
                })
            else:
                return Response({
                    "令牌超时或错误"
                })
        else :
            return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

class modifyPasswordApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        serializer = modifyPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            if user.check_password(serializer.validated_data['old_password']):
                user.set_password(serializer.validated_data['password'])
                user.save()
                return Response({
                    f"Your password has been changed successfully. Please log in again"
                })
        return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

# class modifyPhoneApi(APIView):
#     permission_classes = []
#     def post(self, request: Request) -> Response:
#         serializer = modifyPhoneSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data['username']
#         if get_user_model().objects.get(username=username):
#             user = get_user_model().objects.get(username=username)
#             if serializer.validated_data['token'] == user.token and timezone.now() <= user.token_expires:
#                 user = get_user_model().objects.get(username=serializer.validated_data['username'])
#                 user.phone_number = serializer.validated_data['phone_number']
#                 user.save()
#                 return Response({
#                     f"您的手机号修改成功!"
#                 })
#             else:
#                 return Response({
#                     "令牌超时或错误"
#                 })
#         else :
#             return Response({"The user name does not exist"},status=status.HTTP_404_NOT_FOUND)

# class modifyEmailApi(APIView):
#     permission_classes = []
#     def post(self, request: Request) -> Response:
#         serializer = modifyEmailSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         username = serializer.validated_data['username']
#         if get_user_model().objects.get(username=username):
#             user = get_user_model().objects.get(username=username)
#             if serializer.validated_data['token'] == user.token and timezone.now() <= user.token_expires:
#                 user = get_user_model().objects.get(username=serializer.validated_data['username'])
#                 user.email = serializer.validated_data['email']
#                 user.save()
#                 return Response({
#                     f"Your email address has been successfully modified!"
#                 })
#             else:
#                 return Response({
#                     "令牌超时或错误"
#                 })
#         else :
#             return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

# 无安全验证版本
class modifyEmailApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        serializer = modifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            user.email= serializer.validated_data['email']
            user.save()
            return Response("email modification successful")
        return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

class modifyPhoneApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        serializer = modifyPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            user.phone_number= serializer.validated_data['phone_number']
            user.save()
            return Response("phone modification successful")
        return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

        
class modifyGenderApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        serializer = modifyGenderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            user.gender= serializer.validated_data['gender']
            user.save()
            return Response("Gender modification successful")
        return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)

class modifyNameApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        serializer = modifyNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        if get_user_model().objects.get(username=username):
            user = get_user_model().objects.get(username=username)
            user.name= serializer.validated_data['name']
            user.save()
            return Response("Name changed successfully")
        return Response({"The user name does not exist"},status=status.HTTP_400_BAD_REQUEST)
    
class CreateInvitationCodeApi(APIView):
    """
    创建邀请码 API
    仅 `staff` 或 `admin` 用户可以创建邀请码
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_staff and not user.is_superuser:
            return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        
        # 生成邀请码
        invitation_code = InvitationCode.objects.create(
            creator=user,
            code=''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
            remark=request.data.get("remark", "")
        )

        serializer = InvitationCodeSerializer(invitation_code)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ManageExperimentParticipantsApi(APIView):
    """
    管理实验参与者 API
    允许：
    1. 移除实验参与者
    2. 设置某个用户为 `staff`
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取当前管理员的实验参与者列表"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)
        
        participants = CustomUser.objects.filter(exp_id=request.user.exp_id)
        serializer = ExperimentParticipantSerializer(participants, many=True)
        return Response(serializer.data)

    def delete(self, request, user_id):
        """移除实验参与者"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(CustomUser, id=user_id)
        if user.exp_id != request.user.exp_id:
            return Response({"message": "You cannot remove users from other experiments"}, status=status.HTTP_403_FORBIDDEN)

        user.exp_id = -1  
        user.exp_name = ""
        user.exp_state = "inactive"
        user.save()
        
        return Response({"message": f"User {user.username} removed from the experiment"}, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        """修改用户权限（设置 `staff` 角色）"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"message": "Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(CustomUser, id=user_id)
        if user.exp_id != request.user.exp_id:
            return Response({"message": "You cannot modify users from other experiments"}, status=status.HTTP_403_FORBIDDEN)

        user.is_staff = request.data.get("is_staff", False)
        user.save()
        
        return Response({"message": f"User {user.username} role updated"}, status=status.HTTP_200_OK)