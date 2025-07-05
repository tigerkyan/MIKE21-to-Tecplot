#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIKE21转换器 - 独立版打包脚本
创建完全独立的可执行文件，包含所有依赖
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import tempfile

def create_standalone_spec():
    """创建独立版的spec文件"""

    # 查找所有必需的文件
    mikecore_files = []
    try:
        import mikecore
        mikecore_dir = Path(mikecore.__file__).parent
        mikecore_bin_dir = mikecore_dir / "bin" / "windows"

        print(f"🔍 mikecore目录: {mikecore_bin_dir}")

        if mikecore_bin_dir.exists():
            for file in mikecore_bin_dir.glob("*"):
                if file.suffix.lower() in ['.dll', '.xml', '.ubg', '.pfs']:
                    mikecore_files.append((str(file), '.'))
                    print(f"  📦 {file.name}")
    except Exception as e:
        print(f"❌ 无法找到mikecore: {e}")

    # 创建spec文件内容
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

# 数据文件列表
datas = [
    ('config.yaml', '.'),
    ('app_icon.ico', '.'),
    ('license.dat', '.'),
    ('line1.dxf', '.'),
    ('line1D.dxf', '.'),
    ('line2.dxf', '.'),
    ('line2D.dxf', '.'),
    ('line1-axis.dxf', '.'),
    ('line1D-axis.dxf', '.'),
    ('line2-axis.dxf', '.'),
    ('line2D-axis.dxf', '.'),
    ('README.md', '.'),
]

# 添加mikecore文件
mikecore_files = {mikecore_files}
datas.extend(mikecore_files)

# 隐藏导入列表
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    '_tkinter',
    'mikeio',
    'mikeio.dataset',
    'mikeio.spatial',
    'mikeio.dfs',
    'mikecore',
    'mikecore.eum',
    'mikecore.DfsFile',
    'mikecore.DfsFileFactory',
    'mikecore.DfsBuilder',
    'numpy',
    'numpy.core',
    'numpy.lib',
    'numpy.linalg',
    'pandas',
    'pandas.core',
    'pandas.io',
    'shapely',
    'shapely.geometry',
    'shapely.ops',
    'ezdxf',
    'ezdxf.document',
    'ezdxf.entities',
    'yaml',
    'pathlib',
    'threading',
    'queue',
    'logging',
    'logging.handlers',
    'multiprocessing',
    'concurrent.futures',
    'ctypes',
    'ctypes.util',
    'pkg_resources',
    'setuptools',
    'importlib_metadata',
    'zipp',
    'PIL',
    'PIL.Image',
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends',
    'matplotlib.backends.backend_tkagg',
    'scipy',
    'scipy.spatial',
    'sqlite3',
    'xml.etree.ElementTree',
    'xml.parsers.expat',
    'unicodedata',
    'locale',
    'encodings',
    'encodings.utf_8',
    'encodings.cp1252',
    'encodings.mbcs',
]

# 排除不需要的模块
excludes = [
    'IPython',
    'jupyter',
    'notebook',
    'matplotlib.tests',
    'numpy.tests',
    'pandas.tests',
    'scipy.tests',
    'sklearn',
    'tensorflow',
    'torch',
    'cv2',
]

# 分析阶段
a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 处理重复文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建目录版本（推荐）
exe_dir = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MIKE21转换器_独立版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)

coll = COLLECT(
    exe_dir,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MIKE21转换器_独立版',
)

