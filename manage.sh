#!/bin/bash

# 车牌识别停车缴费系统 - 统一管理脚本

BASE_URL="http://127.0.0.1:5001"
LOG_DIR="logs"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示主菜单
show_menu() {
    echo ""
    echo "🚗 车牌识别停车缴费系统 - 管理工具"
    echo "========================================"
    echo ""
    echo "服务管理："
    echo "  1. 启动服务 (start)"
    echo "  2. 停止服务 (stop)"
    echo "  3. 重启服务 (restart)"
    echo "  4. 查看状态 (status)"
    echo ""
    echo "日志管理："
    echo "  5. 实时查看日志 (logs)"
    echo "  6. 查看最近50行 (logs50)"
    echo "  7. 查看错误日志 (errors)"
    echo "  8. 搜索日志 (search)"
    echo "  9. 清理旧日志 (clean)"
    echo ""
    echo "测试工具："
    echo "  10. 运行测试 (test)"
    echo "  11. 查看统计 (stats)"
    echo ""
    echo "  0. 退出 (exit)"
    echo ""
}

# 启动服务
start_service() {
    echo "🚀 启动车牌识别停车缴费系统..."
    echo ""
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo "📦 创建虚拟环境..."
        python3 -m venv .venv
    fi
    
    # 激活虚拟环境
    source .venv/bin/activate
    
    # 检查依赖
    echo "📋 检查依赖..."
    pip install -q -r requirements.txt
    
    # 检查环境变量
    if [ ! -f ".env" ]; then
        echo "⚙️  创建环境配置文件..."
        cp .env.example .env
    fi
    
    echo ""
    echo "✅ 准备完成！"
    echo ""
    echo "📱 访问地址："
    echo "   - 车牌识别页面: http://127.0.0.1:5001/upload"
    echo "   - 停车缴费页面: http://127.0.0.1:5001/payment"
    echo ""
    echo "💡 提示："
    echo "   - 可以在两个浏览器窗口中分别打开识别和缴费页面"
    echo "   - 缴费页面会自动监听最新的识别结果"
    echo "   - 按 Ctrl+C 停止服务"
    echo ""
    echo "🔧 启动服务..."
    echo ""
    
    # 启动应用
    python app.py
}

# 停止服务
stop_service() {
    echo "🛑 停止车牌识别停车缴费系统..."
    echo ""
    
    # 查找运行中的 Flask 进程
    PIDS=$(ps aux | grep "[p]ython app.py" | awk '{print $2}')
    
    if [ -n "$PIDS" ]; then
        echo "📋 找到以下进程："
        ps aux | grep "[p]ython app.py"
        echo ""
        
        # 停止所有找到的进程
        for PID in $PIDS; do
            echo "🔪 停止进程 PID: $PID"
            kill $PID
            
            # 等待进程结束
            sleep 1
            
            # 检查进程是否还在运行
            if ps -p $PID > /dev/null 2>&1; then
                echo "⚠️  进程 $PID 未响应，强制停止..."
                kill -9 $PID
            fi
        done
        
        echo ""
        echo "✅ 服务已停止"
    else
        echo "ℹ️  未找到运行中的服务"
    fi
    
    echo ""
    
    # 显示端口占用情况
    echo "📊 端口 5001 状态："
    PORT_INFO=$(lsof -i :5001 2>/dev/null)
    if [ -n "$PORT_INFO" ]; then
        echo "$PORT_INFO"
        echo ""
        echo "⚠️  端口 5001 仍被占用"
    else
        echo "   ✅ 端口 5001 未被占用"
    fi
}

# 重启服务
restart_service() {
    echo "🔄 重启车牌识别停车缴费系统..."
    echo ""
    
    echo "1️⃣ 停止现有服务..."
    stop_service
    
    echo ""
    echo "⏳ 等待 2 秒..."
    sleep 2
    echo ""
    
    echo "2️⃣ 启动服务..."
    start_service
}

# 查看状态
check_status() {
    echo "📊 系统状态"
    echo "============"
    echo ""
    
    # 检查进程
    PIDS=$(ps aux | grep "[p]ython app.py" | awk '{print $2}')
    if [ -n "$PIDS" ]; then
        echo "✅ 服务运行中"
        echo ""
        echo "进程信息："
        ps aux | grep "[p]ython app.py"
    else
        echo "❌ 服务未运行"
    fi
    
    echo ""
    
    # 检查端口
    echo "端口状态："
    PORT_INFO=$(lsof -i :5001 2>/dev/null)
    if [ -n "$PORT_INFO" ]; then
        echo "$PORT_INFO"
    else
        echo "   端口 5001 未被占用"
    fi
    
    echo ""
    
    # 检查日志
    if [ -d "$LOG_DIR" ]; then
        echo "日志文件："
        ls -lh "$LOG_DIR" | tail -5
    else
        echo "日志目录不存在"
    fi
}

# 实时查看日志
view_logs() {
    if [ ! -d "$LOG_DIR" ]; then
        echo "❌ 日志目录不存在"
        return
    fi
    
    TODAY=$(date +%Y%m%d)
    LOG_FILE="$LOG_DIR/app_${TODAY}.log"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ 今天的日志文件不存在"
        return
    fi
    
    echo "📖 实时查看日志（按 Ctrl+C 退出）..."
    echo ""
    tail -f "$LOG_FILE"
}

