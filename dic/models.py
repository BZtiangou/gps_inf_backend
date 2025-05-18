from django.db import models

class WordEntry(models.Model):
    word = models.CharField(max_length=255, verbose_name="单词名称")
    phonetic = models.CharField(max_length=100, verbose_name="音标，以英语英标为主")
    definition = models.TextField(verbose_name="单词释义（英文），每行一个释义")
    translation = models.TextField(verbose_name="单词释义（中文），每行一个释义")
    pos = models.CharField(max_length=100, verbose_name="词语位置，用 \"/\" 分割不同位置")
    collins = models.CharField(max_length=10, blank=True, null=True, verbose_name="柯林斯星级")
    oxford = models.BooleanField(default=False, verbose_name="是否是牛津三千核心词汇")
    tag = models.CharField(max_length=100, verbose_name="字符串标签：zk/中考，gk/高考，cet4/四级 等等标签，空格分割")
    bnc = models.IntegerField(blank=True, null=True, verbose_name="英国国家语料库词频顺序")
    frq = models.IntegerField(blank=True, null=True, verbose_name="当代语料库词频顺序")
    exchange = models.CharField(max_length=255, verbose_name="时态复数等变换，使用 \"/\" 分割不同项目")
    detail = models.JSONField(null=True, blank=True, verbose_name="json 扩展信息，字典形式保存例句（待添加）")
    audio = models.URLField(max_length=255, blank=True, null=True, verbose_name="读音音频 url （待添加）")

    class Meta:
        verbose_name = "单词条目"
        verbose_name_plural = "单词条目"

    def __str__(self):
        return self.word