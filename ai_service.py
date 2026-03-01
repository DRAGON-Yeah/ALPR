import os
import requests
import base64
import json
from typing import Dict

class AIService:
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'ollama')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'qwen3-vl:8b')
        self.minimax_api_key = os.getenv('MINIMAX_API_KEY', '')
        self.minimax_group_id = os.getenv('MINIMAX_GROUP_ID', '')
    
    def recognize_plate(self, filepath: str, image_base64: str) -> Dict:
        """识别车牌号"""
        try:
            if self.provider == 'ollama':
                return self._recognize_with_ollama(filepath, image_base64)
            elif self.provider == 'minimax':
                return self._recognize_with_minimax(image_base64)
            else:
                return {'code': '10', 'message': f'不支持的AI提供商: {self.provider}'}
        except Exception as e:
            return {'code': '99', 'message': f'识别失败: {str(e)}'}
    
    def _recognize_with_ollama(self, filepath: str, image_base64: str) -> Dict:
        """使用Ollama进行识别"""
        try:
            url = f"{self.ollama_base_url}/api/generate"
            
            prompt = """请识别图片中的车牌号码。
要求：
1. 只返回JSON格式的结果
2. 如果识别成功，返回：{"code":"0", "plate_number":"车牌号", "message":"解析完成"}
3. 如果识别失败，返回：{"code":"1", "plate_number":"", "message":"未识别到车牌"}
4. 车牌号格式示例：粤A5A66A

请直接返回JSON，不要有其他文字。"""
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('response', '')
            
            # 尝试解析JSON响应
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
                
                parsed_result = json.loads(response_text)
                return parsed_result
            except json.JSONDecodeError:
                # 如果无法解析JSON，尝试从文本中提取车牌号
                return self._extract_plate_from_text(response_text)
        
        except requests.exceptions.RequestException as e:
            return {'code': '11', 'message': f'Ollama服务连接失败: {str(e)}'}
        except Exception as e:
            return {'code': '12', 'message': f'Ollama识别错误: {str(e)}'}
    
    def _recognize_with_minimax(self, image_base64: str) -> Dict:
        """使用MiniMax进行识别"""
        try:
            url = "https://api.minimax.io/v1/text/chatcompletion_v2"
            
            headers = {
                "Authorization": f"Bearer {self.minimax_api_key}",
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
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 尝试解析JSON响应
            try:
                response_text = response_text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                parsed_result = json.loads(response_text)
                return parsed_result
            except json.JSONDecodeError:
                return self._extract_plate_from_text(response_text)
        
        except requests.exceptions.RequestException as e:
            return {'code': '13', 'message': f'MiniMax服务连接失败: {str(e)}'}
        except Exception as e:
            return {'code': '14', 'message': f'MiniMax识别错误: {str(e)}'}
    
    def _extract_plate_from_text(self, text: str) -> Dict:
        """从文本中提取车牌号（备用方案）"""
        import re
        # 中国车牌号正则表达式
        pattern = r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-Z0-9]{5}'
        matches = re.findall(pattern, text)
        
        if matches:
            return {
                'code': '0',
                'plate_number': matches[0],
                'message': '解析完成'
            }
        else:
            return {
                'code': '1',
                'plate_number': '',
                'message': '未识别到车牌'
            }
