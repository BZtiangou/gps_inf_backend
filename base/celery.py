# Celery 配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # 使用 Redis 作为消息代理
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'Asia/Shanghai'  # 设置时区
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'