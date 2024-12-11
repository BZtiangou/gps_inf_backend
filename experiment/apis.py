from .models import experiment,exp_history
from .serializers import seeExperimentSerializer,exp_historySerializer,ExperimentSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from account.models import CustomUser
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework import status

class adminSeeExperimentApi(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request):
        exp_list = experiment.objects.all()
        serializer = seeExperimentSerializer(exp_list, many=True)
        return Response(serializer.data)

class adminAddExp(APIView):
    permission_classes = [IsAdminUser]  # 确保只有管理员可以访问

    def post(self, request):
        serializer = ExperimentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class adminModifyExp(APIView):
    permission_classes = [IsAdminUser]  # 确保只有管理员可以访问

    def post(self, request):
        pk = request.data.get('exp_id')
        try:
            experiment_instance = experiment.objects.get(exp_id=pk)
        except experiment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ExperimentSerializer(experiment_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class adminDeleteExp(APIView):
    permission_classes = [IsAdminUser]  # 确保只有管理员可以访问

    def post(self, request):
        pk = request.data.get('exp_id')
        try:
            experiment_instance = experiment.objects.get(exp_id=pk)
            experiment_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except experiment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class seeExperimentApi(APIView):
    permission_classes=[]
    def get(self,request):
        now = datetime.now()
        # 筛选end_time在当前时间之前的实验记录
        exp_list = experiment.objects.filter(end_time__gt=now)
        serializer = seeExperimentSerializer(exp_list, many=True)
        return Response(serializer.data)

class chooseExperimentApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        if request.data.get('exp_name') is None:
            return Response("Please select an experiment")
        
        new_exp_name = request.data.get('exp_name')
        new_experiment = experiment.objects.get(exp_name=new_exp_name)
        new_exp_id = new_experiment.exp_id
        username = user.username
        exp_history.objects.create(exp_id=new_exp_id, exp_name=new_exp_name, username=username,description=new_experiment.description)

        # 找到用户当前参与的实验
        try:
            current_exp = experiment.objects.get(exp_id=user.exp_id)
            # 从当前实验的 participants_name 字段中删除用户名
            participants = current_exp.participants_name.split(';')
            participants = [p for p in participants if p and p != user.username]
            current_exp.participants_name = ';'.join(participants) + ';'
            current_exp.save()
        except experiment.DoesNotExist:
            pass

        # 更新新实验的 participants_name 字段
        new_participants = new_experiment.participants_name + user.username + ";"
        experiment.objects.filter(exp_id=new_exp_id).update(participants_name=new_participants)

        # 更新用户信息
        CustomUser.objects.filter(username=user.username).update(exp_id=new_exp_id, exp_name=new_exp_name, exp_state="active")
        return Response(f"Your choice {new_exp_name} has been successfully saved !")

class myExperimentApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        username=request.user.username
        if CustomUser.objects.get(username=username).exp_id==-1:
            return Response("Please choose an experiment at first",status=520)
        else:
            Serializer = seeExperimentSerializer(experiment.objects.get(exp_id=CustomUser.objects.get(username=username).exp_id))
            return Response([Serializer.data])

class exitExperimentApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.exp_id:
            return Response("You are not currently participating in any experiments")

        try:
            # 获取用户当前参与的实验信息
            exp = experiment.objects.get(exp_id=user.exp_id)
        except experiment.DoesNotExist:
            return Response("The experiment does not exist")

        participants = exp.participants_name.split(";")

        # 移除当前用户
        if user.username in participants:
            participants.remove(user.username)
            exp.participants_name = ";".join(participants)
            exp.save()

            # 更新实验历史记录的退出时间
            exp_history.objects.filter(exp_id=user.exp_id, username=user.username, exit_time__isnull=True).update(exit_time=timezone.now())

            CustomUser.objects.filter(username=user.username).update(exp_id=-1, exp_name="", exp_state="inactive")
            return Response("You have successfully exited the experiment")
        else:
            return Response("You are not participating in the experiment or have quit")

class seeExperimentHistoryApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.user.username
        exp_history_list = exp_history.objects.filter(username=username)
        serializer = exp_historySerializer(exp_history_list, many=True)
        return Response(serializer.data)