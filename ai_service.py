import os
import requests
import base64
import json
import logging
from typing import Dict

# 配置日志
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'ollama')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'qwen3-vl:8b')
        self.minimax_api_key = os.getenv('MINIMAX_API_KEY', '')
        self.minimax_group_id = os.getenv('MINIMAX_GROUP_ID', '')
        
        logger.info("🤖 AI服务初始化完成")
        logger.info(f"🔧 AI提供商: {self.provider}")
        if self.provider == 'ollama':
            logger.info(f"🔗 Ollama地址: {self.ollama_base_url}")
            logger.info(f"🧠 Ollama模型: {self.ollama_model}")
        elif self.provider == 'minimax':
            logger.info(f"🔑 MiniMax API Key: {'已配置' if self.minimax_api_key else '未配置'}")
            logger.info(f"🆔 MiniMax Group ID: {self.minimax_group_id if self.minimax_group_id else '未配置'}")
    
    def recognize_plate(self, filepath: str, image_base64: str) -> Dict:
        """识别车牌号"""
        try:
            logger.info(f"🎯 开始识别车牌，使用提供商: {self.provider}")
            logger.info(f"📁 图片路径: {filepath}")
            
            if self.provider == 'ollama':
                return self._recognize_with_ollama(filepath, image_base64)
            elif self.provider == 'minimax':
                return self._recognize_with_minimax(image_base64)
            else:
                logger.error(f"❌ 不支持的AI提供商: {self.provider}")
                return {'code': '10', 'message': f'不支持的AI提供商: {self.provider}'}
        except Exception as e:
            logger.error(f"❌ 识别失败: {str(e)}", exc_info=True)
            return {'code': '99', 'message': f'识别失败: {str(e)}'}
    
    def _recognize_with_ollama(self, filepath: str, image_base64: str) -> Dict:
        """使用Ollama进行识别"""
        try:
            logger.info("🔵 使用Ollama进行识别...")
            url = f"{self.ollama_base_url}/api/generate"
            logger.info(f"🔗 请求URL: {url}")
            
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
            
            logger.info(f"📤 发送请求到Ollama，模型: {self.ollama_model}")
            logger.info(f"⏱️  等待Ollama响应（超时60秒）...")
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            logger.info(f"✅ 收到Ollama响应，状态码: {response.status_code}")
            
            result = response.json()
            response_text = result.get('response', '')
            logger.info(f"📝 Ollama原始响应: {response_text[:200]}...")
            
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
                
                logger.info(f"🔄 清理后的响应: {response_text}")
                
                parsed_result = json.loads(response_text)
                logger.info(f"✅ JSON解析成功: {parsed_result}")
                return parsed_result
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️  JSON解析失败: {str(e)}")
                logger.info("🔍 尝试从文本中提取车牌号...")
                # 如果无法解析JSON，尝试从文本中提取车牌号
                return self._extract_plate_from_text(response_text)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ollama服务连接失败: {str(e)}")
            return {'code': '11', 'message': f'Ollama服务连接失败: {str(e)}'}
        except Exception as e:
            logger.error(f"❌ Ollama识别错误: {str(e)}", exc_info=True)
            return {'code': '12', 'message': f'Ollama识别错误: {str(e)}'}
    
    def _recognize_with_minimax(self, image_base64: str) -> Dict:
        """使用MiniMax进行识别"""
        try:
            logger.info("🟣 使用MiniMax进行识别...")
            url = "https://api.minimax.io/v1/text/chatcompletion_v2"
            logger.info(f"🔗 请求URL: {url}")
            
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
            
            logger.info(f"📤 发送请求到MiniMax，模型: MiniMax-M2.5")
            logger.info(f"⏱️  等待MiniMax响应（超时120秒）...")
            
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            logger.info(f"✅ 收到MiniMax响应，状态码: {response.status_code}")
            
            result = response.json()
            response_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            logger.info(f"📝 MiniMax原始响应: {response_text[:200]}...")
            
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
                
                logger.info(f"🔄 清理后的响应: {response_text}")
                
                parsed_result = json.loads(response_text)
                logger.info(f"✅ JSON解析成功: {parsed_result}")
                return parsed_result
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️  JSON解析失败: {str(e)}")
                logger.info("🔍 尝试从文本中提取车牌号...")
                return self._extract_plate_from_text(response_text)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ MiniMax服务连接失败: {str(e)}")
            return {'code': '13', 'message': f'MiniMax服务连接失败: {str(e)}'}
        except Exception as e:
            logger.error(f"❌ MiniMax识别错误: {str(e)}", exc_info=True)
            return {'code': '14', 'message': f'MiniMax识别错误: {str(e)}'}
    
    def _extract_plate_from_text(self, text: str) -> Dict:
        """从文本中提取车牌号（备用方案）"""
        import re
        logger.info("🔍 使用正则表达式提取车牌号...")
        logger.info(f"📝 待提取文本: {text}")
        
        # 中国车牌号正则表达式
        pattern = r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-Z0-9]{5}'
        matches = re.findall(pattern, text)
        
        if matches:
            plate_number = matches[0]
            logger.info(f"✅ 成功提取车牌号: {plate_number}")
            return {
                'code': '0',
                'plate_number': plate_number,
                'message': '解析完成'
            }
        else:
            logger.warning("⚠️  未能从文本中提取到车牌号")
            return {
                'code': '1',
                'plate_number': '',
                'message': '未识别到车牌'
            }
