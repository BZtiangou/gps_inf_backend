from datetime import timedelta
# from account.serializers import MyTokenObtainPairSerializer

# 自定义参数
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    # "TOKEN_OBTAIN_SERIALIZER": MyTokenObtainPairSerializer,
}

