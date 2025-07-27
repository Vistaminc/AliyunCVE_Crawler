#!/usr/bin/env python3
"""
创建桌面快捷方式

为AliyunCVE_Crawler GUI创建桌面快捷方式
"""

import os
import sys
from pathlib import Path


def create_windows_shortcut():
    """创建Windows桌面快捷方式"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        # 获取桌面路径
        desktop = winshell.desktop()
        
        # 快捷方式路径
        shortcut_path = os.path.join(desktop, "AliyunCVE_Crawler.lnk")
        
        # 项目路径
        project_dir = Path(__file__).parent.absolute()
        target = sys.executable
        arguments = str(project_dir / "run_gui.py")
        working_dir = str(project_dir)
        
        # 创建快捷方式
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = working_dir
        shortcut.Description = "AliyunCVE_Crawler - 阿里云CVE爬虫图形界面"
        shortcut.save()
        
        print(f"Windows快捷方式已创建: {shortcut_path}")
        return True
        
    except ImportError:
        print("需要安装 pywin32 和 winshell:")
        print("pip install pywin32 winshell")
        return False
    except Exception as e:
        print(f"创建Windows快捷方式失败: {e}")
        return False


def create_linux_desktop_file():
    """创建Linux桌面文件"""
    try:
        # 获取用户桌面目录
        desktop_dir = Path.home() / "Desktop"
        if not desktop_dir.exists():
            desktop_dir = Path.home() / "桌面"
        
        if not desktop_dir.exists():
            print("未找到桌面目录")
            return False
        
        # 项目路径
        project_dir = Path(__file__).parent.absolute()
        
        # 桌面文件内容
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=AliyunCVE_Crawler
Comment=阿里云CVE爬虫图形界面
Exec={sys.executable} {project_dir / "run_gui.py"}
Path={project_dir}
Icon=applications-internet
Terminal=false
Categories=Network;Security;
"""
        
        # 创建桌面文件
        desktop_file = desktop_dir / "aliyuncve-crawler.desktop"
        with open(desktop_file, 'w', encoding='utf-8') as f:
            f.write(desktop_content)
        
        # 设置可执行权限
        os.chmod(desktop_file, 0o755)
        
        print(f"Linux桌面文件已创建: {desktop_file}")
        return True
        
    except Exception as e:
        print(f"创建Linux桌面文件失败: {e}")
        return False


def create_macos_app():
    """创建macOS应用程序（简化版）"""
    try:
        # 获取桌面路径
        desktop_dir = Path.home() / "Desktop"
        
        # 项目路径
        project_dir = Path(__file__).parent.absolute()
        
        # 创建应用程序包目录结构
        app_dir = desktop_dir / "AliyunCVE_Crawler.app"
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        
        # 创建目录
        macos_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建Info.plist
        info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>vistamin-launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.vistamin.cve-crawler</string>
    <key>CFBundleName</key>
    <string>AliyunCVE_Crawler</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>"""
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(info_plist)
        
        # 创建启动脚本
        launcher_script = f"""#!/bin/bash
cd "{project_dir}"
{sys.executable} run_gui.py
"""
        
        launcher_path = macos_dir / "aliyuncve-launcher"
        with open(launcher_path, 'w') as f:
            f.write(launcher_script)
        
        # 设置可执行权限
        os.chmod(launcher_path, 0o755)
        
        print(f"macOS应用程序已创建: {app_dir}")
        return True
        
    except Exception as e:
        print(f"创建macOS应用程序失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("🛡️ AliyunCVE_Crawler - 快捷方式创建工具")
    print("=" * 50)
    
    # 检测操作系统
    system = sys.platform.lower()
    
    if system.startswith('win'):
        print("检测到Windows系统，创建桌面快捷方式...")
        success = create_windows_shortcut()
    elif system.startswith('linux'):
        print("检测到Linux系统，创建桌面文件...")
        success = create_linux_desktop_file()
    elif system.startswith('darwin'):
        print("检测到macOS系统，创建应用程序...")
        success = create_macos_app()
    else:
        print(f"不支持的操作系统: {system}")
        success = False
    
    if success:
        print("\n✅ 快捷方式创建成功！")
        print("现在可以从桌面直接启动AliyunCVE_Crawler GUI了。")
    else:
        print("\n❌ 快捷方式创建失败。")
        print("您仍然可以通过以下命令启动GUI:")
        print("python run_gui.py")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
