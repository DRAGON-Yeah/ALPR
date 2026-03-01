# 车牌识别停车缴费系统 (ALPR)

一个基于 Python Flask 的车牌识别停车缴费系统，支持本地 Ollama 和云端 MiniMax API 进行图像识别。

## 功能特性

- 📸 支持手机拍照或上传车牌照片
- 🤖 AI 多模态识别（Ollama 本地 / MiniMax 云端）
- 💳 三页面独立系统（识别、缴费、成功）
- 🔄 缴费页面实时监听最新未付款车牌
- 🏷️ 智能付款状态管理，防止重复付款
- ♻️ 付款成功后自动清除，继续监听新车牌
- 📱 完全适配 H5 移动端页面
- 📝 详细的日志输出，支持文件和控制台
- 🖥️ 支持双终端模式（识别终端 + 缴费终端）
- 📊 实时统计（总数、已付款、未付款）

## 技术栈

- 后端：Python 3.13 + Flask 3.0.0
- 前端：原生 HTML/CSS/JavaScript
- AI 识别：Ollama (qwen3-vl:8b) / MiniMax API
- 日志：Python logging（文件 + 控制台）

---

## 快速开始

> 💡 **快速参考**: 查看 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 获取常用命令速查表

### 1. 克隆项目
```bash
git clone <repository-url>
cd ALPR
```

### 2. 一键启动
```bash
./manage.sh start

# 或使用简单脚本
./run.sh
```

脚本会自动：
- 创建虚拟环境
- 安装依赖
- 配置环境变量
- 启动服务

### 3. 访问系统
- 车牌识别页面: http://localhost:5001/upload
- 停车缴费页面: http://localhost:5001/payment

---

## 详细安装步骤

### 1. 环境要求
- Python 3.13+
- pip
- （可选）Ollama（如使用本地识别）

### 2. 创建虚拟环境
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

依赖包括：
- flask==3.0.0
- flask-cors==4.0.0
- pillow>=10.2.0
- requests==2.31.0
- python-dotenv==1.0.0

### 4. 配置环境变量
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
FLASK_PORT=5001
```

### 5. 安装 Ollama（可选）
如果使用本地识别，访问 [Ollama 官网](https://ollama.ai) 下载安装，然后：
```bash
ollama pull qwen3-vl:8b
ollama serve
```

### 6. 启动服务
```bash
# 方式1：使用管理脚本
./manage.sh start

# 方式2：使用简单脚本
./run.sh

# 方式3：直接运行
python app.py

# 停止服务
./manage.sh stop

# 或按 Ctrl+C 停止
```

---

## 使用说明

### 双终端模式（推荐）

**终端A - 识别终端：**
1. 打开 http://localhost:5001/upload
2. 拍照或上传车牌照片
3. 点击"开始识别"
4. 识别成功后自动重置，可继续识别下一辆车

**终端B - 缴费终端：**
1. 打开 http://localhost:5001/payment
2. 页面自动监听最新未付款车牌（每2秒轮询）
3. 当有新车牌识别成功时，自动显示缴费表单
4. 输入金额10元，点击"确认付款"
5. 跳转到成功页面，3秒后自动返回继续监听

### 单终端模式

1. 访问识别页面上传车牌
2. 切换到缴费页面完成付款
3. 付款成功后自动返回缴费页面

### 工作流程

```
识别车牌 → 标记未付款 → 缴费页面监听 → 显示车牌 → 
处理付款 → 标记已付款 → 跳转成功页 → 自动返回 → 
继续监听下一个未付款车牌
```

---

## 管理工具

### 统一管理脚本 (manage.sh)

```bash
# 交互式菜单
./manage.sh

