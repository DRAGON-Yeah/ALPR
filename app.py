from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
import os
import base64
import logging
from datetime import datetime
from dotenv import load_dotenv
from ai_service import AIService

load_dotenv()

# 创建日志目录
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
log_file = os.path.join(LOG_DIR, f'app_{datetime.now().strftime("%Y%m%d")}.log')

# 创建日志格式
log_format = '%(asctime)s [%(levelname)s] %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=date_format,
    handlers=[
        # 控制台输出
        logging.StreamHandler(),
        # 文件输出
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 启动时记录日志文件位置
logger.info(f"📝 日志文件: {log_file}")

app = Flask(__name__)
CORS(app)

# 日志中间件
@app.before_request
def log_request():
    logger.info(f"{'='*60}")
    logger.info(f"📥 收到请求: {request.method} {request.path}")
    if request.method == 'POST' and request.is_json:
        logger.info(f"📦 请求数据: {request.json}")
    logger.info(f"🌐 客户端IP: {request.remote_addr}")

@app.after_request
def log_response(response):
    logger.info(f"📤 响应状态: {response.status_code}")
    logger.info(f"{'='*60}\n")
    return response

# 配置
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

logger.info("🚀 初始化应用配置...")
logger.info(f"📁 上传目录: {UPLOAD_FOLDER}")
logger.info(f"📏 最大文件大小: 16MB")

# 初始化AI服务
logger.info("🤖 初始化AI服务...")
ai_service = AIService()

# 存储识别结果（实际应用中应使用数据库）
recognition_results = {}

@app.route('/')
def index():
    logger.info("🏠 访问首页，重定向到上传页面")
    return redirect('/upload')

@app.route('/upload')
def upload_page():
    logger.info("📸 访问车牌识别页面")
    return render_template('upload.html')

@app.route('/payment')
def payment_page():
    logger.info("💳 访问停车缴费页面")
    return render_template('payment.html')

@app.route('/success')
def success_page():
    plate_number = request.args.get('plate', '未知')
    logger.info(f"✅ 访问付款成功页面，车牌号: {plate_number}")
    return render_template('success.html', plate_number=plate_number)

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """上传图片并进行车牌识别"""
    try:
        logger.info("📸 开始处理图片上传...")
        
        if 'image' not in request.files:
            logger.warning("⚠️  未找到图片文件")
            return jsonify({'code': '1', 'message': '未找到图片文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            logger.warning("⚠️  未选择文件")
            return jsonify({'code': '2', 'message': '未选择文件'}), 400
        
        logger.info(f"📄 文件名: {file.filename}")
        
        # 保存文件
        filename = f"{len(recognition_results)}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"💾 保存文件到: {filepath}")
        file.save(filepath)
        
        # 获取文件大小
        file_size = os.path.getsize(filepath)
        logger.info(f"📊 文件大小: {file_size / 1024:.2f} KB")
        
        # 读取图片并转换为base64
        logger.info("🔄 转换图片为Base64...")
        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        logger.info(f"✅ Base64转换完成，长度: {len(image_data)}")
        
        # 调用AI识别
        logger.info("🤖 开始AI识别...")
        result = ai_service.recognize_plate(filepath, image_data)
        logger.info(f"🎯 识别结果: {result}")
        
        # 生成识别ID
        recognition_id = str(len(recognition_results))
        recognition_results[recognition_id] = {
            **result,
            'paid': False,  # 添加付款状态标记
            'timestamp': datetime.now().isoformat()  # 添加时间戳
        }
        logger.info(f"🆔 生成识别ID: {recognition_id}")
        logger.info(f"📝 当前识别记录数: {len(recognition_results)}")
        
        return jsonify({
            'recognition_id': recognition_id,
            **result
        })
    
    except Exception as e:
        logger.error(f"❌ 服务器错误: {str(e)}", exc_info=True)
        return jsonify({'code': '99', 'message': f'服务器错误: {str(e)}'}), 500

@app.route('/api/check_status/<recognition_id>', methods=['GET'])
def check_status(recognition_id):
    """检查识别状态（用于轮询）"""
    logger.info(f"🔍 查询识别状态: ID={recognition_id}")
    result = recognition_results.get(recognition_id)
    if result:
        logger.info(f"✅ 找到识别记录: {result}")
        return jsonify(result)
    logger.warning(f"⚠️  未找到识别记录: ID={recognition_id}")
    return jsonify({'code': '3', 'message': '未找到识别记录'}), 404

@app.route('/api/latest_recognition', methods=['GET'])
def latest_recognition():
    """获取最新的未付款识别记录（用于缴费页面监听）"""
    logger.info("🔍 查询最新未付款识别记录...")
    
    if not recognition_results:
        logger.info("📭 暂无识别记录")
        return jsonify({'code': '3', 'message': '暂无识别记录'})
    
    # 获取所有未付款的识别记录
    unpaid_records = {k: v for k, v in recognition_results.items() 
                      if not v.get('paid', False) and v.get('code') == '0'}
    
    if not unpaid_records:
        logger.info("📭 暂无未付款记录")
        return jsonify({'code': '3', 'message': '暂无未付款记录'})
    
    # 获取最新的未付款识别ID
    latest_id = max(unpaid_records.keys(), key=lambda x: int(x))
    result = unpaid_records[latest_id]
    
    logger.info(f"📋 最新未付款识别记录: ID={latest_id}, 车牌={result.get('plate_number')}")
    
    return jsonify({
        'recognition_id': latest_id,
        'code': result.get('code'),
        'plate_number': result.get('plate_number'),
        'message': result.get('message')
    })

@app.route('/api/payment', methods=['POST'])
def process_payment():
    """处理付款"""
    try:
        logger.info("💳 开始处理付款...")
        data = request.json
        recognition_id = data.get('recognition_id')
        amount = data.get('amount')
        
        logger.info(f"🆔 识别ID: {recognition_id}")
        logger.info(f"💰 付款金额: {amount}")
        
        if not recognition_id or not amount:
            logger.warning("⚠️  缺少必要参数")
            return jsonify({'code': '4', 'message': '缺少必要参数'}), 400
        
        # 验证金额
        try:
            amount_value = float(amount)
            logger.info(f"🔢 金额验证: {amount_value}")
            if amount_value != 10.0:
                logger.warning(f"⚠️  付款金额不正确: {amount_value}元，应为10元")
                return jsonify({'code': '5', 'message': '付款金额不正确，应为10元'}), 400
        except ValueError:
            logger.error(f"❌ 金额格式错误: {amount}")
            return jsonify({'code': '6', 'message': '金额格式错误'}), 400
        
        # 验证识别记录
        logger.info("🔍 验证识别记录...")
        result = recognition_results.get(recognition_id)
        if not result:
            logger.warning(f"⚠️  识别记录不存在: ID={recognition_id}")
            return jsonify({'code': '7', 'message': '识别记录不存在'}), 404
        
        logger.info(f"📋 识别记录: {result}")
        
        if result.get('code') != '0':
            logger.warning(f"⚠️  车牌识别未成功，无法付款")
            return jsonify({'code': '8', 'message': '车牌识别未成功，无法付款'}), 400
        
        # 检查是否已付款
        if result.get('paid', False):
            logger.warning(f"⚠️  该车牌已付款: {result.get('plate_number')}")
            return jsonify({'code': '9', 'message': '该车牌已付款，请勿重复付款'}), 400
        
        # 付款成功，标记为已付款
        plate_number = result.get('plate_number')
        recognition_results[recognition_id]['paid'] = True
        recognition_results[recognition_id]['paid_at'] = datetime.now().isoformat()
        
        logger.info(f"✅ 付款成功！车牌号: {plate_number}")
        logger.info(f"🏷️  标记识别记录 {recognition_id} 为已付款")
        logger.info("🚪 开闸放行...")
        
        # 统计未付款记录数
        unpaid_count = sum(1 for v in recognition_results.values() if not v.get('paid', False))
        logger.info(f"📊 剩余未付款记录数: {unpaid_count}")
        
        return jsonify({
            'code': '0',
            'message': '付款成功',
            'plate_number': plate_number
        })
    
    except Exception as e:
        logger.error(f"❌ 付款处理失败: {str(e)}", exc_info=True)
        return jsonify({'code': '99', 'message': f'付款处理失败: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    total = len(recognition_results)
    paid = sum(1 for v in recognition_results.values() if v.get('paid', False))
    unpaid = total - paid
    
    logger.info(f"📊 统计信息: 总数={total}, 已付款={paid}, 未付款={unpaid}")
    
    return jsonify({
        'total': total,
        'paid': paid,
        'unpaid': unpaid
    })

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    logger.info("="*60)
    logger.info("🚀 启动车牌识别停车缴费系统")
    logger.info(f"🌐 服务地址: http://0.0.0.0:{port}")
    logger.info(f"🌐 本地访问: http://127.0.0.1:{port}")
    logger.info("="*60)
    app.run(host='0.0.0.0', port=port, debug=True)
