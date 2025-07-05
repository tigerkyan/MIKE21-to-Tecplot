# MIKE21 to Tecplot 转换器

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

一个专业的 MIKE21 DFSU 文件到 Tecplot 格式转换工具，支持 GUI 界面和命令行操作。

## ✨ 主要功能

- 🔄 **批量转换**：支持 MIKE21 DFSU 文件批量转换为 Tecplot DAT 格式
- 🌍 **全场数据导出**：完整导出所有网格点的数据
- 📍 **区域数据提取**：支持基于 DXF 几何文件的区域数据提取
- 🗺️ **坐标变换**：支持自定义坐标系统变换
- 🎨 **现代化界面**：直观的图形用户界面，操作简便
- ⚡ **高性能处理**：优化的算法，快速处理大型数据文件
- 🔐 **授权保护**：内置许可证管理系统

## 📁 项目结构

```
MIKE21-to-Tecplot/
├── 📄 主程序文件
│   ├── mike21_converter.py      # 核心转换模块
│   ├── gui.py                   # 图形界面
│   ├── license_manager.py       # 许可证管理
│   └── projection_fix.py        # 投影修正
├── 🔧 打包脚本
│   ├── pack_standalone_final.py # 最终独立版打包
│   ├── pack_standalone.py       # 独立版打包
│   ├── pack_simple.py          # 简化版打包
│   └── pack_antivirus_safe.py   # 防病毒安全版打包
├── ⚙️ 配置文件
│   ├── config.yaml              # 主配置文件
│   ├── requirements.txt         # Python 依赖
│   └── *.spec                   # PyInstaller 配置
├── 📐 DXF 几何文件
│   ├── line1.dxf               # 线性几何 1
│   ├── line1-axis.dxf          # 线性几何 1 (轴向)
│   ├── line2.dxf               # 线性几何 2
│   └── line2-axis.dxf          # 线性几何 2 (轴向)
├── 📚 文档
│   ├── README.md               # 项目说明
│   ├── 使用说明.txt             # 详细使用说明
│   └── 防病毒说明.txt           # 防病毒软件说明
└── 📦 构建输出
    ├── build/                  # PyInstaller 构建缓存
    ├── dist/                   # 分发文件
    └── MIKE21转换器_最终版/     # 最终发布版本
```

## 🚀 快速开始

### 方式一：使用预编译版本（推荐）

1. 下载发布版本或从 `MIKE21转换器_最终版/` 目录获取
2. 双击 `MIKE21转换器_独立版.exe` 启动程序
3. 按照界面提示进行文件转换

### 方式二：从源码运行

1. **克隆仓库**
   ```bash
   git clone https://github.com/tigerkyan/MIKE21-to-Tecplot.git
   cd MIKE21-to-Tecplot
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python gui.py
   ```

## 📋 系统要求

- **操作系统**：Windows 10/11 (64位)
- **内存**：至少 4GB RAM（推荐 8GB+）
- **磁盘空间**：1GB 可用空间
- **Python**：3.8+ （仅源码运行需要）

## 🔧 开发环境设置

### 安装开发依赖

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 验证环境

```bash
python -c "import mikeio, numpy, shapely, ezdxf; print('所有依赖已安装')"
```

### 构建可执行文件

提供多种打包选项：

1. **最终独立版**（推荐）
   ```bash
   python pack_standalone_final.py
   ```

2. **标准独立版**
   ```bash
   python pack_standalone.py
   ```

3. **简化版**
   ```bash
   python pack_simple.py
   ```

4. **防病毒安全版**
   ```bash
   python pack_antivirus_safe.py
   ```

## 📖 使用说明

### 基本操作流程

1. **启动程序**：双击可执行文件或运行 `python gui.py`
2. **选择输入文件**：点击"浏览"选择 DFSU 文件
3. **配置输出**：设置输出目录和转换参数
4. **开始转换**：点击"开始转换"按钮
5. **查看结果**：转换完成后在输出目录查看 DAT 文件

### 高级功能

- **区域提取**：导入 DXF 文件定义提取区域
- **时间步选择**：指定转换特定时间步的数据
- **坐标变换**：配置自定义投影参数
- **批量处理**：一次性转换多个 DFSU 文件

## ⚙️ 配置文件

编辑 `config.yaml` 自定义程序行为：

```yaml
# 应用程序设置
app:
  name: "MIKE21 to Tecplot 转换器"
  version: "2.1.0"

# 默认路径
paths:
  dfsu_files: "./dfsu_files"
  output_dir: "./output"
  dxf_files: "."

# 转换设置
conversion:
  default_time_step: 0  # 0=首帧，null=所有时间步
```

## 🐛 故障排除

### 常见问题

1. **程序无法启动**
   - 检查是否有 `license.dat` 授权文件
   - 确保所有 DLL 依赖文件完整

2. **转换失败**
   - 验证 DFSU 文件格式正确性
   - 检查输出目录写入权限

3. **防病毒软件误报**
   - 参考 `防病毒说明.txt` 文件
   - 使用防病毒安全版打包脚本

### 日志文件

程序运行日志保存在：
- `mike21_converter.log` - 主程序日志
- `output/conversion.log` - 转换过程日志

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- **作者**：Liangyan
- **项目地址**：https://github.com/tigerkyan/MIKE21-to-Tecplot
- **问题反馈**：通过 GitHub Issues 报告问题

## 🙏 致谢

- [MIKE IO](https://github.com/DHI/mikeio) - MIKE21 文件读取支持
- [NumPy](https://numpy.org/) - 数值计算支持
- [Shapely](https://shapely.readthedocs.io/) - 几何计算支持
- [ezdxf](https://ezdxf.readthedocs.io/) - DXF 文件处理支持

---

⭐ 如果这个项目对您有帮助，请给个 Star！
