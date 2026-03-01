from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import base64
from dotenv import load_dotenv
from ai_service import AIService

load_dotenv()

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 初始化AI服务
ai_service = AIService()

# 存储识别结果（实际应用中应使用数据库）
recognition_results = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """上传图片并进行车牌识别"""
    try:
        if 'image' not in request.files:
            return jsonify({'code': '1', 'message': '未找到图片文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'code': '2', 'message': '未选择文件'}), 400
        
        # 保存文件
        filename = f"{len(recognition_results)}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 读取图片并转换为base64
        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 调用AI识别
        result = ai_service.recognize_plate(filepath, image_data)
        
        # 生成识别ID
        recognition_id = str(len(recognition_results))
        recognition_results[recognition_id] = result
        
        return jsonify({
            'recognition_id': recognition_id,
            **result
        })
    
    except Exception as e:
        return jsonify({'code': '99', 'message': f'服务器错误: {str(e)}'}), 500

@app.route('/api/check_status/<recognition_id>', methods=['GET'])
def check_status(recognition_id):
    """检查识别状态（用于轮询）"""
    result = recognition_results.get(recognition_id)
    if result:
        return jsonify(result)
    return jsonify({'code': '3', 'message': '未找到识别记录'}), 404

@app.route('/api/payment', methods=['POST'])
def process_payment():
    """处理付款"""
    try:
        data = request.json
        recognition_id = data.get('recognition_id')
        amount = data.get('amount')
        
        if not recognition_id or not amount:
            return jsonify({'code': '4', 'message': '缺少必要参数'}), 400
        
        # 验证金额
        try:
            amount_value = float(amount)
            if amount_value != 10.0:
                return jsonify({'code': '5', 'message': '付款金额不正确，应为10元'}), 400
        except ValueError:
            return jsonify({'code': '6', 'message': '金额格式错误'}), 400
        
        # 验证识别记录
        result = recognition_results.get(recognition_id)
        if not result:
            return jsonify({'code': '7', 'message': '识别记录不存在'}), 404
        
        if result.get('code') != '0':
            return jsonify({'code': '8', 'message': '车牌识别未成功，无法付款'}), 400
        
        # 付款成功
        return jsonify({
            'code': '0',
            'message': '付款成功',
            'plate_number': result.get('plate_number')
        })
    
    except Exception as e:
        return jsonify({'code': '99', 'message': f'付款处理失败: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
