# 车牌识别停车缴费系统 (ALPR)

一个基于 Python Flask 的车牌识别停车缴费系统，支持本地 Ollama 和云端 MiniMax API 进行图像识别。

## 功能特性

- 📸 支持手机拍照或上传车牌照片
- 🤖 AI 多模态识别（Ollama 本地 / MiniMax 云端）
- 💳 模拟停车缴费流程
- 📱 完全适配 H5 移动端页面
- 🔄 实时轮询识别状态

## 技术栈

- 后端：Python Flask
- 前端：原生 HTML/CSS/JavaScript
- AI 识别：Ollama (qwen3-vl:8b) / MiniMax API

## 安装步骤

### 1. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 选择 AI 提供商：ollama 或 minimax
AI_PROVIDER=ollama

# Ollama 配置（如果使用本地）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3-vl:8b

# MiniMax 配置（如果使用云端）
MINIMAX_API_KEY=你的API密钥
MINIMAX_GROUP_ID=你的组ID

# 服务器端口
FLASK_PORT=5000
```

### 4. 安装 Ollama（如果使用本地识别）

访问 [Ollama 官网](https://ollama.ai) 下载安装，然后运行：

```bash
ollama pull qwen3-vl:8b
ollama serve
```

### 5. 运行应用

```bash
python app.py
```

访问 `http://localhost:5000` 即可使用。

## 使用说明

1. 打开网页，点击上传区域选择车牌照片或直接拍照
2. 点击"开始识别"按钮上传图片
3. 系统自动识别车牌号（轮询显示进度）
4. 识别成功后显示车牌号和停车费用（10元）
5. 输入金额"10"并点击"确认付款"
6. 显示付款成功页面："付款成功，已经开闸，请通过..."

## API 接口

### 上传图片识别

```
POST /api/upload
Content-Type: multipart/form-data

参数：
- image: 图片文件

返回：
{
  "recognition_id": "识别ID",
  "code": "0",
  "plate_number": "粤A5A66A",
  "message": "解析完成"
}
```

### 查询识别状态

```
GET /api/check_status/<recognition_id>

返回：
{
  "code": "0",
  "plate_number": "粤A5A66A",
  "message": "解析完成"
}
```

### 处理付款

```
POST /api/payment
Content-Type: application/json

参数：
{
  "recognition_id": "识别ID",
  "amount": "10"
}

返回：
{
  "code": "0",
  "message": "付款成功",
  "plate_number": "粤A5A66A"
}
```

## 错误码说明

- `0`: 成功
- `1`: 未找到图片文件
- `2`: 未选择文件
- `3`: 未找到识别记录
- `4`: 缺少必要参数
- `5`: 付款金额不正确
- `6`: 金额格式错误
- `7`: 识别记录不存在
- `8`: 车牌识别未成功
- `10`: 不支持的AI提供商
- `11-14`: AI服务相关错误
- `99`: 服务器错误

## 项目结构

```
ALPR/
├── app.py              # Flask 主应用
├── ai_service.py       # AI 识别服务
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量示例
├── .gitignore         # Git 忽略文件
├── templates/
│   └── index.html     # 主页面
├── static/
│   ├── css/
│   │   └── style.css  # 样式文件
│   └── js/
│       └── app.js     # 前端逻辑
└── uploads/           # 上传文件目录（自动创建）
```

## 注意事项

- 本系统仅用于实验和学习目的
- 生产环境需要添加数据库、用户认证等功能
- MiniMax API 密钥请妥善保管
- 上传的图片会保存在 `uploads/` 目录

## 许可证

MIT License
