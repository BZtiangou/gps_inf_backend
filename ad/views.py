from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image
import subprocess
import os

class ImagePredictAPIView(APIView):
    permission_classes = []

    # def check_image_header(self, file):
    #     header = file.read(10)
    #     file.seek(0)  # 重置文件指针位置
    #     return (
    #         header.startswith(b'\xff\xd8\xff') or  # JPEG
    #         header.startswith(b'\x89PNG\r\n\x1a\n') or  # PNG
    #         header.startswith(b'GIF87a') or
    #         header.startswith(b'GIF89a')  # GIF
    #     )

    def process_image(self, image_file):
        try:
            img = Image.open(image_file)
            img.verify()  # 验证图像
            img.close()
        except (IOError, SyntaxError) as e:
            return False
        return True

    def post(self, request):
        # 获取上传的图片
        image_file = request.FILES.get('file')
        if not image_file:
            return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查文件MIME类型
        if image_file.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
            return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

        # # 检查图片文件头
        # if not self.check_image_header(image_file):
        #     return Response({"error": "File is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)

        # 使用Pillow验证图像
        # if not self.process_image(image_file):
        #     return Response({"error": "Invalid image"}, status=status.HTTP_400_BAD_REQUEST)

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