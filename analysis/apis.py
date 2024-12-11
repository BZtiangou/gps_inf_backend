from .models import gps_cluster,bt_cluster
from .serializers import LabelSerializer,get_GpsclusterSerializers,UpdateBTLabelSerializer,getBTlabelSerializer
from sensor.models import LocationInf
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.permissions import IsAdminUser

class adminGetGPSClusterApi(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        username = request.data.get('username')
        if gps_cluster.objects.filter(username=username)!=None:
            cluster = gps_cluster.objects.filter(username=username)
            serializer = get_GpsclusterSerializers(cluster,many=True)
            return Response(serializer.data)
        else:
            return Response({"The record does not exist"},status=status.HTTP_400_BAD_REQUEST)

class adminGetBTClusterApi(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        username = request.data.get('username')
        if bt_cluster.objects.filter(username=username)!=None:
            bt_inf = bt_cluster.objects.filter(username=username)
            serializer = getBTlabelSerializer(bt_inf,many=True)
            return Response(serializer.data)
        else:
            return Response({"The record does not exist"},status=status.HTTP_400_BAD_REQUEST)

class updateLabelApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        tolerance = 0.001
        username = request.user.username
        serializer = LabelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        longitude = serializer.validated_data.get('longitude')
        latitude = serializer.validated_data.get('latitude')
        label = serializer.validated_data.get('label')

        # 计算经纬度误差范围
        longitude_min = longitude - tolerance
        longitude_max = longitude + tolerance
        latitude_min = latitude - tolerance
        latitude_max = latitude + tolerance

        # 更新符合条件的 LocationInf 记录的 label 字段
        updated_location_count = LocationInf.objects.filter(
            Q(username=username) &
            Q(longitude__gte=longitude_min, longitude__lte=longitude_max) &
            Q(latitude__gte=latitude_min, latitude__lte=latitude_max)
        ).update(label=label)

        # 更新符合条件的 gps_cluster 记录的 cluster_name 字段
        updated_cluster_count = gps_cluster.objects.filter(
            Q(username=username) &
            Q(longitude__gte=longitude_min, longitude__lte=longitude_max) &
            Q(latitude__gte=latitude_min, latitude__lte=latitude_max)
        ).update(cluster_name=label)

        # 返回成功响应和更新的记录数量
        return Response({
            "message": f"{updated_location_count} LocationInf records and {updated_cluster_count} gps_cluster records updated successfully."
        }, status=status.HTTP_200_OK)


class updateBTlabelApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        username = request.user.username
        serializer = UpdateBTLabelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bt_device = serializer.validated_data['bt_device']
        new_label = serializer.validated_data['label']

        try:
            # 查找对应的 bt_cluster 记录
            bt_record = bt_cluster.objects.get(username=username, bt_device=bt_device)
            # 更新标签
            bt_record.label = new_label
            bt_record.save()
            return Response({"message": "Label updated successfully."})
        except bt_cluster.DoesNotExist:
            return Response({"error": f"No record found for the given MAC address and username.{username},{bt_device}"}, status=404)


class get_gps_cluster(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request:Request) -> Response:
        username = request.user.username
        if gps_cluster.objects.filter(username=username)!=None:
            cluster = gps_cluster.objects.filter(username=username)
            serializer = get_GpsclusterSerializers(cluster,many=True)
            return Response(serializer.data)
        else:
            return Response({"The record does not exist"},status=status.HTTP_400_BAD_REQUEST)
        
class getBTLabelApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.user.username
        if bt_cluster.objects.filter(username=username).exists():
            bt_inf = bt_cluster.objects.filter(username=username)
            serializer = getBTlabelSerializer(bt_inf,many=True)
            return Response(serializer.data)
        else:
            return Response({"The record does not exist"},status=status.HTTP_400_BAD_REQUEST)

class getGpsName(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        username = request.user.username
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
        error_margin = 0.001

        # 查询符合条件的记录
        clusters = gps_cluster.objects.filter(
            username=username,
            latitude__gte=latitude - error_margin,
            latitude__lte=latitude + error_margin,
            longitude__gte=longitude - error_margin,
            longitude__lte=longitude + error_margin
        ).exclude(cluster_name='')

        # 如果有符合条件的记录，则返回 cluster_name
        if clusters.exists():
            cluster_names = clusters.values_list('cluster_name', flat=True)
            cluster_longitude=clusters.values_list('longitude', flat=True)
            cluster_latitude=clusters.values_list('latitude', flat=True)
            return Response({"cluster_name": list(cluster_names)[0],"longitude":list(cluster_longitude)[0],"latitude":list(cluster_latitude)[0]}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No matching records found"}, status=status.HTTP_404_NOT_FOUND)