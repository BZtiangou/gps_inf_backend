from django.db import models

# Create your models here.
class PoseSource(models.Model):
    class Meta:
        verbose_name = '视频'
        verbose_name_plural = '姿势视频表'
    username = models.CharField(max_length=100,verbose_name="用户名")
    video = models.FileField(upload_to='videos/',verbose_name="视频路径")
    upload_date = models.DateTimeField(auto_now_add=True,verbose_name="上传时间")

    def __str__(self):
        return f"PoseSource: {self.video.name} uploaded on {self.upload_date}"
