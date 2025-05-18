from django.db import models

class gps_cluster(models.Model):
    class Meta:
        verbose_name = '定位聚类'
        verbose_name_plural = '定位聚类表'
    username = models.CharField(max_length=10, verbose_name="用户名")
    cluster_name = models.CharField(max_length=10, verbose_name="聚类名称",blank=True)
    label = models.IntegerField(blank=True,null=True, verbose_name="聚类标签")
    timestamp = models.DateTimeField(auto_now=True, verbose_name="时间戳")
    longitude = models.FloatField(default=0.0, verbose_name="经度")
    latitude = models.FloatField(default=0.0, verbose_name="纬度") 

class bt_cluster(models.Model):
    class Meta:
        verbose_name = '蓝牙聚类'
        verbose_name_plural = '蓝牙聚类表'
    username = models.CharField(max_length=10, verbose_name="用户名")
    label = models.CharField(max_length=10, verbose_name="聚类名称",blank=True)
    timestamp = models.DateTimeField(auto_now=True, verbose_name="时间戳")
    bt_device = models.CharField(max_length=1500000, verbose_name="蓝牙连接设备")
