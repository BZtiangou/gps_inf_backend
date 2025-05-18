import csv
from django.core.exceptions import ObjectDoesNotExist
from .models import WordEntry  

# CSV 文件字段的中文名称和英文名称
fields = {
    "word": {"en": "Word", "zh": "单词名称"},
    "phonetic": {"en": "Phonetic", "zh": "音标，以英语英标为主"},
    "definition": {"en": "Definition", "zh": "单词释义（英文），每行一个释义"},
    "translation": {"en": "Translation", "zh": "单词释义（中文），每行一个释义"},
    "pos": {"en": "Part of Speech", "zh": "词语位置，用 \"/\" 分割不同位置"},
    "collins": {"en": "Collins", "zh": "柯林斯星级"},
    "oxford": {"en": "Oxford", "zh": "是否是牛津三千核心词汇"},
    "tag": {"en": "Tag", "zh": "字符串标签：zk/中考，gk/高考，cet4/四级 等等标签，空格分割"},
    "bnc": {"en": "BNC", "zh": "英国国家语料库词频顺序"},
    "frq": {"en": "Frequency", "zh": "当代语料库词频顺序"},
    "exchange": {"en": "Exchange", "zh": "时态复数等变换，使用 \"/\" 分割不同项目"},
    "detail": {"en": "Detail", "zh": "json 扩展信息，字典形式保存例句（待添加）"},
    "audio": {"en": "Audio", "zh": "读音音频 url （待添加）"}
}

# 读取 CSV 文件并将数据保存到数据库
def import_words_to_db(csv_filename, num_words=3500):
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print("正在导入数据...")
            for i, row in enumerate(reader):
                if i >= num_words:
                    break
                try:
                    # 尝试获取已存在的单词条目
                    word_entry = WordEntry.objects.get(word=row['word'])
                    print(f"更新单词: {row['word']}")
                except ObjectDoesNotExist:
                    # 如果单词条目不存在，则创建新的条目
                    word_entry = WordEntry(
                        word=row['word'],
                        phonetic=row['phonetic'],
                        definition=row['definition'],
                        translation=row['translation'],
                        pos=row['pos'],
                        collins=row.get('collins', ''),
                        oxford=row.get('oxford') == '1',  # 假设 CSV 中用 '1' 表示 True
                        tag=row.get('tag', ''),
                        bnc=int(row.get('bnc', 0)),
                        frq=int(row.get('frq', 0)),
                        exchange=row.get('exchange', ''),
                        detail=row.get('detail', {}),
                        audio=row.get('audio', '')
                    )
                    print(f"创建单词: {row['word']}")
                word_entry.save()
            print("数据导入完成。")
    except FileNotFoundError:
        print("CSV 文件未找到，请确保文件位于同级目录下。")
    except Exception as e:
        print(f"读取 CSV 文件时发生错误：{e}")

# 调用函数
import_words_to_db('ecdict.csv')