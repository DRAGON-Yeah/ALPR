#!/usr/bin/env python3
"""测试 MiniMax API 连接"""

import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

def test_minimax_api():
    """测试 MiniMax API"""
    api_key = os.getenv('MINIMAX_API_KEY')
    
    if not api_key:
        print("❌ 未找到 MINIMAX_API_KEY")
        return False
    
    print(f"✓ API Key: {api_key[:20]}...")
    
    # 创建一个简单的测试图片（1x1 像素的白色图片）
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    url = "https://api.minimax.io/v1/text/chatcompletion_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "abab6.5-chat",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "这是什么图片？"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{test_image_base64}"
                        }
                    }
                ]
            }
        ]
    }
    
    print("\n正在测试 MiniMax API 连接...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ API 连接成功！")
            print(f"\n响应内容:")
            print(result)
            return True
        else:
            print(f"❌ API 返回错误")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("MiniMax API 连接测试")
    print("=" * 60)
    
    success = test_minimax_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 测试通过！可以使用 MiniMax API")
        print("\n访问 http://localhost:5001 开始使用车牌识别系统")
    else:
        print("✗ 测试失败，请检查 API Key 或网络连接")
    print("=" * 60)
