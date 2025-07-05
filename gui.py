#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIKE21 to Tecplot 转换器 GUI
带软件授权验证的主界面

作者: Powered by Liangyan
版本: 2.1 - 添加软件授权和自定义图标
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import queue
from pathlib import Path

# 导入授权管理器
from license_manager import check_license_and_activate, LicenseManager

import yaml
from mike21_converter import MIKE21Converter
import logging


class ConverterGUI:
    """MIKE21转换器图形界面"""

    def __init__(self, root):
        self.root = root

        # 设置应用程序图标
        try:
            if Path("app_icon.ico").exists():
                self.root.iconbitmap("app_icon.ico")
        except:
            pass

        self.root.title("MIKE21 to Tecplot 转换器 v2.1 - Professional Edition")
        self.root.geometry("900x750")
        self.root.resizable(True, True)

        # 设置窗口背景色为浅色主题
        self.root.configure(bg='#f5f5f5')

        # 初始化授权管理器
        self.license_manager = LicenseManager()

        # 配置现代化样式主题
        self.setup_modern_theme()

        # 添加菜单栏
        self.create_menu()

        # 初始化变量
        self.config = self.load_default_config()
        self.converter = None
        self.processing = False

        # 创建消息队列用于线程间通信
        self.message_queue = queue.Queue()

        # 创建界面
        self.create_widgets()
        self.update_display()

        # 启动消息处理
        self.process_queue()

    def setup_modern_theme(self):
        """设置浅色主题样式（楷体字体）"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配置浅色主题颜色方案
        style.configure('TLabel',
                       background='#f5f5f5',
                       foreground='#333333',
                       font=('楷体', 10))

        style.configure('TFrame',
                       background='#f5f5f5',
                       relief='flat')

        style.configure('TLabelFrame',
                       background='#f5f5f5',
                       foreground='#333333',
                       font=('楷体', 11, 'bold'))

        style.configure('TLabelFrame.Label',
                       background='#f5f5f5',
                       foreground='#1e7b85')

        style.configure('TButton',
                       background='#4a90e2',
                       foreground='white',
                       font=('楷体', 10),
                       borderwidth=1,
                       focuscolor='none')

        style.map('TButton',
                 background=[('active', '#357abd'),
                           ('pressed', '#2868a3')])

        style.configure('TEntry',
                       fieldbackground='#ffffff',
                       foreground='#333333',
                       bordercolor='#4a90e2',
                       lightcolor='#4a90e2',
                       darkcolor='#4a90e2',
                       font=('楷体', 10))

        style.configure('TNotebook',
                       background='#f5f5f5',
                       borderwidth=1)

        style.configure('TNotebook.Tab',
                       background='#e8e8e8',
                       foreground='#333333',
                       padding=[12, 8],
                       font=('楷体', 10))

        style.map('TNotebook.Tab',
                 background=[('selected', '#ffffff'),
                           ('active', '#f0f0f0')])

        style.configure('Treeview',
                       background='#ffffff',
                       foreground='#333333',
                       fieldbackground='#ffffff',
                       font=('楷体', 9))

        style.configure('Treeview.Heading',
                       background='#e8e8e8',
                       foreground='#333333',
                       font=('楷体', 10, 'bold'))

        style.configure('TScrollbar',
                       background='#e8e8e8',
                       troughcolor='#f5f5f5',
                       bordercolor='#d0d0d0',
                       arrowcolor='#666666',
                       darkcolor='#d0d0d0',
                       lightcolor='#ffffff')

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root, bg='#f5f5f5', fg='#333333',
                         activebackground='#4a90e2', activeforeground='#ffffff',
                         font=('楷体', 9))
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0, bg='#f5f5f5', fg='#333333',
                           activebackground='#4a90e2', activeforeground='#ffffff',
                           font=('楷体', 9))
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开配置", command=self.load_config)
        file_menu.add_command(label="保存配置", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0, bg='#f5f5f5', fg='#333333',
                           activebackground='#4a90e2', activeforeground='#ffffff',
                           font=('楷体', 9))
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="软件授权", command=self.show_license_info)
        help_menu.add_command(label="重新激活", command=self.reactivate_software)
        help_menu.add_separator()
        help_menu.add_command(label="关于软件", command=self.show_about)

    def show_license_info(self):
        """显示授权信息"""
        info = self.license_manager.show_license_info()
        messagebox.showinfo("软件授权信息", info)

    def reactivate_software(self):
        """重新激活软件"""
        from license_manager import LicenseDialog
        dialog = LicenseDialog(self.root)
        if dialog.show_activation_dialog():
            messagebox.showinfo("成功", "软件重新激活成功！")

    def show_about(self):
        """显示关于信息"""
        about_text = """
