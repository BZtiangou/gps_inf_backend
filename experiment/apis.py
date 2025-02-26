from .models import Experiment,exp_history, Protocol, Survey, SurveyItem, Trigger
from .serializers import seeExperimentSerializer,exp_historySerializer,ExperimentSerializer,ProtocolSerializer,ProtocolDetailSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from account.models import CustomUser
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.db.models import Prefetch

class adminSeeExperimentApi(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request):
        exp_list = Experiment.objects.all()
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
            experiment_instance = Experiment.objects.get(exp_id=pk)
        except Experiment.DoesNotExist:
            return Response("man, the experiment is not exist",status=status.HTTP_404_NOT_FOUND)

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
            experiment_instance = Experiment.objects.get(exp_id=pk)
            experiment_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Experiment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class seeExperimentApi(APIView):
    permission_classes=[]
    def get(self,request):
        now = datetime.now()
        # 筛选end_time在当前时间之前的实验记录
        exp_list = Experiment.objects.filter(end_time__gt=now)
        serializer = seeExperimentSerializer(exp_list, many=True)
        return Response(serializer.data)

class chooseExperimentApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        if request.data.get('exp_name') is None:
            return Response("Please select an experiment")
        
        new_exp_name = request.data.get('exp_name')
        new_experiment = Experiment.objects.get(exp_name=new_exp_name)
        new_exp_id = new_experiment.exp_id
        username = user.username
        exp_history.objects.create(exp_id=new_exp_id, exp_name=new_exp_name, username=username,description=new_experiment.description)

        # 找到用户当前参与的实验
        try:
            current_exp = Experiment.objects.get(exp_id=user.exp_id)
            # 从当前实验的 participants_name 字段中删除用户名
            participants = current_exp.participants_name.split(';')
            participants = [p for p in participants if p and p != user.username]
            current_exp.participants_name = ';'.join(participants) + ';'
            current_exp.save()
        except Experiment.DoesNotExist:
            pass

        # 更新新实验的 participants_name 字段
        new_participants = new_experiment.participants_name + user.username + ";"
        Experiment.objects.filter(exp_id=new_exp_id).update(participants_name=new_participants)

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
            Serializer = seeExperimentSerializer(Experiment.objects.get(exp_id=CustomUser.objects.get(username=username).exp_id))
            return Response([Serializer.data])

class exitExperimentApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.exp_id:
            return Response("You are not currently participating in any experiments")

        try:
            # 获取用户当前参与的实验信息
            exp = Experiment.objects.get(exp_id=user.exp_id)
        except Experiment.DoesNotExist:
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
    
class CreateProtocolAPIView(APIView):
    """
    API 用于创建新的 Protocol 实验协议（包含 Survey）
    """
    permission_classes=[IsAdminUser]
    def post(self, request, *args, **kwargs):
         # 分离主协议数据和调查问卷数据
        protocol_data = request.data.copy()
        surveys_data = protocol_data.pop('surveys', [])
        protocol_data['creator'] = request.user.username

        # 主协议序列化验证
        serializer = ProtocolSerializer(data=protocol_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # 创建主协议（使用create代替save以更好控制流程）
        protocol = Protocol.objects.create(
            **{k: v for k, v in protocol_data.items() if k != 'surveys'}
        )

        # 处理嵌套问卷结构
        for survey_data in surveys_data:
            # 验证必要字段
            if 'survey_name' not in survey_data:
                raise ValueError("缺少必要字段: survey_name")
            
            # 创建触发器
            trigger_data = survey_data.get('trigger', {})
            trigger = Trigger.objects.create(
                trigger_type=trigger_data.get('trigger_type', 'Regular Time'),
                regular_time_option=trigger_data.get('regular_time_option'),
                specific_time=trigger_data.get('specific_time')
            )

            # 创建问卷
            survey = Survey.objects.create(
                protocol=protocol,
                survey_name=survey_data['survey_name'],
                description=survey_data.get('description', ''),
                trigger=trigger
            )

            # 处理问卷项
            for item_data in survey_data.get('items', []):
                # 转换choices格式
                if 'choices' in item_data and isinstance(item_data['choices'], list):
                    item_data['choices'] = ';'.join(item_data['choices'])
                
                SurveyItem.objects.create(
                    survey=survey,
                    type=item_data.get('type', 'q_and_a'),
                    label=item_data['label'],
                    description=item_data.get('description', ''),
                    question=item_data['question'],
                    choices=item_data.get('choices', '')
                )

        return Response(
            {
                "message": "协议创建成功",
                "protocol_id": protocol.id,
                "surveys_count": len(surveys_data)
            },
            status=status.HTTP_201_CREATED
        )

    
class DeleteProtocolAPIView(APIView):
    """
    删除协议API
    请求方式：POST
    权限要求：管理员
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        # 获取协议ID
        protocol_id = request.data.get('protocol_id')
        
        if not protocol_id:
            return Response(
                {"error": "缺少 protocol_id 参数"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 获取并删除协议（会自动级联删除关联的 Survey 和 Trigger）
            protocol = Protocol.objects.get(pk=protocol_id)
            protocol.delete()
            return Response(
                {"message": f"协议 {protocol_id} 删除成功"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Protocol.DoesNotExist:
            return Response(
                {"error": "指定协议不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
class UpdateProtocolAPIView(APIView):
    """
    局部更新协议API
    请求方式：post
    权限要求：管理员
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            pk = request.data.get('protocol_id')
            protocol = Protocol.objects.get(pk=pk)
        except Protocol.DoesNotExist:
            return Response(
                {"error": "协议不存在"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 允许部分更新，保留原有数据
        serializer = ProtocolSerializer(
            protocol, 
            data=request.data, 
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "协议更新成功",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "error": "数据验证失败",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    

class UserProtocolAPIView(APIView):
    """
    获取用户协议列表（包含完整问卷详细信息）
    请求方式：GET
    权限要求：JWT认证用户
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            username = request.user.username
            
            # 优化数据库查询：一次性预取所有关联数据
            protocols = Protocol.objects.filter(creator=username).prefetch_related(
                Prefetch('surveys', 
                    queryset=Survey.objects.select_related('trigger').prefetch_related(
                        Prefetch('items', queryset=SurveyItem.objects.all())
                    )
                )
            )
            
            serializer = ProtocolDetailSerializer(
                protocols,
                many=True,
                context={'request': request}
            )

            return Response({
                "user": username,
                "count": len(serializer.data),
                "protocols": serializer.data
            })

        except Exception as e:
            return Response(
                {"error": f"查询失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )