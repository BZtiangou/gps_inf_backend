from django.db import models

class Survey(models.Model):
    class Meta:
        verbose_name = '调查问卷'
        verbose_name_plural = '调查问卷表'
    survey_id = models.AutoField(primary_key=True,verbose_name="问卷ID")
    title = models.CharField(max_length=200,verbose_name="问卷标题")
    description = models.TextField(verbose_name="问卷描述",blank=True)
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    questions= models.CharField(max_length=200,verbose_name="问卷包含的问题ID")
    # 触发方式，如 'daily', 'weekly', 'monthly'
    trigger = models.CharField(max_length=50, verbose_name="问卷的触发方式", choices=[
        ('daily', '每天'),
        ('weekly', '每周'),
        ('monthly', '每月')
    ])
    # 触发时间
    trigger_time = models.TimeField(verbose_name="问卷触发时间")
    def __str__(self):
        return f"{self.title} - {self.trigger} at {self.trigger_time}"

class Question(models.Model):
    class Meta:
        verbose_name = '问题'
        verbose_name_plural = '问题表'
    question_id = models.AutoField(primary_key=True,verbose_name="问题ID")
    question_text = models.CharField(max_length=200,verbose_name="问题文本")
    question_type = models.CharField(max_length=20, choices=[('text', 'Text'), ('choice', 'Choice'), ('rating', 'Rating')],verbose_name="问题类型")
    choices = models.TextField(null=True, blank=True,verbose_name="选择项")
    question_group = models.CharField(max_length=200,verbose_name="问题分组")

class Answer(models.Model):
    class Meta:
        verbose_name = '问卷回答'
        verbose_name_plural = '问卷回答表'
    response_id = models.AutoField(primary_key=True,verbose_name="响应ID")
    survey_id = models.IntegerField(verbose_name="问卷ID")
    question_id = models.IntegerField(verbose_name="问题ID")
    username = models.CharField(max_length=20,verbose_name="回答者用户名")
    answer_text = models.TextField(verbose_name="回答文本")
    response_date = models.DateTimeField(auto_now_add=True,verbose_name="响应日期")
