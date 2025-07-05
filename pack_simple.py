#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIKE21转换器 - 简化打包脚本
无版本信息文件的简化打包方案
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def find_mikecore_files():
    """查找mikecore的所有必需文件"""
    files = []

    try:
        import mikecore
        mikecore_dir = Path(mikecore.__file__).parent
        mikecore_bin_dir = mikecore_dir / "bin" / "windows"

        print(f"🔍 找到mikecore目录: {mikecore_bin_dir}")

        if mikecore_bin_dir.exists():
            for file in mikecore_bin_dir.glob("*"):
                if file.suffix.lower() in ['.dll', '.xml', '.ubg', '.pfs']:
                    files.append(str(file))
                    print(f"  📦 添加: {file.name}")

        return files
    except Exception as e:
        print(f"❌ 无法找到mikecore: {e}")
        return []

def create_simple_onedir():
    """创建简化的目录版本"""
    print("🚀 创建简化目录版本...")

    # 获取mikecore文件
    mikecore_files = find_mikecore_files()

    # 基础命令
    cmd = [
        'pyinstaller',
        '--onedir',
        '--windowed',
        '--name=MIKE21转换器_简化版',
        '--clean',
        '--noconfirm',

        # 添加数据文件
        '--add-data=config.yaml;.',
        '--add-data=app_icon.ico;.',
        '--add-data=*.dxf;.',

        # 隐式导入
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=_tkinter',
        '--hidden-import=mikeio',
        '--hidden-import=mikecore',
        '--hidden-import=numpy',
        '--hidden-import=pandas',
        '--hidden-import=yaml',
        '--hidden-import=pathlib',
        '--hidden-import=threading',
        '--hidden-import=queue',
        '--hidden-import=logging',

        # 收集数据
        '--collect-data=mikeio',
        '--collect-data=mikecore',

        # 图标
        '--icon=app_icon.ico',

        # 目标文件
        'gui.py'
    ]

    # 添加mikecore文件
    for file_path in mikecore_files:
        cmd.append(f'--add-binary={file_path};.')

    print(f"📦 包含 {len(mikecore_files)} 个mikecore文件")

    try:
        print("🔧 开始打包...")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("✅ 目录版本打包成功！")
            return True
        else:
            print(f"❌ 打包失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 打包过程中发生错误: {e}")
        return False

def create_simple_onefile():
    """创建简化的单文件版本"""
    print("\n🚀 创建简化单文件版本...")

    # 获取mikecore文件
    mikecore_files = find_mikecore_files()

    # 基础命令
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=MIKE21转换器_单文件版',
        '--clean',
        '--noconfirm',

        # 添加数据文件
        '--add-data=config.yaml;.',
        '--add-data=app_icon.ico;.',
        '--add-data=*.dxf;.',

        # 隐式导入
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=_tkinter',
        '--hidden-import=mikeio',
        '--hidden-import=mikecore',
        '--hidden-import=numpy',
        '--hidden-import=pandas',
        '--hidden-import=yaml',

        # 收集数据
        '--collect-data=mikeio',
        '--collect-data=mikecore',

        # 图标
        '--icon=app_icon.ico',

        # 目标文件
        'gui.py'
    ]

    # 添加mikecore文件
    for file_path in mikecore_files:
        cmd.append(f'--add-binary={file_path};.')

    try:
        print("🔧 开始打包...")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("✅ 单文件版本打包成功！")
            return True
        else:
            print(f"❌ 打包失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 打包过程中发生错误: {e}")
        return False

def test_gui_locally():
    """本地测试GUI"""
    print("\n🧪 测试GUI界面...")
    try:
        result = subprocess.run([sys.executable, 'gui.py'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ GUI测试通过")
        else:
            print(f"⚠️ GUI测试警告: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("✅ GUI启动正常（超时结束测试）")
    except Exception as e:
        print(f"❌ GUI测试失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 MIKE21转换器 - 简化打包工具")
    print("=" * 60)

    # 检查必需文件
    required_files = ['gui.py', 'config.yaml', 'app_icon.ico']
    missing_files = [f for f in required_files if not Path(f).exists()]

    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False

    # 测试本地GUI
    test_gui_locally()

    success_count = 0

    # 创建目录版本
    if create_simple_onedir():
        success_count += 1
        print("\n🎉 目录版本创建成功！")

        # 检查输出
        dist_dir = Path('dist') / 'MIKE21转换器_简化版'
        if dist_dir.exists():
            exe_path = dist_dir / 'MIKE21转换器_简化版.exe'
            if exe_path.exists():
                print(f"📍 目录版本位置: {dist_dir}")
                print(f"📱 可执行文件: {exe_path}")

    # 创建单文件版本
    if create_simple_onefile():
        success_count += 1
        print("\n🎉 单文件版本创建成功！")

        # 检查输出
        exe_path = Path('dist') / 'MIKE21转换器_单文件版.exe'
        if exe_path.exists():
            print(f"📱 单文件版本: {exe_path}")
            print(f"📏 文件大小: {exe_path.stat().st_size / (1024*1024):.1f} MB")

    # 清理临时文件
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        try:
            spec_file.unlink()
            print(f"🧹 清理: {spec_file}")
        except:
            pass

    print("\n" + "=" * 60)
    if success_count > 0:
        print(f"✅ 成功创建了 {success_count} 个版本")
        print("\n📋 使用说明:")
        print("1. 优先使用目录版本（兼容性更好）")
        print("2. 单文件版本适合单独分发")
        print("3. 首次运行可能需要允许防火墙权限")
        print("4. 如遇到杀毒软件误报，请添加信任例外")
    else:
        print("❌ 所有打包尝试都失败了")
    print("=" * 60)

    return success_count > 0

if __name__ == "__main__":
    main()
