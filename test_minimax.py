#!/usr/bin/env python3
"""测试 MiniMax API 连接和图像识别能力"""

import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

def test_minimax_text_api():
    """测试 MiniMax 文本 API 连接"""
    print("\n正在测试 MiniMax 文本 API 连接...")
    
    api_key = os.getenv('MINIMAX_API_KEY')
    
    if not api_key:
        print("❌ 未找到 MINIMAX_API_KEY")
        return False
    
    print(f"✓ API Key: {api_key[:20]}...")
    
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
                "content": "你好，请用一句话介绍你自己。"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and result['choices'] and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print(f"✓ API 连接成功！")
                print(f"响应: {content[:100]}...")
                return True
            else:
                print(f"❌ 响应格式异常")
                return False
        else:
            print(f"❌ API 返回错误: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

def test_model_vision(api_key, model_name, test_image_base64):
    """测试指定模型是否支持图像识别"""
    print(f"\n测试模型: {model_name}")
    
    url = "https://api.minimax.io/v1/text/chatcompletion_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请描述这张图片中的内容"
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
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and result['choices'] and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                if "没有看到" in content or "无法" in content or "不能" in content or "抱歉" in content:
                    print(f"  ✗ 不支持图像")
                    print(f"    响应: {content[:80]}...")
                    return False
                else:
                    print(f"  ✓ 支持图像！")
                    print(f"    响应: {content[:80]}...")
                    return True
            else:
                print(f"  ✗ 响应格式异常")
                return False
        else:
            error_text = response.text
            if "unknown model" in error_text.lower() or "model not found" in error_text.lower():
                print(f"  ✗ 模型不存在")
            else:
                print(f"  ✗ 请求失败: {response.status_code}")
                print(f"    错误: {error_text[:100]}")
            return False
    except Exception as e:
        print(f"  ✗ 测试失败: {str(e)}")
        return False

def test_minimax_vision_capability():
    """测试 MiniMax 各个模型是否支持图像识别"""
    print("\n" + "=" * 60)
    print("测试 MiniMax 图像识别能力")
    print("=" * 60)
    
    api_key = os.getenv('MINIMAX_API_KEY')
    
    # 读取测试图片
    test_image = "car2.png"
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return None
    
    print(f"✓ 找到测试图片: {test_image}")
    
    with open(test_image, 'rb') as f:
        image_data = f.read()
        test_image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    print(f"✓ 图片已转换为 base64 (大小: {len(image_data)} 字节)")
    
    # 测试多个模型
    models_to_test = [
        "MiniMax-M2.5",
        "MiniMax-M2.1",
        "MiniMax-M2",
    ]
    
    print(f"\n将测试以下模型:")
    for model in models_to_test:
        print(f"  - {model}")
    
    print("\n" + "-" * 60)
    
    results = {}
    for model in models_to_test:
        results[model] = test_model_vision(api_key, model, test_image_base64)
    
    return results

def main():
    """主函数"""
    print("=" * 60)
    print("🚗 MiniMax API 测试工具")
    print("=" * 60)
    
    # 测试文本 API
    print("\n" + "=" * 60)
    print("步骤 1: 测试文本 API 连接")
    print("=" * 60)
    text_api_works = test_minimax_text_api()
    
    if not text_api_works:
        print("\n" + "=" * 60)
        print("❌ MiniMax 文本 API 连接失败")
        print("请检查:")
        print("1. MINIMAX_API_KEY 是否正确配置")
        print("2. 网络连接是否正常")
        print("=" * 60)
        return
    
    # 测试图像识别能力
    vision_results = test_minimax_vision_capability()
    
    if vision_results is None:
        print("\n❌ 无法进行图像识别测试")
        return
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"文本 API: {'✓ 正常' if text_api_works else '✗ 失败'}")
    print(f"\n图像识别能力:")
    
    any_vision_support = False
    for model, supports_vision in vision_results.items():
        status = "✓ 支持" if supports_vision else "✗ 不支持"
        print(f"  {model}: {status}")
        if supports_vision:
            any_vision_support = True
    
    if not any_vision_support:
        print("\n" + "=" * 60)
        print("⚠️  重要提示")
        print("=" * 60)
        print("MiniMax 的文本模型 (MiniMax-M2.5) 目前不支持直接的图像输入。")
        print("\n建议使用以下方案进行车牌识别:")
        print("1. 使用 Ollama 本地模型 (qwen3-vl:8b)")
        print("   - 修改 .env 文件: AI_PROVIDER=ollama")
        print("   - 确保 Ollama 服务运行: ollama serve")
        print("   - 运行测试: python test_car_image.py")
        print("\n2. 或者使用 MiniMax 的文件上传 API")
        print("   - 先上传图片获取 file_id")
        print("   - 然后在对话中引用 file_id")
        print("   - 这需要修改代码实现")
    else:
        print("\n✓ 找到支持图像识别的模型！")
        print("支持的模型:")
        for model, supports in vision_results.items():
            if supports:
                print(f"  - {model}")
        print("\n可以使用这些模型进行车牌识别。")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
