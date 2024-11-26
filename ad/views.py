from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import subprocess
import os

class ImagePredictAPIView(APIView):
    permission_classes = []
    def post(self, request):
        # 获取上传的图片
        image_file = request.FILES.get('file')
        if not image_file:
            return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 保存图片到 media/picture
        fs = FileSystemStorage(location=settings.MEDIA_ROOT + '/picture')
        filename = fs.save(image_file.name, image_file)
        file_url = fs.url(filename)

        # 构建图片完整路径
        image_path = os.path.join(settings.MEDIA_ROOT, 'picture', filename)

        # 调用预测脚本
        try:
            # 假设 judge.py 接受图片路径作为命令行参数，并输出预测结果
            result = subprocess.run([
                'bash', '-c',
                f"source /share/xyc/bigtiao/softvoting/venv/bin/activate && python /share/xyc/bigtiao/softvoting/judge.py {image_path}"
            ], capture_output=True, text=True)
            prediction = result.stdout.strip()
            # 检查错误
            # prediction = result.stderr.strip()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 返回预测结果
        return Response({"file_url": file_url, "prediction": prediction,"img":image_path}, status=status.HTTP_200_OK)