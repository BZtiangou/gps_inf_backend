from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image
import subprocess
import os

class ImagePredictAPIView(APIView):
    permission_classes = []  # 可根据需求调整权限控制

    # 验证图像合法性
    def process_image(self, image_file):
        try:
            img = Image.open(image_file)
            img.verify()  # 验证图像完整性
            img.close()
        except (IOError, SyntaxError):
            return False
        return True

    def post(self, request):
        # 获取上传的图片文件
        image_file = request.FILES.get('file')
        if not image_file:
            return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查文件类型
        if image_file.content_type not in ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']:
            return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查文件扩展名
        ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
        extension = os.path.splitext(image_file.name)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            return Response({"error": "Invalid file extension"}, status=status.HTTP_400_BAD_REQUEST)

        # 验证图像文件
        # if not self.process_image(image_file):
        #     return Response({"error": "Invalid image file"}, status=status.HTTP_400_BAD_REQUEST)

        # 保存文件到正式目录
        fs = FileSystemStorage(location=settings.MEDIA_ROOT + '/picture')
        filename = fs.save(image_file.name, image_file)
        final_image_path = os.path.join(settings.MEDIA_ROOT, 'picture', filename)

        # 调用预测脚本
        try:
            result = subprocess.run([
                'bash', '-c',
                f"source /home/xyc/bigtiao/softvote/venv/bin/activate && python /home/xyc/bigtiao/softvote/judge.py {final_image_path}"
            ], capture_output=True, text=True)
            prediction = result.stdout.strip()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 提取表单数据
        bookname = request.data.get('bookname')
        author = request.data.get('author')
        publisher = request.data.get('publisher')

        # 返回预测结果和表单数据
        return Response({
            "prediction": prediction,
            "bookname": bookname,
            "author": author,
            "publisher": publisher
        }, status=status.HTTP_200_OK)
