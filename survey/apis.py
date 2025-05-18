from .models import Survey,Question,Answer
from .serializers import SurveySerializer,AnswerSerializer,QuestionSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import re

# 查看某个问卷的所有问题
class ShowQuestionApi(APIView):
    permission_classes = []

    def get(self, request, survey_id):
        try:
            survey = Survey.objects.get(survey_id=survey_id)
        except Survey.DoesNotExist:
            return Response({"error": "Survey does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        raw_id = Survey.objects.filter(survey_id=survey_id).values('questions').first()
        if not raw_id:
            return Response({"error": "No questions found for this survey"}, status=status.HTTP_404_NOT_FOUND)
        
        questions_str = raw_id['questions']
        question_ids = re.findall(r'\d+', questions_str)  # 使用正则表达式找到所有数字
        
        questions = []
        for question_id in question_ids:
            try:
                question = Question.objects.get(question_id=question_id)
                question_serializer = QuestionSerializer(question)
                questions.append(question_serializer.data)
            except Question.DoesNotExist:
                # 如果问题不存在，可以根据业务需求处理，例如跳过这个问题或返回错误信息
                pass
        return Response(questions, status=status.HTTP_200_OK)
    
# 创建问卷
class createSurveyApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        survey_serializer = SurveySerializer(data=request.data)
        if survey_serializer.is_valid():
            survey_serializer.save()
            return Response(survey_serializer.data)
        return Response(survey_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 上传问题到题库
class submitQuestionApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request:Request) -> Response:
        question_serializer = QuestionSerializer(data=request.data)
        if question_serializer.is_valid():
            question_serializer.save()
            return Response(question_serializer.data)
        return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 提交问卷
class SendResApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        survey_id = request.data.get('survey_id')
        answers = request.data.get('answers')

        if not survey_id:
            return Response({"error": "survey_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            survey = Survey.objects.get(survey_id=survey_id)
        except Survey.DoesNotExist:
            return Response({"error": "Survey does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Validate answers format
        if not isinstance(answers, list):
            return Response({"error": "answers should be a list"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = []
        username=request.user.username 
        for answer in answers:
            question_id = answer.get('question_id')
            answer_text = answer.get('answer_text')
            # Validate required fields
            if not question_id or not answer_text:
                return Response({"error": "question_id and answer_text are required for each answer"}, status=status.HTTP_400_BAD_REQUEST)

            # Create response object
            response = Answer.objects.create(
                survey_id=survey_id,
                question_id=question_id,
                username=username,
                answer_text=answer_text
            )
            response_data.append(AnswerSerializer(response).data)

        return Response(response_data)
# {
#     "survey_id": 1,
#     "answers": [
#         {"question_id": 1, "answer_text": "I like the service."},
#         {"question_id": 2, "answer_text": "Very satisfied."},
#         {"question_id": 3, "answer_text": "5"}
#     ]
# }


class getquestionsApi(APIView):
    permission_classes = []
    def get(self,request:Request) -> Response:
        questions = Question.objects.all()
        question_serializer = QuestionSerializer(questions,many=True)
        return Response(question_serializer.data)