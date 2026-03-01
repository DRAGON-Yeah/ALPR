#!/usr/bin/env python3
"""使用真实车牌图片测试系统"""

import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

def test_with_car_image():
    """使用车牌图片测试"""
    
    car_image_path = "/Users/womeng/Desktop/car.jpg"
    
    # 检查文件是否存在
    if not os.path.exists(car_image_path):
        print(f"❌ 图片文件不存在: {car_image_path}")
        return False
    
    print(f"✓ 找到图片文件: {car_image_path}")
    print(f"✓ 文件大小: {os.path.getsize(car_image_path) / 1024:.2f} KB")
    
    # 读取图片并转换为base64
    with open(car_image_path, 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    print(f"✓ 图片已转换为 base64 (长度: {len(image_base64)})")
    
    # 测试 MiniMax API
    api_key = os.getenv('MINIMAX_API_KEY')
    url = "https://api.minimax.io/v1/text/chatcompletion_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "MiniMax-01",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """请识别图片中的车牌号码。
要求：
1. 只返回JSON格式的结果
2. 如果识别成功，返回：{"code":"0", "plate_number":"车牌号", "message":"解析完成"}
3. 如果识别失败，返回：{"code":"1", "plate_number":"", "message":"未识别到车牌"}
4. 车牌号格式示例：粤A5A66A

请直接返回JSON，不要有其他文字。"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    }
    
    print("\n正在调用 MiniMax API 识别车牌...")
    print(f"API URL: {url}")
    print(f"模型: {payload['model']}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ API 调用成功！")
            print("\n完整响应:")
            print("=" * 60)
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("=" * 60)
            
            # 提取识别结果
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print(f"\n识别结果内容:")
                print(content)
                
                # 尝试解析JSON
                try:
                    # 清理响应文本
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.startswith('```'):
                        content = content[3:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()
                    
                    parsed = json.loads(content)
                    print(f"\n解析后的结果:")
                    print(json.dumps(parsed, indent=2, ensure_ascii=False))
                    
                    if parsed.get('code') == '0':
                        print(f"\n🎉 识别成功！车牌号: {parsed.get('plate_number')}")
                    else:
                        print(f"\n⚠️ 识别失败: {parsed.get('message')}")
                except json.JSONDecodeError as e:
                    print(f"\n⚠️ 无法解析为JSON: {e}")
            
            return True
        else:
            print(f"❌ API 返回错误")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（120秒）")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_local_api():
    """测试本地 Flask API"""
    print("\n" + "=" * 60)
    print("测试本地 Flask API")
    print("=" * 60)
    
    car_image_path = "/Users/womeng/Desktop/car.jpg"
    
    if not os.path.exists(car_image_path):
        print(f"❌ 图片文件不存在: {car_image_path}")
        return False
    
    try:
        # 上传图片到本地API
        with open(car_image_path, 'rb') as f:
            files = {'image': ('car.jpg', f, 'image/jpeg')}
            response = requests.post('http://localhost:5001/api/upload', files=files, timeout=120)
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        
        print("\n响应结果:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('code') == '0':
            print(f"\n🎉 本地API识别成功！车牌号: {result.get('plate_number')}")
            return True
        else:
            print(f"\n⚠️ 识别结果: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("车牌识别系统 - 真实图片测试")
    print("=" * 60)
    
    # 测试 MiniMax API
    print("\n[1] 测试 MiniMax API 直接调用")
    print("=" * 60)
    minimax_success = test_with_car_image()
    
    # 测试本地 Flask API
    print("\n[2] 测试本地 Flask API")
    print("=" * 60)
    local_success = test_local_api()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"MiniMax API: {'✓ 通过' if minimax_success else '✗ 失败'}")
    print(f"本地 Flask API: {'✓ 通过' if local_success else '✗ 失败'}")
    print("=" * 60)