# 查看最近N行日志
view_recent_logs() {
    local lines=${1:-50}
    
    if [ ! -d "$LOG_DIR" ]; then
        echo "❌ 日志目录不存在"
        return
    fi
    
    TODAY=$(date +%Y%m%d)
    LOG_FILE="$LOG_DIR/app_${TODAY}.log"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ 今天的日志文件不存在"
        return
    fi
    
    echo "📖 查看最近 $lines 行日志..."
    echo ""
    tail -n "$lines" "$LOG_FILE"
}

# 查看错误日志
view_errors() {
    if [ ! -d "$LOG_DIR" ]; then
        echo "❌ 日志目录不存在"
        return
    fi
    
    TODAY=$(date +%Y%m%d)
    LOG_FILE="$LOG_DIR/app_${TODAY}.log"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ 今天的日志文件不存在"
        return
    fi
    
    echo "📖 错误日志："
    echo ""
    grep -i "error\|warning\|❌\|⚠️" "$LOG_FILE"
}

# 搜索日志
search_logs() {
    if [ ! -d "$LOG_DIR" ]; then
        echo "❌ 日志目录不存在"
        return
    fi
    
    TODAY=$(date +%Y%m%d)
    LOG_FILE="$LOG_DIR/app_${TODAY}.log"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ 今天的日志文件不存在"
        return
    fi
    
    read -p "请输入搜索关键词: " keyword
    
    if [ -z "$keyword" ]; then
        echo "❌ 关键词不能为空"
        return
    fi
    
    echo ""
    echo "🔍 搜索结果："
    echo ""
    grep -i "$keyword" "$LOG_FILE"
}

# 清理旧日志
clean_logs() {
    if [ ! -d "$LOG_DIR" ]; then
        echo "❌ 日志目录不存在"
        return
    fi
    
    read -p "确认清理 7 天前的日志？(y/n): " confirm
    if [ "$confirm" = "y" ]; then
        echo "🗑️  清理中..."
        find "$LOG_DIR" -name "app_*.log" -mtime +7 -delete
        echo "✅ 清理完成"
    else
        echo "❌ 已取消"
    fi
}

# 运行测试
run_test() {
    echo "🧪 测试付款流程"
    echo "================"
    echo ""
    
    # 测试1：查看统计
    echo "📊 测试1：查看初始统计"
    curl -s "$BASE_URL/api/stats" | python3 -m json.tool
    echo ""
    echo ""
    
    # 测试2：查询最新未付款记录
    echo "🔍 测试2：查询最新未付款记录"
    curl -s "$BASE_URL/api/latest_recognition" | python3 -m json.tool
    echo ""
    echo ""
    
    # 测试3：上传车牌
    if [ -f "car.jpg" ]; then
        echo "📸 测试3：上传车牌照片"
        RESULT=$(curl -s -X POST "$BASE_URL/api/upload" -F "image=@car.jpg")
        echo "$RESULT" | python3 -m json.tool
        
        RECOGNITION_ID=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('recognition_id', ''))" 2>/dev/null)
        
        if [ -n "$RECOGNITION_ID" ]; then
            echo ""
            echo "🆔 识别ID: $RECOGNITION_ID"
            echo ""
            
            # 测试4：处理付款
            echo "💳 测试4：处理付款"
            curl -s -X POST "$BASE_URL/api/payment" \
                -H "Content-Type: application/json" \
                -d "{\"recognition_id\":\"$RECOGNITION_ID\",\"amount\":\"10\"}" | python3 -m json.tool
            echo ""
            echo ""
            
            # 测试5：查看最终统计
            echo "📊 测试5：查看最终统计"
            curl -s "$BASE_URL/api/stats" | python3 -m json.tool
        fi
    else
        echo "⚠️  未找到 car.jpg 文件，跳过上传测试"
    fi
    
    echo ""
    echo "✅ 测试完成！"
}

# 查看统计
view_stats() {
    echo "📊 系统统计"
    echo "==========="
    echo ""
    curl -s "$BASE_URL/api/stats" | python3 -m json.tool
}

# 主程序
main() {
    # 如果有命令行参数，直接执行
    if [ $# -gt 0 ]; then
        case $1 in
            start)
                start_service
                ;;
            stop)
                stop_service
                ;;
            restart)
                restart_service
                ;;
            status)
                check_status
                ;;
            logs)
                view_logs
                ;;
            logs50)
                view_recent_logs 50
                ;;
            logs100)
                view_recent_logs 100
                ;;
            errors)
                view_errors
                ;;
            search)
                search_logs
                ;;
            clean)
                clean_logs
                ;;
            test)
                run_test
                ;;
            stats)
                view_stats
                ;;
            *)
                echo "❌ 未知命令: $1"
                echo ""
                echo "可用命令："
                echo "  start, stop, restart, status"
                echo "  logs, logs50, logs100, errors, search, clean"
                echo "  test, stats"
                exit 1
                ;;
        esac
        exit 0
    fi
    
    # 交互式菜单
    while true; do
        show_menu
        read -p "请选择 (0-11): " choice
        
        case $choice in
            1)
                start_service
                ;;
            2)
                stop_service
                ;;
            3)
                restart_service
                ;;
            4)
                check_status
                ;;
            5)
                view_logs
                ;;
            6)
                view_recent_logs 50
                ;;
            7)
                view_errors
                ;;
            8)
                search_logs
                ;;
            9)
                clean_logs
                ;;
            10)
                run_test
                ;;
            11)
                view_stats
                ;;
            0)
                echo ""
                echo "👋 再见！"
                exit 0
                ;;
            *)
                echo ""
                echo "❌ 无效选择"
                ;;
        esac
        
        echo ""
        read -p "按 Enter 继续..."
    done
}

# 运行主程序
main "$@"