# 命令行模式
./manage.sh start      # 启动服务
./manage.sh stop       # 停止服务
./manage.sh restart    # 重启服务
./manage.sh status     # 查看状态
./manage.sh logs       # 实时查看日志
./manage.sh logs50     # 查看最近50行
./manage.sh errors     # 查看错误日志
./manage.sh search     # 搜索日志
./manage.sh clean      # 清理旧日志
./manage.sh test       # 运行测试
./manage.sh stats      # 查看统计
```

### 简单运行脚本 (run.sh)

```bash
./run.sh  # 快速启动服务
```

---

## API 接口

### 1. 上传图片识别
```
POST /api/upload
Content-Type: multipart/form-data

参数：
- image: 图片文件

返回：
{
  "recognition_id": "0",
  "code": "0",
  "plate_number": "粤A5A66A",
  "message": "解析完成"
}
```

### 2. 获取最新未付款记录
```
GET /api/latest_recognition

返回：
{
  "recognition_id": "0",
  "code": "0",
  "plate_number": "粤A5A66A",
  "message": "解析完成"
}
```

### 3. 查询识别状态
```
GET /api/check_status/<recognition_id>

返回：
{
  "code": "0",
  "plate_number": "粤A5A66A",
  "message": "解析完成"
}
```

### 4. 处理付款
```
POST /api/payment
Content-Type: application/json

参数：
{
  "recognition_id": "0",
  "amount": "10"
}

返回：
{
  "code": "0",
  "message": "付款成功",
  "plate_number": "粤A5A66A"
}
```

### 5. 获取统计信息
```
GET /api/stats

返回：
{
  "total": 3,
  "paid": 2,
  "unpaid": 1
}
```

---

## 日志系统

### 日志位置
```
logs/
├── app_20260301.log    # 今天的日志
├── app_20260302.log    # 明天的日志
└── ...
```

### 日志特点
- ✅ 双重输出：控制台 + 文件
- ✅ 每天自动创建新文件
- ✅ UTF-8 编码
- ✅ 详细的步骤追踪
- ✅ Emoji 图标增强可读性

### 查看日志
```bash
# 实时查看
./manage.sh logs

# 查看最近50行
./manage.sh logs50

# 查看错误
./manage.sh errors

# 搜索内容
./manage.sh search

# 直接查看文件
tail -f logs/app_$(date +%Y%m%d).log
```

### 日志示例
```
2026-03-01 23:48:11 [INFO] 📝 日志文件: logs/app_20260301.log
2026-03-01 23:48:11 [INFO] 🚀 初始化应用配置...
2026-03-01 23:49:02 [INFO] 📥 收到请求: GET /api/latest_recognition
2026-03-01 23:50:00 [INFO] 📸 开始处理图片上传...
2026-03-01 23:50:05 [INFO] 🎯 识别结果: {'code': '0', 'plate_number': '粤A5A66A'}
2026-03-01 23:51:00 [INFO] 💳 开始处理付款...
2026-03-01 23:51:00 [INFO] ✅ 付款成功！车牌号: 粤A5A66A
2026-03-01 23:51:00 [INFO] 🏷️  标记识别记录 0 为已付款
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 未找到图片文件 |
| 2 | 未选择文件 |
| 3 | 未找到识别记录 |
| 4 | 缺少必要参数 |
| 5 | 付款金额不正确 |
| 6 | 金额格式错误 |
| 7 | 识别记录不存在 |
| 8 | 车牌识别未成功 |
| 9 | 该车牌已付款 |
| 10 | 不支持的AI提供商 |
| 11-14 | AI服务相关错误 |
| 99 | 服务器错误 |

---

## 项目结构

```
ALPR/
├── app.py                      # Flask 主应用
├── ai_service.py               # AI 识别服务
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量示例
├── .env                        # 环境配置（需创建）
├── .gitignore                 # Git 忽略文件
├── README.md                  # 项目说明（本文件）
├── ARCHITECTURE.md            # 系统架构文档
├── templates/
│   ├── upload.html            # 车牌识别页面
│   ├── payment.html           # 停车缴费页面
│   └── success.html           # 付款成功页面
├── static/
│   ├── css/
│   │   └── style.css          # 样式文件
│   └── js/
│       ├── upload.js          # 识别页面逻辑
│       └── payment.js         # 缴费页面逻辑
├── scripts/
│   ├── manage.sh              # 统一管理脚本
│   └── run.sh                 # 简单运行脚本
├── logs/                      # 日志目录（自动创建）
└── uploads/                   # 上传文件目录（自动创建）
```

