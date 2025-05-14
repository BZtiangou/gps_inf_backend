import requests
import json
import os
import dotenv

def call_deepseek_chat(prompt, model="deepseek-chat", temperature=0.3, max_tokens=2048):
    """
    调用DeepSeek聊天API
    
    参数:
    prompt : str - 用户输入的提示内容
    model : str - 使用的模型名称(默认: deepseek-chat)
    temperature : float - 生成多样性(默认: 0.3)
    max_tokens : int - 最大生成token数(默认: 2048)
    
    返回:
    str - API返回的完整响应内容
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DeepSeek_API_Key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            DeepSeek_API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        
        # 检查HTTP状态码
        response.raise_for_status()
        
        # 解析JSON响应
        result = response.json()
        
        # 提取助手的回复内容
        if result.get("choices"):
            return result["choices"][0]["message"]["content"]
        return "Error: No response content"
        
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"Other error occurred: {err}"


# 使用示例
if __name__ == "__main__":
    # 配置信息 - 替换成你自己的信息
    dotenv.load_dotenv(dotenv_path= "/var/www/gps_inf/.env", verbose=True)
    DeepSeek_API_Key = os.environ.get("DEEPSEEK_API_KEY")
    DeepSeek_API_URL = "https://api.deepseek.com/v1/chat/completions"
    # test_prompt = "你好，请用Python写一个快速排序算法"
    # response = call_deepseek_chat(test_prompt)