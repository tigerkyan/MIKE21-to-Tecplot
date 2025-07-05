#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIKE21转换器 - 简化防病毒优化打包脚本
减少Windows Defender误报的专用打包工具（无版本信息文件）
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
        'tcl86t.dll', 'tk86t.dll',
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

def create_directory_version():
    """创建目录版本（推荐用于分发，减少误报）"""
    print("🚀 创建防病毒优化目录版本...")
    
    # 获取所有必需的DLL
    dll_paths = find_system_dlls()
    
    cmd = [
        'pyinstaller',
        '--onedir',                     # 目录模式（减少误报）
        '--windowed',                   # 无控制台窗口
        '--name=MIKE21Converter',       # 使用英文名称，避免中文路径问题
        '--clean',                      # 清理临时文件
        '--noconfirm',                  # 不询问覆盖
        '--optimize=0',                 # 不优化（避免被误判为加壳）
        '--noupx',                      # 不使用UPX压缩（常被误报）
        '--debug=bootloader',           # 添加调试信息
        '--exclude-module=matplotlib.tests',  # 排除测试模块
        '--exclude-module=scipy.tests',
        '--exclude-module=pandas.tests',
        
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
        
        # 收集数据文件
        '--collect-data=mikeio',
        '--collect-data=matplotlib',
        
        # 设置图标
        '--icon=app_icon.ico',
        
        # 目标文件
        'gui.py'
    ]
    
    # 添加DLL文件
    for dll_path in dll_paths:
        cmd.append(f'--add-binary={dll_path};.')
    
    print(f"📦 找到 {len(dll_paths)} 个系统DLL文件")
    print("🔧 执行防病毒优化打包...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 目录版本创建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 目录版本创建失败: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr[-500:]}")  # 只显示最后500字符
        return False

def create_single_file_version():
    """创建单文件版本（备用选项）"""
    print("\n🚀 创建单文件版本...")
    
    # 获取所有必需的DLL
    dll_paths = find_system_dlls()
    
    cmd = [
        'pyinstaller',
        '--onefile',                    # 单文件模式
        '--windowed',                   # 无控制台窗口
        '--name=MIKE21Converter_Single', # 英文名称
        '--clean',
        '--noconfirm',
        '--optimize=0',                 # 不优化
        '--noupx',                      # 不使用UPX压缩
        '--exclude-module=matplotlib.tests',
        '--exclude-module=scipy.tests',
        '--exclude-module=pandas.tests',
        
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
        
        # 收集数据文件
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
        print("✅ 单文件版本创建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 单文件版本创建失败: {e}")
        return False

def create_antivirus_instructions():
    """创建防病毒软件使用说明"""
    instructions = """# MIKE21转换器 - 防病毒软件配置指南

## 🛡️ 关于Windows Defender误报

PyInstaller打包的程序经常被杀毒软件误报，这是正常现象，原因如下：

### 误报原因
1. **启发式检测**: 杀毒软件对自解压程序比较敏感
2. **动态加载**: Python程序需要动态加载大量库文件
3. **无数字签名**: 个人开发者难以获得代码签名证书

## 🔧 解决方案

### 方案1: 添加白名单（推荐）
1. 打开Windows安全中心
2. 点击"病毒和威胁防护"
3. 在"病毒和威胁防护设置"中点击"管理设置"
4. 向下滚动到"排除项"，点击"添加或删除排除项"
5. 点击"添加排除项" → "文件夹"
6. 选择程序所在的整个文件夹

### 方案2: 临时禁用实时保护
1. 打开Windows安全中心
2. 转到"病毒和威胁防护"
3. 在"病毒和威胁防护设置"中，将"实时保护"关闭
4. 运行程序
5. 使用完毕后重新启用实时保护

### 方案3: 使用目录版本
- 目录版本比单文件版本误报概率更低
- 推荐使用: `MIKE21Converter/MIKE21Converter.exe`

## ✅ 软件安全保证

- 源代码开源透明
- 仅用于数据格式转换
- 不联网，不收集数据
- 不修改系统设置
- 不访问敏感信息

## 📞 技术支持

如有疑问请联系: Powered by Liangyan
"""
    
    with open('防病毒配置指南.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ 创建防病毒配置指南")

def main():
    """主函数"""
    print("=" * 70)
    print("🛡️  MIKE21转换器 - 防病毒优化打包工具 v2.0")
    print("=" * 70)
    
    # 检查必需文件
    required_files = ['gui.py', 'config.yaml', 'app_icon.ico']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False
    
    # 创建使用说明
    create_antivirus_instructions()
    
    success_count = 0
    
    # 先创建目录版本（推荐）
    if create_directory_version():
        success_count += 1
        print("\n🎉 目录版本打包完成！（推荐使用，误报率最低）")
        
        # 再尝试创建单文件版本
        if create_single_file_version():
            success_count += 1
            print("\n🎉 单文件版本也打包完成！")
        else:
            print("\n⚠️  单文件版本失败，但目录版本可用")
    else:
        print("\n❌ 目录版本打包失败")
        return False
    
    print("\n" + "=" * 70)
    print("📋 打包结果:")
    print(f"   🎯 主要版本: dist/MIKE21Converter/ (推荐使用)")
    if success_count > 1:
        print(f"   📦 备用版本: dist/MIKE21Converter_Single.exe")
    print(f"   📄 使用指南: 防病毒配置指南.txt")
    
    print("\n💡 防误报建议:")
    print("   1. 优先使用目录版本 (MIKE21Converter/)")
    print("   2. 将程序目录添加到Windows Defender白名单")
    print("   3. 首次运行选择'仍要运行'或'允许'")
    print("   4. 如果被删除，请按说明文件操作")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()
