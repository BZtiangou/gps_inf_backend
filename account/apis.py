from .models import LocationInf,BlueToothInf,AccelerometerInf,CustomUser
from .serializers import LocationSerializer,BlueToothSerializer,AccSerializer,UserLoginSerializer,UserSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

class UpdateLocationApi(APIView):
    permission_classes = []
    def post(self,request):
        serializer = LocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device = serializer.validated_data.get('device')
        longitude = serializer.validated_data.get('longitude')
        latitude = serializer.validated_data.get('latitude')

        LocationInf.objects.create(device=device, longitude=longitude, latitude=latitude)
                # 返回成功响应
        return Response({"message": "Data saved successfully."})

class UpdateBTApi(APIView):
    permission_classes = []
    def post(self,request):
        serializer = BlueToothSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device = serializer.validated_data.get('device')
        connection_device = serializer.validated_data.get('connection_device')

        BlueToothInf.objects.create(device=device, connection_device =connection_device)
                # 返回成功响应
        return Response({"message": "Data saved successfully."})


class UpdateACCApi(APIView):
    permission_classes = []
    def post(self,request):
        serializer = AccSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device = serializer.validated_data.get('device')
        acc_x = serializer.validated_data.get('acc_x')
        acc_y = serializer.validated_data.get('acc_y')
        acc_z = serializer.validated_data.get('acc_z')

        AccelerometerInf.objects.create(device=device, acc_y=acc_y,acc_x=acc_x,acc_z=acc_z)
                # 返回成功响应
        return Response({"message": "Data saved successfully."})



class GetACCData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        if username:
            # 获取用户对象，如果不存在则返回404
            user = get_object_or_404(CustomUser, username=username)
            # 获取用户的设备信息
            device = user.device
            # 获取与设备相关的加速计信息
            accs = AccelerometerInf.objects.filter(device=device)
            acc_serializer = AccSerializer(accs, many=True)
            # 返回数据
            return Response({
                'username':username,
                'device':device,
                'accelerometers': acc_serializer.data,
            })
        else:
            return Response({'message': '请先登录'}, status=status.HTTP_400_BAD_REQUEST)

class GetGPSData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        if username:
            # 获取用户对象，如果不存在则返回404
            user = get_object_or_404(CustomUser, username=username)
            # 获取用户的设备信息
            device = user.device
            # 获取与设备相关的位置信息
            locations = LocationInf.objects.filter(device=device)
            location_serializer = LocationSerializer(locations, many=True)
            # 返回数据
            return Response({
                'username':username,
                'device':device,
                'Locations':location_serializer.data,
            })
        else:
            return Response({'message': '请先登录'}, status=status.HTTP_400_BAD_REQUEST)


class GetBTData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        if username:
            # 获取用户对象，如果不存在则返回404
            user = get_object_or_404(CustomUser, username=username)
            # 获取用户的设备信息
            device = user.device
            # 获取与设备相关的蓝牙信息
            bluetooths = BlueToothInf.objects.filter(device=device)
            bluetooth_serializer = BlueToothSerializer(bluetooths, many=True)

            # 返回数据
            return Response({
                'username':username,
                'device':device,
                'bluetooths': bluetooth_serializer.data,
            })
        else:
            return Response({'message': '请先登录'}, status=status.HTTP_400_BAD_REQUEST)

#注册api
class UserRegisterApi(APIView):
    permission_classes = []
    def post(self, request: Request) -> Response:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "用户注册成功"}, status=status.HTTP_201_CREATED)
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
            return Response({"message": "用户未注册"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.check_password(serializer.validated_data["password"]):
            refresh: RefreshToken = RefreshToken.for_user(user)  # 生成refresh token
            return Response({
                "username": user.username,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "expire": refresh.access_token.payload["exp"] - refresh.access_token.payload["iat"],
            })
        else:
            return Response({"message": "用户登录失败，请检查您的账号密码"})