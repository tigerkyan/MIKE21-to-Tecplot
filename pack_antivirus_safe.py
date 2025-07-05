#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIKE21转换器 - 防病毒误报优化打包脚本
减少Windows Defender误报的专用打包工具
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import tempfile

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

def create_version_info():
    """创建版本信息文件以减少误报"""
    version_info = """# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 1, 0, 0),
    prodvers=(2, 1, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'080404B0',
        [StringStruct(u'CompanyName', u'Powered by Liangyan'),
        StringStruct(u'FileDescription', u'MIKE21 to Tecplot Data Converter'),
        StringStruct(u'FileVersion', u'2.1.0.0'),
        StringStruct(u'InternalName', u'MIKE21Converter'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024 Liangyan'),
        StringStruct(u'OriginalFilename', u'MIKE21Converter.exe'),
        StringStruct(u'ProductName', u'MIKE21 Data Converter Professional'),
        StringStruct(u'ProductVersion', u'2.1.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)"""

    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info.strip())

    print("✅ 创建版本信息文件")
    return True

def create_clean_exe():
    """创建减少误报的可执行文件"""
    print("🚀 开始创建防误报优化的可执行文件...")

    # 创建版本信息
    create_version_info()

    # 获取所有必需的DLL
    dll_paths = find_system_dlls()

    # 构建PyInstaller命令 - 优化参数以减少误报
    cmd = [
        'pyinstaller',
        '--onefile',                    # 单文件模式
        '--windowed',                   # 无控制台窗口
        '--name=MIKE21转换器',           # 简化名称，避免特殊字符
        '--clean',                      # 清理临时文件
        '--noconfirm',                  # 不询问覆盖
        '--optimize=1',                 # 降低优化级别，减少压缩
        '--noupx',                      # 不使用UPX压缩（常被误报）
        '--debug=bootloader',           # 添加调试信息

        # 添加版本信息
        '--version-file=version_info.txt',

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

        # 收集数据文件
        '--collect-data=mikeio',
        '--collect-data=matplotlib',

        # 设置图标
        '--icon=app_icon.ico',

        # 目标文件
        'gui.py'
    ]

    # 添加找到的DLL文件
    for dll_path in dll_paths:
        cmd.append(f'--add-binary={dll_path};.')

    print(f"📦 找到 {len(dll_paths)} 个系统DLL文件")
    print("🔧 执行优化打包命令...")

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
    """创建目录版本（推荐用于分发）"""
    print("\n🚀 创建目录版本（推荐用于分发）...")

    # 获取所有必需的DLL
    dll_paths = find_system_dlls()

    cmd = [
        'pyinstaller',
        '--onedir',                     # 目录模式
        '--windowed',
        '--name=MIKE21转换器',
        '--clean',
        '--noconfirm',
        '--optimize=1',                 # 降低优化级别
        '--noupx',                      # 不使用UPX压缩

        # 添加版本信息
        '--version-file=version_info.txt',

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

def create_readme_for_users():
    """创建用户说明文件"""
    readme_content = """# MIKE21转换器 - 防病毒软件说明

## 关于Windows Defender误报

本软件是使用Python和PyInstaller构建的合法应用程序，可能会被某些杀毒软件误报为病毒。这是因为：

1. **PyInstaller特性**: PyInstaller将Python脚本打包成可执行文件，这种行为可能被杀毒软件误判
2. **动态代码加载**: 程序需要动态加载数据处理库，可能触发启发式检测
3. **文件操作**: 程序需要读写文件，进行数据转换操作

## 如何解决误报问题

### 方法1: 添加信任例外
1. 打开Windows Defender安全中心
2. 转到"病毒和威胁防护"
3. 点击"病毒和威胁防护设置"
4. 在"排除项"中添加程序文件夹路径

### 方法2: 使用目录版本
- 推荐使用目录版本而非单文件版本
- 目录版本误报概率更低
- 运行 `MIKE21转换器/MIKE21转换器.exe`

### 方法3: 临时禁用实时保护
1. 在Windows Defender中临时关闭实时保护
2. 运行程序
3. 运行完成后重新启用保护

## 软件安全性保证

- ✅ 源代码完全开源透明
- ✅ 无任何恶意代码
- ✅ 仅用于MIKE21数据转换
- ✅ 不访问网络，不收集用户数据
- ✅ 不修改系统文件

## 数字签名

由于个人开发者获取代码签名证书成本较高，本软件暂未进行数字签名。
如需企业级部署，建议联系开发者获取签名版本。

## 联系方式

如有疑问，请联系: Powered by Liangyan
"""

    with open('防病毒说明.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("✅ 创建用户说明文件")

def main():
    """主函数"""
    print("=" * 70)
    print("🛡️  MIKE21转换器 - 防病毒误报优化打包工具")
    print("=" * 70)

    # 检查必需文件
    required_files = ['gui.py', 'config.yaml', 'app_icon.ico']
    missing_files = [f for f in required_files if not Path(f).exists()]

    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False

    # 创建用户说明
    create_readme_for_users()

    # 先创建目录版本（推荐）
    if create_directory_version():
        print("\n🎉 目录版本打包完成！（推荐使用）")

        # 再尝试创建单文件版本
        if create_clean_exe():
            print("\n🎉 单文件版本也打包完成！")
        else:
            print("\n⚠️  单文件版本失败，请使用目录版本")
    else:
        print("\n❌ 打包失败")
        return False

    # 清理临时文件
    if Path('version_info.txt').exists():
        Path('version_info.txt').unlink()

    print("\n" + "=" * 70)
    print("📋 打包结果:")
    print("   🎯 推荐使用: dist/MIKE21转换器/ (目录版本)")
    print("   📦 备选方案: dist/MIKE21转换器.exe (单文件版本)")
    print("   📄 用户说明: 防病毒说明.txt")
    print("\n💡 使用建议:")
    print("   - 优先使用目录版本，误报概率更低")
    print("   - 将整个文件夹加入杀毒软件白名单")
    print("   - 首次运行时选择'允许'或'信任'")
    print("=" * 70)

    return True

if __name__ == "__main__":
    main()
