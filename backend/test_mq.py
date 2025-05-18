import os
import sys
import pika
import django

# 设置Django环境
sys.path.append('/var/www/gps_inf')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# 导入Django设置
from django.conf import settings

def test_rabbitmq_connection():
    """测试RabbitMQ连接"""
    print("=== RabbitMQ连接测试 ===")
    print(f"主机: {settings.RABBITMQ_HOST}")
    print(f"端口: {settings.RABBITMQ_PORT}")
    print(f"用户: {settings.RABBITMQ_USER}")
    print(f"虚拟主机: {settings.RABBITMQ_VHOST}")
    
    try:
        # 创建连接参数
        credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER, 
            settings.RABBITMQ_PASSWORD
        )
        
        connection_params = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=int(settings.RABBITMQ_PORT),
            virtual_host=settings.RABBITMQ_VHOST,
            credentials=credentials
        )
        
        # 创建连接
        connection = pika.BlockingConnection(connection_params)
        
        # 创建通道
        channel = connection.channel()
        
        # 声明一个测试队列
        test_queue = 'test_queue'
        channel.queue_declare(queue=test_queue)
        
        # 发送测试消息
        test_message = 'Hello RabbitMQ!'
        channel.basic_publish(
            exchange='',
            routing_key=test_queue,
            body=test_message
        )
        
        print(f"成功发送测试消息: '{test_message}'")
        
        # 接收测试消息
        method_frame, header_frame, body = channel.basic_get(test_queue)
        if method_frame:
            print(f"成功接收消息: '{body.decode()}'")
            channel.basic_ack(method_frame.delivery_tag)
        else:
            print("没有接收到消息")
        
        # 删除测试队列
        channel.queue_delete(test_queue)
        
        # 关闭连接
        connection.close()
        
        print("RabbitMQ连接测试成功!")
        return True
    
    except Exception as e:
        print(f"连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_rabbitmq_connection()