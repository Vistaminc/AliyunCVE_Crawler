#!/usr/bin/env python3
"""
AliyunCVE_Crawler GUI启动器

快速启动图形界面的便捷脚本
"""

import sys
import os
import subprocess
from pathlib import Path


def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'ttkbootstrap',
        'playwright',
        'loguru',
        'aiofiles'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages


def install_dependencies():
    """安装缺失的依赖"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False


def install_playwright():
    """安装Playwright浏览器"""
    print("正在安装Playwright浏览器...")
    try:
        subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
        print("Playwright浏览器安装完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Playwright安装失败: {e}")
        return False


def create_directories():
    """创建必要的目录"""
    directories = [
        'data/aliyun_cve',
        'logs',
        'monitoring_data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("目录结构创建完成！")


def main():
    """主函数"""
    print("=" * 50)
    print("CVE爬虫 GUI启动器")
    print("=" * 50)
    
    # 检查依赖
    print("检查依赖包...")
    missing = check_dependencies()
    
    if missing:
        print(f"缺少以下依赖包: {', '.join(missing)}")
        
        response = input("是否自动安装缺失的依赖？(y/n): ").lower().strip()
        if response in ['y', 'yes', '是']:
            if not install_dependencies():
                print("依赖安装失败，请手动安装后重试")
                return
            
            # 检查是否需要安装Playwright
            try:
                import playwright
                if not install_playwright():
                    print("Playwright安装失败，请手动安装后重试")
                    return
            except ImportError:
                pass
        else:
            print("请手动安装依赖后重试")
            return
    
    # 创建目录
    create_directories()
    
    # 启动GUI
    print("启动图形界面...")
    try:
        from gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"导入GUI模块失败: {e}")
        print("请确保所有依赖都已正确安装")
    except Exception as e:
        print(f"启动GUI失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
