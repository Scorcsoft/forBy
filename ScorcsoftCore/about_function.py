import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from ScorcsoftUI.page_about_widget import Ui_page_about


class AboutPage(QWidget, Ui_page_about):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        i = """
monkeyForBy(吗喽解析器)是一个吗喽🐒使用Python + PyQt5为BBY开发的解析工具，拥有以下功能模块帮助各位大师傅在渗透时快速处理以下信息泄露：

1. .DS_Store（.DS_Store文件泄露利用工具，递归解析.DS_Store 文件内容，还原网站目录结构）
2. .git (还没做)
3. .svn (还没做)


如果有bug或功能建议，你可以扫描上方二维码或者在 Github 中提交 Issue，被采纳建议的提供者将加入牛马名单成为牛马。
        """
        self.label_software_name.setText("吗喽解析工具")
        self.label_version.setText("Version 1.0.1")
        self.label_Introduction.setText(i)
        self.label_company_name.setText("Scorcsoft | 天蝎软件")
        self.label_copyright.setText("Copyright © 2021-2025 Scorcsoft. All rights reserved.")

        self.label_qr_code.setPixmap(QPixmap(os.path.abspath("ScorcsoftAssets/contact.jpg")))
        self.label_qr_code.setScaledContents(True)  # 确保图片适应 QLabel

