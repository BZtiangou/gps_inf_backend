from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理表'

    email = models.EmailField(verbose_name="邮箱地址")
    device = models.CharField(max_length=150, default="", verbose_name="设备及其操作系统", blank=True)
    phone_number = models.CharField(max_length=11, verbose_name="手机号码")
    gender = models.CharField(
        max_length=10,
        choices=(("male", "男"), ("female", "女")),
        verbose_name="性别",
        default="未知"
    )
    name = models.CharField(max_length=20, verbose_name="真名", default="")
    exp_state = models.CharField(max_length=64, verbose_name="实验状态", default="inactive")
    exp_title = models.CharField(max_length=64, verbose_name="实验名称", default="", blank=True)
    exp_id = models.IntegerField(verbose_name="实验ID", default=-1)
    familiar_word_ids = models.TextField(verbose_name="熟悉的单词ID", default="", blank=True)
    unfamiliar_word_ids = models.TextField(verbose_name="不熟悉的单词ID", default="", blank=True)
    call_times = models.IntegerField(verbose_name="调用AI次数",default=0)
