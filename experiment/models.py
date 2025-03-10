from django.db import models

# 基础传感器配置抽象类
class SensorBase(models.Model):
    class Meta:
        abstract = True
    
    @classmethod
    def create_sensor_fields(cls, prefix, mode_choices, interval_choices):
        # 创建通用传感器字段的方法保持不变
        return (
            models.CharField(
                max_length=16,
                verbose_name=f"{prefix}监听模式",
                choices=mode_choices,
                default="onchange",
                name=f"{prefix}_mode"
            ),
            models.CharField(
                max_length=16,
                verbose_name=f"{prefix}间隔模式", 
                choices=interval_choices,
                default="normal",
                name=f"{prefix}_interval"
            )
        )

# GPS配置抽象类
class GpsConfig(models.Model):
    class Meta:
        abstract = True
    
    gps_frequency = models.IntegerField(verbose_name="GPS调用间隔(分钟)", default=-1)
    gps_altitude = models.BooleanField(verbose_name="是否记录海拔高度", default=False)
    gps_accuracy = models.FloatField(verbose_name="GPS 精度要求（米）", default=5.0)
    gps_isHighAccuracy = models.BooleanField(verbose_name="是否使用高精度模式", default=True)
    gps_geocode = models.BooleanField(verbose_name="是否获取地理编码信息", default=False)
    gps_timeout = models.IntegerField(verbose_name="GPS 获取超时时间（秒）", default=30)

# 蓝牙配置抽象类
class BluetoothConfig(models.Model):
    class Meta:
        abstract = True
    
    bt_frequency = models.IntegerField(verbose_name="蓝牙调用频率(分钟)", default=-1)
    bt_services = models.JSONField(verbose_name="扫描的蓝牙服务 UUID", default=list, blank=True)
    bt_allowDuplicatesKey = models.BooleanField(verbose_name="是否允许重复蓝牙数据", default=False)
    bt_interval = models.IntegerField(verbose_name="蓝牙扫描间隔（秒）", default=5)
    bt_powerLevel = models.CharField(
        max_length=16, 
        verbose_name="蓝牙功率级别", 
        choices=[("low", "低功耗"), ("medium", "中等功耗"), ("high", "高功耗")],
        default="medium"
    )

# 传感器配置类保持原样
class GyroSensor(SensorBase):
    (gyro_mode, gyro_interval) = SensorBase.create_sensor_fields(
        prefix="陀螺仪",
        mode_choices=[("onchange","监听变化值"), ("nochange","无需变化的监听")],
        interval_choices=[("normal", "普通模式"), ("game", "游戏模式"), ("ui", "ui模式")]
    )
    class Meta:
        abstract = True

class AccSensor(SensorBase):
    (acc_mode, acc_interval) = SensorBase.create_sensor_fields(
        prefix="加速度计",
        mode_choices=[("onchange","监听变化值"), ("nochange","无需变化的监听")],
        interval_choices=[("normal", "普通模式"), ("game", "游戏模式"), ("ui", "ui模式")]
    )
    class Meta:
        abstract = True

# 最终的Protocol模型
class Protocol(GyroSensor, AccSensor, GpsConfig, BluetoothConfig, models.Model):
    class Meta:
        verbose_name = '协议'
        verbose_name_plural = '协议表'
    
    creator = models.CharField(max_length=64, verbose_name="协议创建者", default="")
    protocol_name= models.CharField(max_length=255, verbose_name="协议名称")



class Trigger(models.Model):
    class Meta:
        verbose_name = "触发器"
        verbose_name_plural = "触发器表"

    TRIGGER_TYPES = [
        ("Location", "位置触发"),
        ("Regular Time", "定时触发"),
    ]

    trigger_type = models.CharField(
        max_length=32, 
        choices=TRIGGER_TYPES, 
        verbose_name="触发类型"
    )
    regular_time_option = models.CharField(
        max_length=32, 
        verbose_name="定时选项", 
        null=True, 
        blank=True
    )  # 例如 "Daily"
    specific_time = models.TimeField(
        verbose_name="具体时间", 
        null=True, 
        blank=True
    )  # 例如 00:38