---

## 常见问题

### Q: 端口5001被占用？
A: 修改 `.env` 文件中的 `FLASK_PORT` 为其他端口，或使用 `./stop.sh` 停止占用进程。

### Q: 识别失败？
A: 检查 AI 服务配置：
- **Ollama**: 确保服务运行在 http://localhost:11434
- **MiniMax**: 检查 API Key 是否正确

### Q: 缴费页面没有显示识别结果？
A: 
1. 确保先上传了车牌照片
2. 检查浏览器控制台是否有错误
3. 查看服务器日志：`./logs.sh tail`

### Q: 如何切换 AI 提供商？
A: 修改 `.env` 文件中的 `AI_PROVIDER`：
- `AI_PROVIDER=ollama` - 使用本地 Ollama
- `AI_PROVIDER=minimax` - 使用云端 MiniMax

### Q: 如何查看日志？
A: 使用 `./logs.sh` 脚本或直接查看 `logs/` 目录下的文件。

### Q: 虚拟环境问题？
A: 删除 `.venv` 目录后重新运行 `./start.sh`。

---

## 开发指南

### 修改代码后重启
```bash
./manage.sh restart
```

### 查看实时日志
```bash
./manage.sh logs
```

### 测试功能
```bash
# 确保服务正在运行
./manage.sh test

# 使用真实图片测试
python test_car_image.py
```

**测试图片准备：**
1. 准备一张车牌照片
2. 命名为 `car1.png`
3. 放在项目根目录
4. 运行 `python test_car_image.py`

详细测试说明请查看 [TESTING.md](TESTING.md)

### 调试模式
```bash
# 停止后台服务
./manage.sh stop

# 前台运行查看详细输出
source .venv/bin/activate
python app.py
```

---

## 生产部署

### 使用 Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### 使用 Docker
```dockerfile
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

构建和运行：
```bash
docker build -t alpr .
docker run -p 5001:5001 -v $(pwd)/logs:/app/logs alpr
```

---

## 系统架构

详细的系统架构说明请查看 [ARCHITECTURE.md](ARCHITECTURE.md)

### 核心特性

1. **智能付款状态管理**
   - 每个识别记录标记付款状态
   - 自动过滤已付款车牌
   - 防止重复付款

2. **实时监听机制**
   - 缴费页面每2秒轮询
   - 只显示未付款车牌
   - 自动更新最新记录

3. **自动循环流程**
   - 付款成功后3秒自动返回
   - 继续监听新车牌
   - 无需手动操作

---

## 注意事项

- 本系统仅用于实验和学习目的
- 生产环境需要添加数据库、用户认证等功能
- MiniMax API 密钥请妥善保管
- 上传的图片会保存在 `uploads/` 目录
- 日志文件会保存在 `logs/` 目录
- 建议定期清理旧日志：`./logs.sh clean`

---

## 许可证

MIT License

---

## 技术支持

如遇问题，请查看：
1. 服务器日志：`./logs.sh tail`
2. 浏览器控制台错误
3. [ARCHITECTURE.md](ARCHITECTURE.md) 架构文档

---

## 更新日志

### v2.1.0 - 2026-03-01
- ✅ 智能付款状态管理
- ✅ 防重复付款
- ✅ 自动清除已付款车牌
- ✅ 日志文件持久化
- ✅ 完整的脚本工具集

### v2.0.0 - 2026-03-01
- ✅ 三页面系统架构
- ✅ 实时监听机制
- ✅ 详细日志输出
- ✅ 双终端支持

---

**祝使用愉快！🎉**
