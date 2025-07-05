#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIKE21转换器 - 完全独立打包脚本
真正的"无环境依赖" - 包含所有必要的DLL
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def find_system_dlls():
    """查找系统必需的DLL文件"""
    dll_paths = []

    # 查找Python安装目录下的DLL
    python_dir = Path(sys.executable).parent

    # 查找mikecore的二进制文件
    try:
        import mikecore
        mikecore_dir = Path(mikecore.__file__).parent
        mikecore_bin_dir = mikecore_dir / "bin" / "windows"

        print(f"🔍 找到mikecore二进制目录: {mikecore_bin_dir}")

        if mikecore_bin_dir.exists():
            # 收集所有mikecore的DLL和数据文件
            for file in mikecore_bin_dir.glob("*"):
                if file.suffix.lower() in ['.dll', '.xml', '.ubg', '.pfs']:
                    dll_paths.append(str(file))
                    print(f"  📦 添加mikecore文件: {file.name}")
        else:
            print("❌ mikecore二进制目录不存在")
    except Exception as e:
        print(f"❌ 无法找到mikecore: {e}")

    # 查找tcl/tk相关DLL
    tcl_dlls = [
        'tcl86t.dll', 'tk86t.dll',  # 可能的tcl/tk版本
        'tcl87t.dll', 'tk87t.dll',
        'tcl90t.dll', 'tk90t.dll',
        'tcl9.0.dll', 'tk9.0.dll'
    ]

    for dll in tcl_dlls:
        dll_path = python_dir / 'DLLs' / dll
        if dll_path.exists():
            dll_paths.append(str(dll_path))

    # 查找其他重要DLL
    other_dlls = [
        'libffi.dll',
        'libcrypto-1_1.dll',
        'libssl-1_1.dll',
        'sqlite3.dll',
        'zlib1.dll'
    ]

    for dll in other_dlls:
        dll_path = python_dir / 'DLLs' / dll
        if dll_path.exists():
            dll_paths.append(str(dll_path))

    return dll_paths

def create_standalone_exe():
    """创建完全独立的可执行文件"""
    print("🚀 开始创建无环境依赖的可执行文件...")

    # 获取所有必需的DLL
    dll_paths = find_system_dlls()

    # 构建PyInstaller命令
    cmd = [
        'pyinstaller',
        '--onefile',                    # 单文件模式
        '--windowed',                   # 无控制台窗口
        '--name=MIKE21转换器_独立版',
        '--clean',                      # 清理临时文件
        '--noconfirm',                  # 不询问覆盖
        '--optimize=2',                 # 优化级别
        '--strip',                      # 去除调试信息

        # 添加配置文件
        '--add-data=config.yaml;.',
        '--add-data=app_icon.ico;.',

        # 添加DXF文件
        '--add-data=line1.dxf;.',
        '--add-data=line1D.dxf;.',
        '--add-data=line2.dxf;.',
        '--add-data=line2D.dxf;.',
        '--add-data=line1-axis.dxf;.',
        '--add-data=line1D-axis.dxf;.',
        '--add-data=line2-axis.dxf;.',
        '--add-data=line2D-axis.dxf;.',

        # 显式包含所有必需模块
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=_tkinter',
        '--hidden-import=mikeio',
        '--hidden-import=numpy',
        '--hidden-import=pandas',
        '--hidden-import=shapely',
        '--hidden-import=ezdxf',
        '--hidden-import=yaml',
        '--hidden-import=matplotlib',
        '--hidden-import=scipy',
        '--hidden-import=PIL',
        '--hidden-import=pkg_resources',
        '--hidden-import=pkg_resources.py2_warn',

        # 收集所有子模块
        '--collect-submodules=mikeio',
        '--collect-submodules=numpy',
        '--collect-submodules=pandas',
        '--collect-submodules=matplotlib',
        '--collect-submodules=scipy',
        '--collect-submodules=shapely',
        '--collect-submodules=ezdxf',
        '--collect-submodules=PIL',

        # 收集所有数据文件
        '--collect-data=mikeio',
        '--collect-data=matplotlib',
        '--collect-data=scipy',
        '--collect-data=shapely',
        '--collect-data=ezdxf',

        # 设置图标
        '--icon=app_icon.ico',

        # 目标文件
        'gui.py'
    ]

    # 添加找到的DLL文件
    for dll_path in dll_paths:
        cmd.append(f'--add-binary={dll_path};.')

    print(f"📦 找到 {len(dll_paths)} 个系统DLL文件")
    print("🔧 执行打包命令...")

    try:
        # 执行打包
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功！")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def create_directory_version():
    """创建目录版本（更稳定）"""
    print("\n🚀 创建目录版本...")

    # 获取所有必需的DLL
    dll_paths = find_system_dlls()

    cmd = [
        'pyinstaller',
        '--onedir',                     # 目录模式
        '--windowed',
        '--name=MIKE21转换器_目录版',
        '--clean',
        '--noconfirm',
        '--optimize=2',

        # 添加数据文件
        '--add-data=config.yaml;.',
        '--add-data=app_icon.ico;.',
        '--add-data=line1.dxf;.',
        '--add-data=line1D.dxf;.',
        '--add-data=line2.dxf;.',
        '--add-data=line2D.dxf;.',
        '--add-data=line1-axis.dxf;.',
        '--add-data=line1D-axis.dxf;.',
        '--add-data=line2-axis.dxf;.',
        '--add-data=line2D-axis.dxf;.',

        # 隐式导入
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=_tkinter',
        '--hidden-import=mikeio',
        '--hidden-import=numpy',
        '--hidden-import=pandas',
        '--hidden-import=shapely',
        '--hidden-import=ezdxf',
        '--hidden-import=yaml',
        '--hidden-import=matplotlib',
        '--hidden-import=scipy',
        '--hidden-import=PIL',

        # 收集模块
        '--collect-submodules=mikeio',
        '--collect-submodules=tkinter',
        '--collect-data=mikeio',
        '--collect-data=matplotlib',

        '--icon=app_icon.ico',
        'gui.py'
    ]

    # 添加DLL文件
    for dll_path in dll_paths:
        cmd.append(f'--add-binary={dll_path};.')

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 目录版本创建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 目录版本创建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 MIKE21转换器 - 完全独立打包工具")
    print("=" * 60)

    # 检查必需文件
    required_files = ['gui.py', 'config.yaml', 'app_icon.ico']
    missing_files = [f for f in required_files if not Path(f).exists()]

    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False

    # 先创建目录版本（更稳定）
    if create_directory_version():
        print("\n🎉 目录版本打包完成！")

        # 再尝试创建单文件版本
        if create_standalone_exe():
            print("\n🎉 单文件版本也打包完成！")
        else:
            print("\n⚠️  单文件版本失败，但目录版本可用")
    else:
        print("\n❌ 打包失败")
        return False

    print("\n" + "=" * 60)
    print("📋 打包结果:")
    print("   - 目录版本: dist/MIKE21转换器_目录版/")
    print("   - 单文件版本: dist/MIKE21转换器_独立版.exe")
    print("=" * 60)

    return True

if __name__ == "__main__":
    main()