MIKE21 to Tecplot 转换器 v2.1 - Professional Edition

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 功能特性:
• 支持MIKE21 DFSU文件转换为Tecplot格式
• 支持全场数据和区域数据输出
• 支持线程池并行处理
• 支持自定义坐标变换
• 支持多区域投影分析
• 现代化GUI界面设计

⚙️ 技术规格:
• Python 3.12+ 
• 支持Windows 10/11
• 集成MIKE IO库
• 支持DXF几何文件

📄 版权信息:
• 基于开源项目开发
• 集成软件授权保护
• Powered by Liangyan

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()

        messagebox.showinfo("关于", about_text)

    def load_default_config(self):
        """加载默认配置"""
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except:
            return {
                'paths': {'input_dir': './dfsu_files', 'output_dir': './output'},
                'coordinate_transform': {'x_shift': 620000, 'y_shift': 3500000},
                'time_settings': {'time_index': 0},
                'regions': {},
                'output_settings': {'export_full_field': True, 'export_regions': True, 'precision': 6},
                'processing': {'parallel_workers': None, 'verbose': True}
            }

    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置根窗口的网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 配置主框架的列权重
        main_frame.columnconfigure(0, weight=1)

        # 设置主框架的行权重 - 关键修复
        main_frame.rowconfigure(0, weight=0)  # 标题区域 - 固定高度
        main_frame.rowconfigure(1, weight=1)  # 选项卡区域 - 可扩展
        main_frame.rowconfigure(2, weight=0)  # 控制按钮区域 - 固定高度
        main_frame.rowconfigure(3, weight=0)  # 进度条区域 - 固定高度
        main_frame.rowconfigure(4, weight=1)  # 日志区域 - 可扩展
        main_frame.rowconfigure(5, weight=0)  # 页脚区域 - 固定高度

        # 创建标题和水印区域
        self.create_header(main_frame)

        # 创建选项卡
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 10))

        # 基本设置选项卡
        self.create_basic_tab()

        # 高级设置选项卡
        self.create_advanced_tab()

        # 区域设置选项卡
        self.create_regions_tab()

        # 控制按钮
        self.create_control_buttons(main_frame)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', style='TProgressbar')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 10))

        # 日志输出区域
        self.create_log_area(main_frame)

        # 状态栏和水印
        self.create_footer(main_frame)

    def create_header(self, parent):
        """创建标题和水印区域"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)

        # 软件标题
        title_label = ttk.Label(header_frame,
                               text="🚀 MIKE21 to Tecplot 转换器",
                               font=('Microsoft YaHei UI', 16, 'bold'),
                               foreground='#4a9eff')
        title_label.grid(row=0, column=0, sticky=tk.W)

        # 版本信息
        version_label = ttk.Label(header_frame,
                                 text="v2.1 Professional Edition",
                                 font=('Microsoft YaHei UI', 10),
                                 foreground='#888888')
        version_label.grid(row=1, column=0, sticky=tk.W)

        # 水印 - Powered by Liangyan
        watermark_label = ttk.Label(header_frame,
                                   text="✨ Powered by Liangyan",
                                   font=('Microsoft YaHei UI', 10, 'italic'),
                                   foreground='#888888')
        watermark_label.grid(row=0, column=2, sticky=tk.E)

        # 状态指示器
        status_label = ttk.Label(header_frame,
                                text="🟢 Ready",
                                font=('Microsoft YaHei UI', 9),
                                foreground='#4ade80')
        status_label.grid(row=1, column=2, sticky=tk.E)

    def create_basic_tab(self):
        """创建基本设置选项卡"""
        basic_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(basic_frame, text="基本设置")

        # 输入目录
        ttk.Label(basic_frame, text="输入目录:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.input_dir_var = tk.StringVar(value=self.config.get('paths', {}).get('input_dir', './dfsu_files'))
        input_frame = ttk.Frame(basic_frame)
        input_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        basic_frame.columnconfigure(1, weight=1)

        ttk.Entry(input_frame, textvariable=self.input_dir_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="浏览", command=self.browse_input_dir).pack(side=tk.RIGHT, padx=(5, 0))

        # 输出目录
        ttk.Label(basic_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.output_dir_var = tk.StringVar(value=self.config.get('paths', {}).get('output_dir', './output'))
        output_frame = ttk.Frame(basic_frame)
        output_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="浏览", command=self.browse_output_dir).pack(side=tk.RIGHT, padx=(5, 0))

        # 坐标变换
        coord_frame = ttk.LabelFrame(basic_frame, text="坐标变换", padding="10")
        coord_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))

        ttk.Label(coord_frame, text="X偏移:").grid(row=0, column=0, sticky=tk.W)
        self.x_shift_var = tk.StringVar(value=str(self.config.get('coordinate_transform', {}).get('x_shift', 620000)))
        ttk.Entry(coord_frame, textvariable=self.x_shift_var, width=15).grid(row=0, column=1, padx=(5, 15))

        ttk.Label(coord_frame, text="Y偏移:").grid(row=0, column=2, sticky=tk.W)
        self.y_shift_var = tk.StringVar(value=str(self.config.get('coordinate_transform', {}).get('y_shift', 3500000)))
        ttk.Entry(coord_frame, textvariable=self.y_shift_var, width=15).grid(row=0, column=3, padx=(5, 0))

        # 输出选项
        output_frame = ttk.LabelFrame(basic_frame, text="输出选项", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

        self.export_full_field_var = tk.BooleanVar(value=self.config.get('output_settings', {}).get('export_full_field', True))
        ttk.Checkbutton(output_frame, text="输出全场数据", variable=self.export_full_field_var).grid(row=0, column=0, sticky=tk.W)

        self.export_regions_var = tk.BooleanVar(value=self.config.get('output_settings', {}).get('export_regions', True))
        ttk.Checkbutton(output_frame, text="输出区域数据", variable=self.export_regions_var).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))

    def create_advanced_tab(self):
        """创建高级设置选项卡"""
        advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_frame, text="高级设置")

        # 时间步设置
        time_frame = ttk.LabelFrame(advanced_frame, text="时间步设置", padding="10")
        time_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(time_frame, text="时间步索引:").grid(row=0, column=0, sticky=tk.W)
        self.time_index_var = tk.StringVar(value=str(self.config.get('time_settings', {}).get('time_index', 0)))
        ttk.Entry(time_frame, textvariable=self.time_index_var, width=10).grid(row=0, column=1, padx=(5, 0))
        ttk.Label(time_frame, text="(0=第一帧, -1=最后一帧, 留空=所有帧)", font=("TkDefaultFont", 8)).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))

        # 处理选项
        process_frame = ttk.LabelFrame(advanced_frame, text="处理选项", padding="10")
        process_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(process_frame, text="并行进程数:").grid(row=0, column=0, sticky=tk.W)
        self.parallel_workers_var = tk.StringVar(value=str(self.config.get('processing', {}).get('parallel_workers', '') or '自动'))
        ttk.Entry(process_frame, textvariable=self.parallel_workers_var, width=10).grid(row=0, column=1, padx=(5, 0))

        ttk.Label(process_frame, text="数值精度:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.precision_var = tk.StringVar(value=str(self.config.get('output_settings', {}).get('precision', 6)))
        ttk.Entry(process_frame, textvariable=self.precision_var, width=10).grid(row=1, column=1, padx=(5, 0), pady=(5, 0))

        self.verbose_var = tk.BooleanVar(value=self.config.get('processing', {}).get('verbose', True))
        ttk.Checkbutton(process_frame, text="详细输出", variable=self.verbose_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        # 配置文件操作
        config_frame = ttk.LabelFrame(advanced_frame, text="配置文件", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(config_frame, text="加载配置", command=self.load_config).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(config_frame, text="保存配置", command=self.save_config).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(config_frame, text="重置默认", command=self.reset_config).grid(row=0, column=2)

    def create_regions_tab(self):
        """创建区域设置选项卡"""
        regions_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(regions_frame, text="区域设置")

        # 区域列表
        list_frame = ttk.Frame(regions_frame)
        list_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        regions_frame.rowconfigure(0, weight=1)
        regions_frame.columnconfigure(1, weight=1)

        ttk.Label(list_frame, text="区域列表:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # 创建树形视图显示区域
        columns = ('name', 'region_dxf', 'axis_dxf', 'description')
        self.regions_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        # 设置列标题
        self.regions_tree.heading('name', text='区域名称')
        self.regions_tree.heading('region_dxf', text='区域DXF')
        self.regions_tree.heading('axis_dxf', text='轴线DXF')
        self.regions_tree.heading('description', text='描述')

        # 设置列宽
        self.regions_tree.column('name', width=100)
        self.regions_tree.column('region_dxf', width=150)
        self.regions_tree.column('axis_dxf', width=150)
        self.regions_tree.column('description', width=150)

        self.regions_tree.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(2, weight=1)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.regions_tree.yview)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S))
        self.regions_tree.configure(yscrollcommand=scrollbar.set)

        # 区域操作按钮
        button_frame = ttk.Frame(regions_frame)
        button_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Button(button_frame, text="添加区域", command=self.add_region).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="编辑区域", command=self.edit_region).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除区域", command=self.delete_region).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="刷新列表", command=self.refresh_regions).pack(side=tk.RIGHT)

    def create_control_buttons(self, parent):
        """创建控制按钮"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 5))
        button_frame.columnconfigure(2, weight=1)  # 让中间空间可扩展

        # 左侧按钮组
        left_buttons = ttk.Frame(button_frame)
        left_buttons.grid(row=0, column=0, sticky=tk.W)

        self.start_button = ttk.Button(left_buttons, text="🚀 开始转换", command=self.start_conversion)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(left_buttons, text="⏹️ 停止转换", command=self.stop_conversion,
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        # 右侧按钮组
        right_buttons = ttk.Frame(button_frame)
        right_buttons.grid(row=0, column=3, sticky=tk.E)

        ttk.Button(right_buttons, text="🗑️ 清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(right_buttons, text="📁 打开输出目录", command=self.open_output_dir).pack(side=tk.LEFT)

    def create_log_area(self, parent):
        """创建日志输出区域"""
        log_frame = ttk.LabelFrame(parent, text="📋 运行日志", padding="8")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 5))

        # 配置日志文本区域 - 修改为浅色主题
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            width=80,
            bg='#ffffff',              # 改为白色背景
            fg='#333333',              # 改为深色文字
            insertbackground='#333333', # 改为深色光标
            font=('楷体', 9),           # 改为楷体字体
            wrap=tk.WORD,
            relief='solid',
            borderwidth=1
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        # 设置日志处理器
        self.setup_logging()

    def setup_logging(self):
        """设置日志处理器"""
        # 创建自定义日志处理器
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget, queue_obj):
                super().__init__()
                self.text_widget = text_widget
                self.queue = queue_obj

            def emit(self, record):
                try:
                    msg = self.format(record)
                    # 确保消息是UTF-8编码的字符串
                    if isinstance(msg, bytes):
                        msg = msg.decode('utf-8', errors='ignore')
                    self.queue.put(('log', msg))
                except Exception:
                    # 如果编码失败，忽略这条日志消息
                    pass

        # 配置日志
        self.log_handler = GUILogHandler(self.log_text, self.message_queue)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # 获取根日志记录器并添加处理器
        logger = logging.getLogger()
        logger.addHandler(self.log_handler)
        logger.setLevel(logging.INFO)

    def browse_input_dir(self):
        """浏览输入目录"""
        directory = filedialog.askdirectory(title="选择DFSU文件目录", initialdir=self.input_dir_var.get())
        if directory:
            self.input_dir_var.set(directory)

    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录", initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)

    def update_display(self):
        """更新界面显示"""
        self.refresh_regions()

    def refresh_regions(self):
        """刷新区域列表"""
        # 清空现有项
        for item in self.regions_tree.get_children():
            self.regions_tree.delete(item)

        # 添加区域
        regions = self.config.get('regions', {})
        for name, config in regions.items():
            self.regions_tree.insert('', 'end', values=(
                name,
                config.get('region_dxf', ''),
                config.get('axis_dxf', ''),
                config.get('description', '')
            ))

    def add_region(self):
        """添加区域"""
        self.edit_region_dialog()

    def edit_region(self):
        """编辑区域"""
        selection = self.regions_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的区域")
            return

        item = self.regions_tree.item(selection[0])
        region_name = item['values'][0]
        self.edit_region_dialog(region_name)

    def delete_region(self):
        """删除区域"""
        selection = self.regions_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的区域")
            return

        item = self.regions_tree.item(selection[0])
        region_name = item['values'][0]

        if messagebox.askyesno("确认", f"确定要删除区域 '{region_name}' 吗？"):
            if region_name in self.config.get('regions', {}):
                del self.config['regions'][region_name]
                self.refresh_regions()

    def edit_region_dialog(self, region_name=None):
        """编辑区域对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑区域" if region_name else "添加区域")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 获取现有数据
        region_data = {}
        if region_name:
            region_data = self.config.get('regions', {}).get(region_name, {})

        # 区域名称
        ttk.Label(dialog, text="区域名称:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar(value=region_name or '')
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        # 区域DXF文件
        ttk.Label(dialog, text="区域DXF:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        region_dxf_var = tk.StringVar(value=region_data.get('region_dxf', ''))
        region_frame = ttk.Frame(dialog)
        region_frame.grid(row=1, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
        ttk.Entry(region_frame, textvariable=region_dxf_var, width=25).pack(side=tk.LEFT)
        ttk.Button(region_frame, text="...", width=3,
                  command=lambda: self.browse_dxf_file(region_dxf_var)).pack(side=tk.RIGHT)

        # 轴线DXF文件
        ttk.Label(dialog, text="轴线DXF:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        axis_dxf_var = tk.StringVar(value=region_data.get('axis_dxf', ''))
        axis_frame = ttk.Frame(dialog)
        axis_frame.grid(row=2, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
        ttk.Entry(axis_frame, textvariable=axis_dxf_var, width=25).pack(side=tk.LEFT)
        ttk.Button(axis_frame, text="...", width=3,
                  command=lambda: self.browse_dxf_file(axis_dxf_var)).pack(side=tk.RIGHT)

        # 描述
        ttk.Label(dialog, text="描述:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        desc_var = tk.StringVar(value=region_data.get('description', ''))
        ttk.Entry(dialog, textvariable=desc_var, width=30).grid(row=3, column=1, padx=10, pady=5)

        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        def save_region():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("错误", "区域名称不能为空")
                return

            if not region_name and name in self.config.get('regions', {}):
                messagebox.showerror("错误", "区域名称已存在")
                return

            # 保存区域数据
            if 'regions' not in self.config:
                self.config['regions'] = {}

            # 如果是重命名，删除旧名称
            if region_name and region_name != name and region_name in self.config['regions']:
                del self.config['regions'][region_name]

            self.config['regions'][name] = {
                'region_dxf': region_dxf_var.get().strip(),
                'axis_dxf': axis_dxf_var.get().strip(),
                'description': desc_var.get().strip()
            }

            self.refresh_regions()
            dialog.destroy()

        ttk.Button(button_frame, text="保存", command=save_region).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def browse_dxf_file(self, var):
        """浏览DXF文件"""
        filename = filedialog.askopenfilename(
            title="选择DXF文件",
            filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)

    def load_config(self):
        """加载配置文件"""
        filename = filedialog.askopenfilename(
            title="加载配置文件",
            filetypes=[("YAML files", "*.yaml"), ("YAML files", "*.yml"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
                self.update_display()
                messagebox.showinfo("成功", "配置文件加载成功")
            except Exception as e:
                messagebox.showerror("错误", f"加载配置文件失败: {e}")

    def save_config(self):
        """保存配置文件"""
        filename = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("YAML files", "*.yml"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.update_config_from_gui()
                with open(filename, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
                messagebox.showinfo("成功", "配置文件保存成功")
            except Exception as e:
                messagebox.showerror("错误", f"保存配置文件失败: {e}")

    def reset_config(self):
        """重置为默认配置"""
        if messagebox.askyesno("确认", "确定要重置为默认配置吗？"):
            self.config = self.load_default_config()
            self.update_display()

    def update_config_from_gui(self):
        """从界面更新配置"""
        # 确保配置结构完整
        if 'paths' not in self.config:
            self.config['paths'] = {}
        if 'coordinate_transform' not in self.config:
            self.config['coordinate_transform'] = {}
        if 'time_settings' not in self.config:
            self.config['time_settings'] = {}
        if 'output_settings' not in self.config:
            self.config['output_settings'] = {}
        if 'processing' not in self.config:
            self.config['processing'] = {}
        if 'regions' not in self.config:
            self.config['regions'] = {}

        # 更新路径
        self.config['paths']['input_dir'] = self.input_dir_var.get()
        self.config['paths']['output_dir'] = self.output_dir_var.get()

        # 更新坐标变换
        try:
            self.config['coordinate_transform']['x_shift'] = float(self.x_shift_var.get())
            self.config['coordinate_transform']['y_shift'] = float(self.y_shift_var.get())
        except ValueError:
            pass

        # 更新时间设置
        try:
            time_val = self.time_index_var.get().strip()
            if time_val == '' or time_val.lower() in ['null', 'none']:
                self.config['time_settings']['time_index'] = None
            else:
                self.config['time_settings']['time_index'] = int(time_val)
        except ValueError:
            pass

        # 更新输出设置
        self.config['output_settings']['export_full_field'] = self.export_full_field_var.get()
        self.config['output_settings']['export_regions'] = self.export_regions_var.get()

        try:
            self.config['output_settings']['precision'] = int(self.precision_var.get())
        except ValueError:
            pass

        # 更新处理选项
        try:
            workers_val = self.parallel_workers_var.get().strip()
            if workers_val == '自动' or workers_val == '':
                self.config['processing']['parallel_workers'] = None
            else:
                self.config['processing']['parallel_workers'] = int(workers_val)
        except ValueError:
            pass

        self.config['processing']['verbose'] = self.verbose_var.get()

    def start_conversion(self):
        """开始转换"""
        if self.processing:
            return

        # 检查输入目录
        input_dir = Path(self.input_dir_var.get())
        if not input_dir.exists():
            messagebox.showerror("错误", "输入目录不存在")
            return

        # 检查是否有DFSU文件
        dfsu_files = list(input_dir.glob("*.dfsu"))
        if not dfsu_files:
            messagebox.showerror("错误", "输入目录中没有找到DFSU文件")
            return

        # 更新配置
        self.update_config_from_gui()

        # 启动转换线程
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()

        # 清空日志
        self.log_text.delete(1.0, tk.END)

        # 在新线程中运行转换
        self.conversion_thread = threading.Thread(target=self.run_conversion, daemon=True)
        self.conversion_thread.start()

    def run_conversion(self):
        """在后台线程中运行转换"""
        try:
            # 创建临时配置文件
            temp_config_path = Path("temp_gui_config.yaml")
            with open(temp_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

            # 创建转换器
            converter = MIKE21Converter(str(temp_config_path))

            # 运行转换
            result = converter.run()

            # 发送结果消息
            self.message_queue.put(('result', result))

            # 清理临时文件
            if temp_config_path.exists():
                temp_config_path.unlink()

        except Exception as e:
            self.message_queue.put(('error', str(e)))
        finally:
            self.message_queue.put(('finished', None))

    def stop_conversion(self):
        """停止转换"""
        # 注意：实际停止需要更复杂的实现
        messagebox.showinfo("提示", "转换正在停止中，请等待当前文件处理完成...")
        self.processing = False

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def open_output_dir(self):
        """打开输出目录"""
        import os
        import subprocess
        output_dir = self.output_dir_var.get()
        if Path(output_dir).exists():
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", output_dir])
            else:
                subprocess.run(["xdg-open", output_dir])
        else:
            messagebox.showwarning("警告", "输出目录不存在")

    def process_queue(self):
        """处理消息队列"""
        try:
            while True:
                msg_type, msg_data = self.message_queue.get_nowait()

                if msg_type == 'log':
                    self.log_text.insert(tk.END, msg_data + '\n')
                    self.log_text.see(tk.END)

                elif msg_type == 'result':
                    if msg_data['success']:
                        messagebox.showinfo("成功",
                            f"转换完成！\n成功处理 {msg_data['successful_files']}/{msg_data['total_files']} 个文件")
                    else:
                        messagebox.showerror("失败", f"转换失败：{msg_data.get('message', '未知错误')}")

                elif msg_type == 'error':
                    messagebox.showerror("错误", f"转换过程中发生错误：{msg_data}")

                elif msg_type == 'finished':
                    self.processing = False
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.progress.stop()

        except queue.Empty:
            pass

        # 继续检查队列
        self.root.after(100, self.process_queue)

    def create_footer(self, parent):
        """创建页脚状态栏"""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        footer_frame.columnconfigure(1, weight=1)

        # 左侧水印
        left_watermark = ttk.Label(footer_frame,
                                  text="© 2024 Powered by Liangyan | Professional Data Conversion Tool",
                                  font=('Microsoft YaHei UI', 8),
                                  foreground='#666666')
        left_watermark.grid(row=0, column=0, sticky=tk.W)

        # 右侧技术信息
        tech_info = ttk.Label(footer_frame,
                             text="Python 3.12+ | MIKE IO | Tecplot",
                             font=('Microsoft YaHei UI', 8),
                             foreground='#666666')
        tech_info.grid(row=0, column=2, sticky=tk.E)

def main():
    """主函数 - 带授权验证"""
    # 在启动GUI之前先检查软件授权
    print("MIKE21转换器 v2.1 - 启动中...")

    if not check_license_and_activate():
        print("程序因授权验证失败而退出")
        return

    # 授权验证通过，启动GUI
    root = tk.Tk()

    # 设置应用程序图标
    try:
        if Path("app_icon.ico").exists():
            root.iconbitmap("app_icon.ico")
    except Exception as e:
        print(f"加载图标失败: {e}")

    app = ConverterGUI(root)

    # 居中窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()
