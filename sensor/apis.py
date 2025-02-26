from .models import LocationInf,BlueToothInf,AccelerometerInf,GyroInf,BatteryInf
from .serializers import LocationSerializer,BlueToothSerializer,AccSerializer,GyroSerializer,BatterySerializer
from analysis.models import gps_cluster,bt_cluster
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from incdbscan import IncrementalDBSCAN
import numpy as np
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser

class adminGetGPSApi(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        username = request.data.get('username')
        if username:
            # 获取与设备相关的位置信息
            locations = LocationInf.objects.filter(username=username)
            location_serializer = LocationSerializer(locations, many=True)
            # 返回数据
            return Response({
                'username':username,
                'Locations':location_serializer.data,
            })
        else:
            return Response({'message': f'{username}Please log in first'}, status=status.HTTP_400_BAD_REQUEST)

class adminGetBTApi(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        username = request.data.get('username')
        if username:
            # 获取与设备相关的蓝牙信息
            bluetooths = BlueToothInf.objects.filter(username=username)
            bluetooth_serializer = BlueToothSerializer(bluetooths, many=True)
            # 返回数据
            return Response({
                'username':username,
                'bluetooths': bluetooth_serializer.data,
            })
        else:
            return Response({'message': 'Please log in first'}, status=status.HTTP_400_BAD_REQUEST)
        
class adminGetACCApi(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        username = request.data.get('username')[:10000]
        if username:
            # 获取与设备相关的加速计信息
            accs = AccelerometerInf.objects.filter(username=username)
            acc_serializer = AccSerializer(accs, many=True)
            # 返回数据
            return Response({
                'username':username,
                'accelerometers': acc_serializer.data,
            })
        else:
            return Response({'message': 'Please log in first'}, status=status.HTTP_400_BAD_REQUEST)

class adminGetGyroApi(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        username = request.data.get('username')
        if username:
            # 获取与设备相关的加速计信息
            gyro= GyroInf.objects.filter(username=username)[:10000]
            gyro_serializer = GyroSerializer(gyro, many=True)
            # 返回数据
            return Response({
                'username':username,
                'gyro': gyro_serializer.data,
            })
        else:
            return Response({'message': 'Please log in first'}, status=status.HTTP_400_BAD_REQUEST)

class adminGetBatteryApi(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        username = request.data.get('username')
        if username:
            Battery= BatteryInf.objects.filter(username=username)
            Battery_serializer = BatterySerializer(Battery, many=True)
            # 返回数据
            return Response({
                'username':username,
                'Battery': Battery_serializer.data,
            })
        else:
            return Response({'message': 'Please log in first'}, status=status.HTTP_400_BAD_REQUEST)

class UpdateLocationApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        eps = 0.001
        min_samples = 5
        username = request.user.username
        serializer = LocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device = serializer.validated_data.get('device')
        longitude = serializer.validated_data.get('longitude')
        latitude = serializer.validated_data.get('latitude')
        accuracy = serializer.validated_data.get('accuracy')

        # 获取用户所有位置信息
        user_locations = LocationInf.objects.filter(username=username).values_list('longitude', 'latitude')
        coordinates = np.array(user_locations)

        # 初始化增量DBSCAN
        clusterer = IncrementalDBSCAN(eps=eps, min_pts=min_samples)

        # 插入已有的数据点
        if len(coordinates) > 0:
            clusterer.insert(coordinates)

        # 插入新数据点
        new_point = np.array([[longitude, latitude]])
        clusterer.insert(new_point)

        if len(coordinates) > 0:
            # 如果 coordinates 不为空，进行拼接
            all_labels = clusterer.get_cluster_labels(np.vstack((coordinates, new_point)))
        else:
            # 如果 coordinates 为空，直接使用 new_point
            all_labels = clusterer.get_cluster_labels(new_point)

        # 获取新点的标签
        new_point_label = all_labels[-1]

        # 如果新点形成了新的簇，则保存新的聚类信息
        if new_point_label != -1 and not gps_cluster.objects.filter(
           username=username,label=new_point_label
        ).exists():
            gps_cluster.objects.create(
                username=username,
                longitude=longitude,
                latitude=latitude,
                label=new_point_label
            )

        # 保存新的位置信息
        LocationInf.objects.create(
            username=username,
            device=device,
            longitude=longitude,
            latitude=latitude,
            accuracy=accuracy
        )

        # 返回成功响应和 flag
        return Response({
            "message": "Data saved successfully."
        })
    
class UpdateBTApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.user.username
        serializer = BlueToothSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            # 这里处理数据验证错误，并返回状态码521
            return Response({"message": "Data validation error."})

        device = serializer.validated_data.get('device')
        connection_device = serializer.validated_data.get('connection_device')

        # 解析 connection_device 字段
        devices = connection_device.split(';')
        mac_counter = {}
        results = []

        # 统计 BlueToothInf 表中当前用户的 MAC 地址计数
        all_user_records = BlueToothInf.objects.filter(username=username)
        for record in all_user_records:
            conn_devices = record.connection_device.split(';')
            for conn_dev in conn_devices:
                try:
                    _, mac_addr = conn_dev.split(':', 1)
                except ValueError:
                    continue
                if mac_addr in mac_counter:
                    mac_counter[mac_addr] += 1
                else:
                    mac_counter[mac_addr] = 1

        for dev in devices:
            try:
                name, mac = dev.split(':', 1)
            except ValueError:
                continue

            # 检查是否在当前用户的 bt_cluster 中
            if bt_cluster.objects.filter(username=username, bt_device=f"{name}:{mac}").exists():
                results.append({'mac': mac, 'flag': 0})
            else:
                # 判断设备名称是否有效
                if mac_counter.get(mac, 0) > 5 and name != "undefined":
                    # 保存到 bt_cluster
                    bt_cluster.objects.create(
                        username=username,
                        bt_device=f"{name}:{mac}"
                    )
                    important=f'{name}:{mac}'
                    results.append({'important': important, 'flag': 1})
                else:
                    results.append({'mac': mac, 'flag': 0})

        # 保存到 BlueToothInf 中
        BlueToothInf.objects.create(username=username, device=device, connection_device=connection_device)

        # 返回处理结果
        return Response({"message": "Data saved successfully.", "results": results})

class UpdateACCApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        username = request.user.username
        serializer = AccSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device = serializer.validated_data.get('device')
        acc_x = serializer.validated_data.get('acc_x')
        acc_y = serializer.validated_data.get('acc_y')
        acc_z = serializer.validated_data.get('acc_z')

        AccelerometerInf.objects.create(username=username,device=device, acc_y=acc_y,acc_x=acc_x,acc_z=acc_z)
                # 返回成功响应
        return Response({"message": "Data saved successfully."})

class GetACCData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        if username:
            # 获取与设备相关的加速计信息
            accs = AccelerometerInf.objects.filter(username=username)
            acc_serializer = AccSerializer(accs, many=True)
            # 返回数据
            return Response({
                'username':username,
                'accelerometers': acc_serializer.data,
            })
        else:
            return Response({'message': 'Please log in first'}, status=status.HTTP_400_BAD_REQUEST)

class GetGPSData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        if username:
            # 获取与设备相关的位置信息
            locations = LocationInf.objects.filter(username=username)
            location_serializer = LocationSerializer(locations, many=True)
            # 返回数据
            return Response({
                'username':username,
                'Locations':location_serializer.data,
            })
        else:
            return Response({'message': 'Please log in first'}, status=status.HTTP_400_BAD_REQUEST)

class GetBTData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        if username:
            # 获取与设备相关的蓝牙信息
            bluetooths = BlueToothInf.objects.filter(username=username)
            bluetooth_serializer = BlueToothSerializer(bluetooths, many=True)
            # 返回数据
            return Response({
                'username':username,
                'bluetooths': bluetooth_serializer.data,
            })
        else:
            return Response({'message': 'Please log in first'}, status=status.HTTP_400_BAD_REQUEST)

class UpdateGyroApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        username = request.user.username
        serializer = GyroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device = serializer.validated_data.get('device')
        x = serializer.validated_data.get('x')
        y = serializer.validated_data.get('y')
        z = serializer.validated_data.get('z')

        GyroInf.objects.create(username=username,device=device, y=y,x=x,z=z)
                # 返回成功响应
        return Response({"message": "Data saved successfully."})
    
class updateBatteryApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.user.username
        serializer = BatterySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取验证后的数据
        device = serializer.validated_data.get('device')
        battery_level = serializer.validated_data.get('battery_level')
        battery_status = serializer.validated_data.get('battery_status')
        
        # 如果设备为空，将其设置为空字符串
        if not device:
            device = ""

        # 保存电池信息
        BatteryInf.objects.create(username=username, device=device, battery_level=battery_level, battery_status=battery_status)
        
        return Response({"message": "Data saved successfully."})

class GetBatteryData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        if username:
            Battery= BatteryInf.objects.filter(username=username)
            Battery_serializer = BatterySerializer(Battery, many=True)
            # 返回数据
            return Response({
                'username':username,
                'Battery': Battery_serializer.data,
            })
        else:
            return Response({'message': 'Please log in first'}, status=status.HTTP_400_BAD_REQUEST)

class GetGyroData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        if username:
            # 获取与设备相关的加速计信息
            gyro= GyroInf.objects.filter(username=username)
            gyro_serializer = GyroSerializer(gyro, many=True)
            # 返回数据
            return Response({
                'username':username,
                'gyro': gyro_serializer.data,
            })
        else:
            return Response({'message': 'Please log in first'}, status=status.HTTP_400_BAD_REQUEST)