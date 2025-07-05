"""
MIKE21转换器 - 软件授权验证系统
提供注册码验证和授权管理功能
"""

import hashlib
import json
import os
import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import tkinter as tk
from tkinter import messagebox, simpledialog
import base64


class LicenseManager:
    """软件授权管理器"""

    def __init__(self):
        self.license_file = Path("license.dat")
        self.machine_id = self._get_machine_id()
        self.product_key = "MIKE21-TECPLOT-CONVERTER-2025"

    def _get_machine_id(self) -> str:
        """获取机器唯一标识"""
        import platform
        import getpass

        # 结合多个系统信息生成唯一ID
        machine_info = f"{platform.node()}-{platform.machine()}-{getpass.getuser()}"
        return hashlib.md5(machine_info.encode()).hexdigest()[:16]

    def _generate_activation_code(self, registration_code: str) -> str:
        """生成激活码"""
        # 结合注册码、机器ID和产品密钥生成激活码
        combined = f"{registration_code}-{self.machine_id}-{self.product_key}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def _validate_registration_code(self, reg_code: str) -> bool:
        """验证注册码格式和有效性"""
        # 注册码格式: MIKE21-XXXXX-XXXXX-XXXXX
        if not reg_code or len(reg_code) != 24:  # 修正长度：MIKE21(6) + 3个-(3) + 3个5位段(15) = 24
            return False

        parts = reg_code.split('-')
        if len(parts) != 4 or parts[0] != "MIKE21":
            return False

        # 验证每个部分都是5位字母数字
        for part in parts[1:]:
            if len(part) != 5 or not part.isalnum():
                return False

        return True

    def _create_license_data(self, reg_code: str) -> Dict:
        """创建授权数据"""
        activation_code = self._generate_activation_code(reg_code)

        license_data = {
            "registration_code": reg_code,
            "machine_id": self.machine_id,
            "activation_code": activation_code,
            "activation_date": datetime.datetime.now().isoformat(),
            "product_version": "2.1",
            "license_type": "Standard",
            "expires": None,  # 永久授权
            "authorized": True
        }

        return license_data

    def _save_license(self, license_data: Dict) -> bool:
        """保存授权信息到文件"""
        try:
            # 编码并保存授权数据
            json_str = json.dumps(license_data)
            encoded = base64.b64encode(json_str.encode()).decode()

            with open(self.license_file, 'w') as f:
                f.write(encoded)

            return True
        except Exception as e:
            print(f"保存授权文件失败: {e}")
            return False

    def _load_license(self) -> Optional[Dict]:
        """加载授权信息"""
        if not self.license_file.exists():
            return None

        try:
            with open(self.license_file, 'r') as f:
                encoded = f.read()

            json_str = base64.b64decode(encoded.encode()).decode()
            license_data = json.loads(json_str)

            return license_data
        except Exception as e:
            print(f"读取授权文件失败: {e}")
            return None

    def is_licensed(self) -> Tuple[bool, str]:
        """检查软件是否已授权"""
        license_data = self._load_license()

        if not license_data:
            return False, "未找到授权信息，请输入注册码激活软件"

        # 验证机器ID
        if license_data.get("machine_id") != self.machine_id:
            return False, "授权文件与当前机器不匹配"

        # 验证激活码
        reg_code = license_data.get("registration_code", "")
        expected_activation = self._generate_activation_code(reg_code)

        if license_data.get("activation_code") != expected_activation:
            return False, "授权文件已损坏或无效"

        # 检查是否已授权
        if not license_data.get("authorized", False):
            return False, "软件未授权"

        # 检查过期时间（如果设置了）
        expires = license_data.get("expires")
        if expires:
            expire_date = datetime.datetime.fromisoformat(expires)
            if datetime.datetime.now() > expire_date:
                return False, "软件授权已过期"

        return True, "软件已正确授权"

    def activate_software(self, registration_code: str) -> Tuple[bool, str]:
        """激活软件"""
        # 验证注册码格式
        if not self._validate_registration_code(registration_code):
            return False, "注册码格式错误，正确格式: MIKE21-XXXXX-XXXXX-XXXXX"

        # 这里可以添加在线验证逻辑
        # 目前使用离线验证
        valid_codes = [
            "MIKE21-ABC12-DEF34-GHI56",
            "MIKE21-XYZ98-UVW76-RST54",
            "MIKE21-DEMO1-DEMO2-DEMO3",
            "MIKE21-TRIAL-VER01-2025A",
            "MIKE21-ADMIN-SUPER-USER1"
        ]

        if registration_code not in valid_codes:
            return False, "无效的注册码，请联系软件提供商获取正确的注册码"

        # 创建授权数据
        license_data = self._create_license_data(registration_code)

        # 保存授权文件
        if self._save_license(license_data):
            return True, f"软件激活成功！授权给机器: {self.machine_id[:8]}..."
        else:
            return False, "授权文件保存失败"

    def show_license_info(self) -> str:
        """显示授权信息"""
        license_data = self._load_license()

        if not license_data:
            return "未找到授权信息"

        info = f"""
软件授权信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
注册码: {license_data.get('registration_code', 'N/A')}
机器ID: {license_data.get('machine_id', 'N/A')[:8]}...
激活日期: {license_data.get('activation_date', 'N/A')[:10]}
产品版本: {license_data.get('product_version', 'N/A')}
授权类型: {license_data.get('license_type', 'N/A')}
过期时间: {'永久' if not license_data.get('expires') else license_data.get('expires')[:10]}
授权状态: {'✅ 已授权' if license_data.get('authorized') else '❌ 未授权'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip()

        return info


class LicenseDialog:
    """授权对话框"""

    def __init__(self, parent=None):
        self.parent = parent
        self.license_manager = LicenseManager()
        self.result = False

    def show_activation_dialog(self) -> bool:
        """显示激活对话框"""
        root = tk.Tk() if not self.parent else tk.Toplevel(self.parent)
        root.title("MIKE21转换器 - 软件激活")
        root.geometry("600x500")  # 增大窗口尺寸
        root.resizable(False, False)

        # 设置图标
        try:
            if Path("app_icon.ico").exists():
                root.iconbitmap("app_icon.ico")
        except:
            pass

        # 居中显示 - 修复transient循环引用问题
        if self.parent:
            root.transient(self.parent)
            root.grab_set()
        else:
            # 没有父窗口时，只居中显示，不设置transient
            root.update_idletasks()
            width = 650  # 增加窗口宽度
            height = 580  # 增加窗口高度
            x = (root.winfo_screenwidth() // 2) - (width // 2)
            y = (root.winfo_screenheight() // 2) - (height // 2)
            root.geometry(f"{width}x{height}+{x}+{y}")
            root.grab_set()

        # 主框架 - 增加更多边距
        main_frame = tk.Frame(root, padx=30, pady=20)  # 减少垂直边距
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(main_frame,
                              text="MIKE21转换器",
                              font=("Arial", 18, "bold"),
                              fg="#1E90FF")
        title_label.pack(pady=(0, 10))  # 减少间距

        # 副标题
        subtitle_label = tk.Label(main_frame,
                                 text="需要激活才能使用",
                                 font=("Arial", 12))
        subtitle_label.pack(pady=(0, 15))  # 减少间距

        # 说明文字
        info_text = """请输入您的注册码以激活软件