class Survey(models.Model):
    class Meta:
        verbose_name = "调查问卷"
        verbose_name_plural = "调查问卷表"

    protocol = models.ForeignKey(
        Protocol, 
        on_delete=models.CASCADE,
        related_name='surveys', 
        verbose_name="关联协议"
    )  # 关联实验协议
    survey_name = models.CharField(max_length=255, verbose_name="问卷名称")
    description = models.TextField(verbose_name="问卷描述", blank=True)
    trigger = models.OneToOneField(
        Trigger, 
        on_delete=models.CASCADE, 
        verbose_name="触发器"
    )  # 每个 Survey 只有一个触发器


class SurveyItem(models.Model):
    class Meta:
        verbose_name = "问卷项"
        verbose_name_plural = "问卷项表"

    ITEM_TYPES = [
        ("q_and_a", "问答题"),
        ("choice", "单选题"),
        ("multiple_choice", "多选题"),
        ("fill_in_blank", "填空题"),
        ("rating", "评分题"),
        ("matrix", "矩阵题"),
        ("ranking", "排序题"),
        ("file_upload", "文件上传"),
    ]

    survey = models.ForeignKey(
        Survey, 
        on_delete=models.CASCADE, 
        verbose_name="所属问卷",
        related_name="items"
    )
    type = models.CharField(
        max_length=32, 
        choices=ITEM_TYPES, 
        verbose_name="问题类型"
    )
    label = models.CharField(max_length=255, verbose_name="标签")
    description = models.TextField(verbose_name="问题描述", blank=True)
    question = models.TextField(verbose_name="问题内容")
    choices = models.TextField(
        verbose_name="选项列表", 
        blank=True, 
        default="",
        help_text="多个选项用英文分号 `;` 分隔，例如: 选项A;选项B;选项C"
    )  # 用 ; 分隔选项，如 "选项1;选项2;选项3"

class Experiment(models.Model):
    # 状态常量定义
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    TERMINATED = 'Terminated'
    STATE_CHOICES = [
        (ACTIVE, '进行中'),
        (INACTIVE, '未激活'),
        (TERMINATED, '已终止'),
    ]
    class Meta:
        verbose_name = '实验'
        verbose_name_plural = '实验表'
    start_time = models.DateTimeField(verbose_name="实验开始时间")
    end_time = models.DateTimeField(verbose_name="实验结束时间")
    exp_id = models.AutoField(primary_key=True, verbose_name="实验ID")
    exp_title = models.CharField(max_length=64, verbose_name="实验名称", default="")
    exp_creator = models.CharField(max_length=64, verbose_name="实验创建者", default="")
    exp_code = models.CharField(max_length=255, verbose_name="实验邀请码", default="")
    exp_staff = models.CharField(max_length=64, verbose_name="实验管理者", default="", blank=True)
    exp_state = models.CharField(
        max_length=16, 
        verbose_name="实验状态", 
        choices=STATE_CHOICES, 
        default=INACTIVE 
    )
    description = models.CharField(max_length=255, verbose_name="实验描述", default="")
    participants_name = models.CharField(max_length=64, verbose_name="实验参与者", default="", blank=True)
    protocol_name= models.CharField(max_length=255, verbose_name="实验选择的协议名称")
    protocol_id = models.IntegerField(verbose_name="协议ID")
    def __str__(self):
        return f"{self.exp_name} ({self.exp_id})"


class exp_history(models.Model):
    class Meta:
        verbose_name = '实验历史'
        verbose_name_plural = '实验历史表'
    username = models.CharField(max_length=10, verbose_name="用户名")
    exp_id = models.IntegerField(verbose_name="实验ID")
    exp_title = models.CharField(max_length=64, verbose_name="实验名称", default="", blank=True)
    description = models.CharField(max_length=255, verbose_name="实验描述", default="")
    join_time = models.DateTimeField(verbose_name="参加时间", auto_now_add=True)
    exit_time = models.DateTimeField(verbose_name="退出时间", null=True, blank=True)
