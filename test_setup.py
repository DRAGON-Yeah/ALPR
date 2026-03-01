#!/usr/bin/env python3
"""测试系统配置"""

import os
import sys

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠ 警告: 建议使用 Python 3.8 或更高版本")
        return False
    return True

def check_env_file():
    """检查环境变量文件"""
    if os.path.exists('.env'):
        print("✓ .env 文件存在")
        return True
    else:
        print("✗ .env 文件不存在，请复制 .env.example 并配置")
        return False

def check_directories():
    """检查必要的目录"""
    dirs = ['templates', 'static/css', 'static/js', 'uploads']
    all_exist = True
    for d in dirs:
        if os.path.exists(d):
            print(f"✓ 目录 {d} 存在")
        else:
            print(f"✗ 目录 {d} 不存在")
            all_exist = False
    return all_exist

def check_files():
    """检查必要的文件"""
    files = [
        'app.py',
        'ai_service.py',
        'requirements.txt',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    all_exist = True
    for f in files:
        if os.path.exists(f):
            print(f"✓ 文件 {f} 存在")
        else:
            print(f"✗ 文件 {f} 不存在")
            all_exist = False
    return all_exist

def main():
    print("=" * 50)
    print("车牌识别系统 - 配置检查")
    print("=" * 50)
    print()
    
    checks = [
        ("Python 版本", check_python_version),
        ("环境变量", check_env_file),
        ("目录结构", check_directories),
        ("必要文件", check_files)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n检查 {name}:")
        print("-" * 50)
        results.append(check_func())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ 所有检查通过！")
        print("\n下一步:")
        print("1. 创建虚拟环境: python3 -m venv .venv")
        print("2. 激活虚拟环境: source .venv/bin/activate")
        print("3. 安装依赖: pip install -r requirements.txt")
        print("4. 配置 .env 文件（选择 ollama 或 minimax）")
        print("5. 运行应用: python app.py")
        print("\n或者直接运行: ./run.sh")
    else:
        print("✗ 部分检查未通过，请修复后再运行")
    print("=" * 50)

if __name__ == '__main__':
    main()