注册码格式: MIKE21-XXXXX-XXXXX-XXXXX

可用的测试注册码:
• MIKE21-ABC12-DEF34-GHI56
• MIKE21-DEMO1-DEMO2-DEMO3
• MIKE21-TRIAL-VER01-2025A

如需获取正式注册码，请联系软件提供商"""

        info_label = tk.Label(main_frame,
                             text=info_text,
                             justify=tk.LEFT,
                             font=("Arial", 10),
                             wraplength=550)  # 增加文字换行宽度
        info_label.pack(pady=(0, 20))  # 减少间距

        # 注册码输入框架
        reg_frame = tk.Frame(main_frame)
        reg_frame.pack(fill=tk.X, pady=(0, 20))  # 减少间距

        tk.Label(reg_frame, text="注册码:", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))
        reg_entry = tk.Entry(reg_frame, font=("Consolas", 12), width=40, relief=tk.GROOVE, bd=2)
        reg_entry.pack(fill=tk.X, pady=(0, 5), ipady=8)
        reg_entry.focus()

        # 结果显示
        result_label = tk.Label(main_frame, text="", wraplength=550, font=("Arial", 10))
        result_label.pack(pady=(0, 20))  # 减少间距

        # 按钮框架 - 改善布局
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))  # 增加顶部边距

        def activate():
            reg_code = reg_entry.get().strip().upper()
            if not reg_code:
                result_label.config(text="请输入注册码", fg="red")
                return

            success, message = self.license_manager.activate_software(reg_code)

            if success:
                result_label.config(text=message, fg="green")
                self.result = True
                root.after(2000, root.destroy)  # 2秒后自动关闭
            else:
                result_label.config(text=message, fg="red")

        def cancel():
            self.result = False
            root.destroy()

        # 激活按钮 - 改善布局
        activate_btn = tk.Button(button_frame,
                               text="激活软件",
                               command=activate,
                               bg="#4CAF50",
                               fg="white",
                               font=("Arial", 12, "bold"),
                               padx=25,
                               pady=10,
                               width=12)  # 设置固定宽度
        activate_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # 取消按钮 - 改善布局
        cancel_btn = tk.Button(button_frame,
                             text="取消",
                             command=cancel,
                             font=("Arial", 12),
                             padx=25,
                             pady=10,
                             width=12)  # 设置固定宽度
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # 回车键激活
        reg_entry.bind('<Return>', lambda e: activate())

        # 运行对话框
        if not self.parent:
            root.mainloop()
        else:
            root.wait_window()

        return self.result


def check_license_and_activate() -> bool:
    """检查授权并在需要时显示激活对话框"""
    license_manager = LicenseManager()

    # 检查是否已授权
    is_licensed, message = license_manager.is_licensed()

    if is_licensed:
        print(f"✅ {message}")
        return True

    print(f"⚠️ {message}")

    # 显示激活对话框
    dialog = LicenseDialog()
    activated = dialog.show_activation_dialog()

    if activated:
        print("🎉 软件激活成功！")
        return True
    else:
        print("❌ 软件未激活，程序将退出")
        return False


# 测试函数
if __name__ == "__main__":
    print("MIKE21转换器 - 授权系统测试")
    print("=" * 50)

    # 测试授权检查
    if check_license_and_activate():
        print("✅ 授权验证通过，可以使用软件")

        # 显示授权信息
        license_manager = LicenseManager()
        print(license_manager.show_license_info())
    else:
        print("❌ 授权验证失败")
