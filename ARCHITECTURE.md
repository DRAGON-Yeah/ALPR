# 系统架构说明

## 整体架构

```mermaid
graph TB
    subgraph System["车牌识别停车缴费系统"]
        A["识别终端 A<br/>/upload<br/>📸 拍照识别"]
        B["缴费终端 B<br/>/payment<br/>💳 监听缴费"]
        C["Flask 后端服务器<br/>路由管理<br/>API 接口<br/>日志系统"]
        D["AI 识别服务<br/>Ollama 本地<br/>MiniMax 云端"]
    end
    
    A -->|POST /api/upload| C
    B -->|GET /api/latest_recognition 每2秒轮询| C
    C --> D
```

## 页面流程

### 识别页面流程

```mermaid
flowchart TD
    A[用户访问 /upload] --> B[选择或拍摄车牌照片]
    B --> C[点击开始识别]
    C --> D[POST /api/upload]
    D --> E[后端调用 AI 识别]
    E --> F[返回识别结果]
    F --> G[显示成功消息]
    G --> H[2秒后自动重置]
    H --> I[准备下一次识别]
    I --> B
```

### 缴费页面流程

```mermaid
flowchart TD
    A[用户访问 /payment] --> B[页面加载完成]
    B --> C[启动监听定时器 每2秒]
    C --> D[GET /api/latest_recognition]
    D --> E{检查是否有新识别记录}
    E -->|无新记录| C
    E -->|有新记录且识别成功| F[显示车牌号和缴费表单]
    F --> G[用户输入金额并确认]
    G --> H[POST /api/payment]
    H --> I[跳转到 /success]
    I --> J[显示付款成功]
    J --> K[3秒后自动返回 /payment]
    K --> C
```

## 数据流

### 1. 图片上传识别

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务器
    participant AI as AI服务
    
    C->>S: POST /api/upload<br/>(multipart/form-data)
    S->>S: 保存图片
    S->>S: 转换Base64
    S->>AI: recognize_plate()
    AI->>AI: 调用AI模型
    AI->>AI: 解析响应
    AI-->>S: 返回识别结果
    S->>S: 存储结果
    S-->>C: 返回JSON<br/>{recognition_id, ...}
```

### 2. 监听最新识别

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务器
    
    loop 每2秒轮询
        C->>S: GET /api/latest_recognition
        S->>S: 查找最新记录
        S->>S: 比较ID
        S-->>C: 返回最新结果<br/>{recognition_id, ...}
    end
```

### 3. 处理付款

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务器
    
    C->>S: POST /api/payment<br/>{recognition_id, amount}
    S->>S: 验证金额
    S->>S: 验证识别记录
    S->>S: 处理付款
    S-->>C: 返回成功<br/>{code: "0", ...}
    C->>S: 跳转 /success
```

## 核心组件

### 前端组件

#### 1. upload.js
- 文件选择处理
- 图片预览
- 上传请求
- 状态显示
- 自动重置

#### 2. payment.js
- 监听定时器
- 轮询最新识别
- 显示缴费表单
- 付款请求
- 页面跳转

#### 3. style.css
- 响应式布局
- 动画效果
- 状态样式
- 移动端适配

### 后端组件

#### 1. app.py
- Flask 应用初始化
- 路由定义
- API 接口
- 日志中间件
- 请求处理

#### 2. ai_service.py
- AI 服务封装
- Ollama 集成
- MiniMax 集成
- 响应解析
- 错误处理

## 数据存储

### 内存存储（当前实现）
```python
recognition_results = {
    "0": {
        "code": "0",
        "plate_number": "粤A5A66A",
        "message": "解析完成"
    },
    "1": {
        "code": "0",
        "plate_number": "京B12345",
        "message": "解析完成"
    }
}
```

### 数据库存储（生产环境建议）
```sql
CREATE TABLE recognitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number VARCHAR(20),
    image_path VARCHAR(255),
    status VARCHAR(20),
    created_at TIMESTAMP,
    paid BOOLEAN DEFAULT FALSE
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recognition_id INTEGER,
    amount DECIMAL(10,2),
    paid_at TIMESTAMP,
    FOREIGN KEY (recognition_id) REFERENCES recognitions(id)
);
```

## API 接口规范

### 1. POST /api/upload
**请求：**
- Content-Type: multipart/form-data
- Body: image (file)

**响应：**
```json
{
  "recognition_id": "0",
  "code": "0",
  "plate_number": "粤A5A66A",
  "message": "解析完成"
}
```

### 2. GET /api/latest_recognition
**响应：**
```json
{
  "recognition_id": "0",
  "code": "0",
  "plate_number": "粤A5A66A",
  "message": "解析完成"
}
```

### 3. POST /api/payment
**请求：**
```json
{
  "recognition_id": "0",
  "amount": "10"
}
```

**响应：**
```json
{
  "code": "0",
  "message": "付款成功",
  "plate_number": "粤A5A66A"
}
```

## 错误处理

### 错误码定义
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

## 性能优化

### 前端优化
1. 图片压缩后上传
2. 防抖处理避免重复请求
3. 轮询间隔可配置
4. 使用 CSS 动画而非 JS

### 后端优化
1. 异步处理 AI 识别
2. 结果缓存
3. 图片存储优化
4. 数据库索引

### 扩展性
1. 支持多个识别终端
2. 支持多个缴费终端
3. 负载均衡
4. 分布式存储

## 安全考虑

1. **文件上传安全**
   - 文件类型验证
   - 文件大小限制（16MB）
   - 文件名安全处理

2. **API 安全**
   - CORS 配置
   - 请求频率限制
   - 参数验证

3. **数据安全**
   - 敏感信息加密
   - API Key 环境变量存储
   - 日志脱敏

## 部署建议

### 开发环境
```bash
python app.py
```

### 生产环境
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Docker 部署
```dockerfile
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

## 监控和日志

### 日志级别
- INFO: 正常操作
- WARNING: 警告信息
- ERROR: 错误信息

### 监控指标
- 请求数量
- 响应时间
- 识别成功率
- 付款成功率
- 错误率

## 未来扩展

1. **功能扩展**
   - 支持更多支付方式
   - 车辆进出记录
   - 停车时长计算
   - 优惠券系统

2. **技术扩展**
   - WebSocket 实时通信
   - Redis 缓存
   - 消息队列
   - 微服务架构

3. **AI 扩展**
   - 支持更多 AI 模型
   - 车型识别
   - 车辆颜色识别
   - 车辆损伤检测
