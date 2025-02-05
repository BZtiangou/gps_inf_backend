# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from dic.models import WordEntry
from .serializers import WordEntrySerializer
from account.models import CustomUser
from rest_framework import status
import random
from rest_framework.permissions import IsAuthenticated

class GetWordInfoApi(APIView):
    permission_classes=[]
    def get(self, request):
        words = WordEntry.objects.all()[:100]
        serializer = WordEntrySerializer(words, many=True)
        return Response(serializer.data)


class RandomUnfamiliarWordApi(APIView):
    permission_classes = [IsAuthenticated]  # 确保用户已登录才能访问该接口
    def get(self, request):
        # 获取当前用户
        username = request.user.username
        user = CustomUser.objects.get(username=username)
        # 获取用户熟悉的单词ID列表，转换为 Python 列表
        familiar_ids = user.familiar_word_ids.split(',') if user.familiar_word_ids else []
        # 查询所有不在熟悉单词ID列表中的单词
        available_words = WordEntry.objects.exclude(id__in=familiar_ids)

        # 如果没有可用的单词，返回提示信息
        if not available_words.exists():
            return Response({"detail": "没有找到不在熟悉列表中的单词"}, status=404)

        # 随机选择一个单词
        random_word = random.choice(available_words)

        # 序列化并返回单词数据
        serializer = WordEntrySerializer(random_word)
        return Response(serializer.data)

class RandomfamiliarWordApi(APIView):
    permission_classes = [IsAuthenticated]  # 确保用户已登录才能访问该接口
    def get(self, request):
        # 获取当前用户
        username = request.user.username
        user = CustomUser.objects.get(username=username)
        unfamiliar_ids = user.unfamiliar_word_ids.split(',') if user.unfamiliar_word_ids else []
        available_words = WordEntry.objects.exclude(id__in=unfamiliar_ids)

        # 如果没有可用的单词，返回提示信息
        if not available_words.exists():
            return Response({"detail": "没有找到在熟悉列表中的单词"}, status=404)
        random_word = random.choice(available_words)
        # 序列化并返回单词数据
        serializer = WordEntrySerializer(random_word)
        return Response(serializer.data)

class UpdateWordFamiliarityApi(APIView):
    permission_classes = [IsAuthenticated]  # 确保用户已登录才能访问该接口

    def post(self, request):
        # 获取 POST 请求参数
        word_id = request.data.get('word')
        is_familiar = request.data.get('is_familiar')

        # 检查参数是否完整
        if not word_id or not is_familiar:
            return Response({"detail": "缺少必需的参数 'word' 或 'is_familiar'"}, status=status.HTTP_400_BAD_REQUEST)

        # 获取当前用户
        user = request.user

        # 确保 word_id 是字符串类型（因为存储在 TextField 中的是字符串）
        word_id = str(word_id)

        # 处理 'familiar' 情况
        if is_familiar == 'familiar':
            # 更新熟悉的单词 ID 列表
            familiar_ids = user.familiar_word_ids.split(',') if user.familiar_word_ids else []
            if word_id not in familiar_ids:
                familiar_ids.append(word_id)
                user.familiar_word_ids = ','.join(familiar_ids)

            # 从不熟悉的单词列表中移除该单词（避免冲突）
            unfamiliar_ids = user.unfamiliar_word_ids.split(',') if user.unfamiliar_word_ids else []
            if word_id in unfamiliar_ids:
                unfamiliar_ids.remove(word_id)
                user.unfamiliar_word_ids = ','.join(unfamiliar_ids)

        # 处理 'unfamiliar' 情况
        elif is_familiar == 'unfamiliar':
            # 更新不熟悉的单词 ID 列表
            unfamiliar_ids = user.unfamiliar_word_ids.split(',') if user.unfamiliar_word_ids else []
            if word_id not in unfamiliar_ids:
                unfamiliar_ids.append(word_id)
                user.unfamiliar_word_ids = ','.join(unfamiliar_ids)

            # 从熟悉的单词列表中移除该单词（避免冲突）
            familiar_ids = user.familiar_word_ids.split(',') if user.familiar_word_ids else []
            if word_id in familiar_ids:
                familiar_ids.remove(word_id)
                user.familiar_word_ids = ','.join(familiar_ids)

        else:
            return Response({"detail": "参数 'is_familiar' 必须是 'familiar' 或 'unfamiliar'"}, status=status.HTTP_400_BAD_REQUEST)

        # 保存用户信息
        user.save()

        return Response({"detail": "单词熟悉度已更新"}, status=status.HTTP_200_OK)