# 创建单文件版本
exe_onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MIKE21转换器_单文件独立版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)
'''

    # 写入spec文件
    with open('MIKE21_独立版.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ 创建spec文件: MIKE21_独立版.spec")
    return Path('MIKE21_独立版.spec')

def create_user_manual():
    """创建用户使用手册"""
    manual_content = """# MIKE21转换器独立版 - 使用说明

## 📋 软件简介
MIKE21 to Tecplot 转换器是一款专业的海洋工程数据转换工具，支持将MIKE21 DFSU格式文件转换为Tecplot可读的DAT格式。

## 🚀 主要功能
- ✅ 支持MIKE21 DFSU文件批量转换
- ✅ 支持全场数据导出
- ✅ 支持区域数据提取
- ✅ 支持自定义坐标变换
- ✅ 支持DXF几何文件导入
- ✅ 现代化图形界面
- ✅ 软件授权保护

## 📁 文件说明
```
MIKE21转换器_独立版/
├── MIKE21转换器_独立版.exe      # 主程序
├── config.yaml                 # 配置文件
├── license.dat                 # 授权文件
├── *.dxf                      # DXF几何文件
├── app_icon.ico               # 程序图标
├── README.md                  # 说明文档
└── _internal/                 # 内部依赖文件（不要删除）
```

## 🎯 使用步骤

### 1. 启动程序
双击 `MIKE21转换器_独立版.exe` 启动程序

### 2. 软件激活
首次运行需要输入注册码激活软件

### 3. 配置输入输出
- **输入目录**: 选择包含DFSU文件的文件夹
- **输出目录**: 选择转换结果保存的文件夹

### 4. 设置参数
- **坐标变换**: 设置X、Y坐标偏移量
- **时间设置**: 选择导出的时间步
- **输出设置**: 选择导出选项和精度

### 5. 区域设置（可选）
- 加载DXF几何文件定义感兴趣区域
- 设置区域名称和对应的DXF文件

### 6. 开始转换
点击"开始转换"按钮，程序将自动处理所有DFSU文件

## ⚙️ 配置说明

### 坐标变换
```yaml
coordinate_transform:
  x_shift: 620000    # X坐标偏移量
  y_shift: 3500000   # Y坐标偏移量
```

### 时间设置
```yaml
time_settings:
  time_index: 0      # 0=第一帧, -1=最后帧, null=所有帧
```

### 区域配置
```yaml
regions:
  line1:
    region_dxf: "line1.dxf"
    axis_dxf: "line1-axis.dxf"
  line2:
    region_dxf: "line2.dxf"
    axis_dxf: "line2-axis.dxf"
```

## 📊 输出格式
程序生成标准的Tecplot ASCII格式文件（.dat），包含：
- 坐标信息（X, Y）
- 物理变量数据
- 时间序列数据（如适用）

## ❗ 注意事项
1. **系统要求**: Windows 10/11 64位系统
2. **文件权限**: 确保程序具有读写权限
3. **防病毒软件**: 可能需要添加信任例外
4. **中文路径**: 支持中文文件名和路径
5. **内存使用**: 大文件处理时需要足够内存

## 🔧 故障排除

### 常见问题
1. **程序无法启动**
   - 检查系统是否为64位Windows
   - 尝试以管理员身份运行

2. **转换失败**
   - 检查输入文件格式是否正确
   - 确认DXF文件路径正确
   - 查看日志文件了解详细错误

3. **防病毒误报**
   - 将程序文件夹添加到防病毒软件白名单
   - 使用Windows Defender例外设置

### 日志文件
程序运行时会在输出目录生成 `conversion.log` 文件，包含详细的处理信息和错误消息。

## 📞 技术支持
如有技术问题，请联系: Powered by Liangyan

## 📄 版权信息
版权所有 © 2024 Liangyan
本软件受软件授权协议保护
"""

    with open('使用说明.txt', 'w', encoding='utf-8') as f:
        f.write(manual_content)

    print("✅ 创建使用说明文档")

def build_standalone():
    """构建独立版本"""
    print("🚀 开始构建MIKE21转换器独立版...")

    # 检查必需文件
    required_files = ['gui.py', 'config.yaml', 'app_icon.ico', 'license.dat']
    missing_files = [f for f in required_files if not Path(f).exists()]

    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False

    # 创建spec文件
    spec_file = create_standalone_spec()

    # 创建用户手册
    create_user_manual()

    # 执行打包
    try:
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            str(spec_file)
        ]

        print("🔧 执行打包命令...")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

        if result.returncode == 0:
            print("✅ 独立版构建成功！")

            # 检查输出
            dist_dir = Path('dist')

            # 目录版本
            dir_version = dist_dir / 'MIKE21转换器_独立版'
            if dir_version.exists():
                print(f"📁 目录版本: {dir_version}")

                # 复制使用说明到目录版本
                shutil.copy2('使用说明.txt', dir_version / '使用说明.txt')
                print("📄 已添加使用说明文档")

            # 单文件版本
            exe_file = dist_dir / 'MIKE21转换器_单文件独立版.exe'
            if exe_file.exists():
                size_mb = exe_file.stat().st_size / (1024 * 1024)
                print(f"📱 单文件版本: {exe_file} ({size_mb:.1f} MB)")

            return True

        else:
            print(f"❌ 构建失败!")
            print(f"错误输出: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False

    finally:
        # 清理临时文件
        if spec_file.exists():
            spec_file.unlink()
            print("🧹 清理临时文件")

def main():
    """主函数"""
    print("=" * 70)
    print("🏗️  MIKE21转换器 - 独立版打包工具")
    print("=" * 70)

    if build_standalone():
        print("\n" + "=" * 70)
        print("🎉 独立版构建完成！")
        print("\n📋 构建结果:")
        print("   📁 推荐使用: dist/MIKE21转换器_独立版/ (目录版本)")
        print("   📱 便携版本: dist/MIKE21转换器_单文件独立版.exe")
        print("   📄 使用手册: 使用说明.txt")
        print("\n💡 分发建议:")
        print("   - 目录版本包含所有依赖，兼容性最佳")
        print("   - 单文件版本便于传输，但启动稍慢")
        print("   - 建议连同使用说明一起分发")
        print("=" * 70)
        return True
    else:
        print("\n❌ 构建失败，请检查错误信息")
        return False

if __name__ == "__main__":
    main()
