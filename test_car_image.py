#!/usr/bin/env python3
"""车牌识别系统 - 图片测试工具"""

import os
import sys
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

# 配置
TEST_IMAGE = "car2.png"  # 测试图片文件名
BASE_URL = "http://127.0.0.1:5001"
TIMEOUT = 120

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def check_image_file(image_path):
    """检查图片文件是否存在"""
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        print(f"💡 请将测试图片命名为 '{TEST_IMAGE}' 并放在当前目录")
        return False
    
    file_size = os.path.getsize(image_path)
    print(f"✅ 找到图片文件: {image_path}")
    print(f"📊 文件大小: {file_size / 1024:.2f} KB")
    
    if file_size > 16 * 1024 * 1024:
        print(f"⚠️  警告: 文件大小超过 16MB 限制")
        return False
    
    return True

def read_image_base64(image_path):
    """读取图片并转换为 base64"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        print(f"✅ 图片已转换为 base64 (长度: {len(image_base64)})")
        return image_base64
    except Exception as e:
        print(f"❌ 读取图片失败: {str(e)}")
        return None

def test_minimax_api(image_base64):
    """测试 MiniMax API 直接调用"""
    print_section("测试 MiniMax API 直接调用")
    
    api_key = os.getenv('MINIMAX_API_KEY')
    if not api_key:
        print("❌ 未配置 MINIMAX_API_KEY")
        print("💡 请在 .env 文件中配置 MINIMAX_API_KEY")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...")
    
    url = "https://api.minimax.io/v1/text/chatcompletion_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "MiniMax-M2.5",
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
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    }
    
    print(f"\n📤 正在调用 MiniMax API...")
    print(f"🔗 URL: {url}")
    print(f"🧠 模型: {payload['model']}")
    print(f"⏱️  超时: {TIMEOUT}秒")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        print(f"\n📥 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 调用成功！")
            
            # 提取识别结果
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print(f"\n📝 原始响应:")
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
                    print(f"\n🎯 解析后的结果:")
                    print(json.dumps(parsed, indent=2, ensure_ascii=False))
                    
                    if parsed.get('code') == '0':
                        print(f"\n🎉 识别成功！车牌号: {parsed.get('plate_number')}")
                        return True
                    else:
                        print(f"\n⚠️  识别失败: {parsed.get('message')}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"\n⚠️  无法解析为JSON: {e}")
                    print(f"原始内容: {content}")
                    return False
            else:
                print("❌ 响应格式错误")
                return False
        else:
            print(f"❌ API 返回错误")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（{TIMEOUT}秒）")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ollama_api(image_base64):
    """测试 Ollama API 直接调用"""
    print_section("测试 Ollama API 直接调用")
    
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'qwen3-vl:8b')
    
    print(f"🔗 Ollama URL: {ollama_url}")
    print(f"🧠 模型: {ollama_model}")
    
    url = f"{ollama_url}/api/generate"
    
    payload = {
        "model": ollama_model,
        "prompt": """请识别图片中的车牌号码。
要求：
1. 只返回JSON格式的结果
2. 如果识别成功，返回：{"code":"0", "plate_number":"车牌号", "message":"解析完成"}
3. 如果识别失败，返回：{"code":"1", "plate_number":"", "message":"未识别到车牌"}
4. 车牌号格式示例：粤A5A66A

请直接返回JSON，不要有其他文字。""",
        "images": [image_base64],
        "stream": False
    }
    
    print(f"\n📤 正在调用 Ollama API...")
    
    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        print(f"\n📥 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 调用成功！")
            
            response_text = result.get('response', '')
            print(f"\n📝 原始响应:")
            print(response_text)
            
            # 尝试解析JSON
            try:
                # 清理响应文本
                response_text = response_text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                parsed = json.loads(response_text)
                print(f"\n🎯 解析后的结果:")
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
                
                if parsed.get('code') == '0':
                    print(f"\n🎉 识别成功！车牌号: {parsed.get('plate_number')}")
                    return True
                else:
                    print(f"\n⚠️  识别失败: {parsed.get('message')}")
                    return False
            except json.JSONDecodeError as e:
                print(f"\n⚠️  无法解析为JSON: {e}")
                return False
        else:
            print(f"❌ API 返回错误")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 Ollama 服务")
        print(f"💡 请确保 Ollama 正在运行: ollama serve")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（{TIMEOUT}秒）")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return False

def test_local_api(image_path):
    """测试本地 Flask API"""
    print_section("测试本地 Flask API")
    
    print(f"🔗 API URL: {BASE_URL}/api/upload")
    
    try:
        # 检查服务是否运行
        try:
            requests.get(BASE_URL, timeout=5)
        except:
            print(f"❌ 无法连接到本地服务")
            print(f"💡 请先启动服务: ./manage.sh start")
            return False
        
        print("✅ 服务正在运行")
        
        # 上传图片
        print(f"\n📤 正在上传图片...")
        with open(image_path, 'rb') as f:
            files = {'image': (TEST_IMAGE, f, 'image/png')}
            response = requests.post(f'{BASE_URL}/api/upload', files=files, timeout=TIMEOUT)
        
        print(f"📥 状态码: {response.status_code}")
        result = response.json()
        
        print(f"\n📝 响应结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('code') == '0':
            print(f"\n🎉 本地API识别成功！")
            print(f"🆔 识别ID: {result.get('recognition_id')}")
            print(f"🚗 车牌号: {result.get('plate_number')}")
            return True
        else:
            print(f"\n⚠️  识别结果: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚗 车牌识别系统 - 图片测试工具")
    print("=" * 60)
    
    # 检查图片文件
    image_path = os.path.join(os.getcwd(), TEST_IMAGE)
    if not check_image_file(image_path):
        sys.exit(1)
    
    # 读取图片
    image_base64 = read_image_base64(image_path)
    if not image_base64:
        sys.exit(1)
    
    # 获取 AI 提供商配置
    ai_provider = os.getenv('AI_PROVIDER', 'ollama')
    print(f"\n🔧 当前 AI 提供商: {ai_provider}")
    
    results = {}
    
    # 测试对应的 AI API
    if ai_provider == 'minimax':
        results['MiniMax API'] = test_minimax_api(image_base64)
    elif ai_provider == 'ollama':
        results['Ollama API'] = test_ollama_api(image_base64)
    else:
        print(f"⚠️  未知的 AI 提供商: {ai_provider}")
    
    # 测试本地 Flask API
    results['本地 Flask API'] = test_local_api(image_path)
    
    # 打印测试总结
    print_section("测试总结")
    for name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    print("=" * 60)
    
    # 返回退出码
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
