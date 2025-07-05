# MIKE21 to Tecplot 转换器

一个专业的MIKE21 DFSU文件到Tecplot格式转换工具，支持GUI界面和命令行操作。

## 🚀 快速开始

### 构建可执行文件

1. **一键构建**（推荐）
   ```bash
   # 双击运行或在命令行执行
   build_release.bat
   ```

2. **手动构建**
   ```bash
   python build_project.py
   ```

### 构建完成后

构建成功后，您会在 `release` 文件夹中找到：
- `MIKE21_Converter.exe` - 主程序
- `启动转换器.bat` - 快速启动脚本
- `使用说明.txt` - 详细使用说明
- `examples/` - 示例文件
- 配置文件和DXF模板

## 📋 系统要求

- Windows 10/11 (64位)
- 至少 4GB 内存
- 1GB 可用磁盘空间

## 🔧 开发环境设置

如果您需要修改源码或重新构建：

1. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **安装PyInstaller**
   ```bash
   pip install pyinstaller
   ```

3. **验证环境**
   ```bash
   python -c "import mikeio, numpy, shapely, ezdxf; print('所有依赖已安装')"
   ```

## 📁 项目结构

```
mikeio/
├── gui.py                    # GUI主程序
├── mike21_converter.py       # 核心转换器
├── license_manager.py        # 授权管理
├── launcher.py              # 启动器
├── build_project.py         # 构建脚本
├── config.yaml              # 配置文件
├── requirements.txt         # Python依赖
├── mike21_converter_final.spec  # PyInstaller配置
├── version_info.txt         # 版本信息
├── dfsu_files/              # DFSU示例文件
├── output/                  # 转换结果
└── release/                 # 构建输出
```

## 🛠️ 功能特性

### 核心功能
- ✅ MIKE21/3 DFSU文件读取
- ✅ 多边形区域裁剪
- ✅ 速度矢量投影
- ✅ Tecplot格式输出
- ✅ 批量文件处理

### 用户界面
- ✅ 现代化GUI界面
- ✅ 实时进度显示
- ✅ 详细日志输出
- ✅ 配置文件管理

### 高级特性
- ✅ 多线程并行处理
- ✅ 内存优化算法
- ✅ 软件授权验证
- ✅ 自动错误恢复

## 📝 使用说明

### GUI模式（推荐）

1. 启动程序后选择DFSU文件
2. 导入DXF裁剪区域和轴线文件
3. 设置输出路径和参数
4. 点击"开始转换"

### 命令行模式

```bash
python launcher.py --cli --input file.dfsu --region region.dxf --axis axis.dxf
```

## 🔍 故障排除

### 常见问题

1. **构建失败 - 缺少依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **exe文件无法启动**
   - 检查是否缺少Visual C++ Redistributable
   - 确保Windows系统已更新

3. **转换失败 - 内存不足**
   - 在config.yaml中调整memory_limit设置
   - 启用lazy_loading模式

### 日志文件

- 构建日志：`build.log`
- 运行日志：`mike21_converter.log`

## 📊 性能优化

### 构建优化
- 使用UPX压缩减小exe体积
- 排除不必要的模块
- 优化依赖包含

### 运行优化
- 多线程并行处理
- 内存映射大文件
- 智能缓存机制

## 🔐 授权信息

本软件包含授权验证功能，支持：
- 离线授权模式
- 在线验证（可选）
- 试用期限制

## 📞 技术支持

- 作者：Powered by Liangyan
- 版本：2.1.0 Professional Edition
- 构建日期：2024年

## 🔄 更新日志

### v2.1.0 (2024)
- ✨ 重新设计构建系统
- 🔧 优化依赖管理
- 🚀 提升打包效率
- 📱 改进用户界面
- 🛡️ 增强错误处理

### v2.0.0
- 🎉 首个稳定版本
- 🖥️ GUI界面支持
- ⚡ 并行处理能力
- 📋 配置文件管理

## 📄 许可证

请遵守软件许可协议使用本程序。

---

> **提示**：首次构建可能需要较长时间下载依赖，请耐心等待。构建成功后，exe文件可以在任何Windows系统上独立运行，无需安装Python环境。
