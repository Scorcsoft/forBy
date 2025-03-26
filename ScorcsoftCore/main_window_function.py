import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout
from ScorcsoftUI.main_window import Ui_MainWindow
from ScorcsoftCore.about_function import AboutPage
from ScorcsoftCore.ds_store_analyze_function import DSStoreAnalyze
from ScorcsoftCore.git_directory_analyze_function import GitDirectoryAnalyze
from ScorcsoftCore.svn_directory_analyze_function import SVNDirectoryAnalyze


class monkeyStringApp(QMainWindow, Ui_MainWindow):
    def __init__(self, BASE_DIR):
        super().__init__()
        self.setupUi(self)

        layout = QVBoxLayout(self.centralwidget)
        layout.addWidget(self.Main_Window_Left_Menu_QListWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setStretch(0, 1)  # 让 QListWidget 充满整个布局
        self.centralwidget.setLayout(layout)
        self.BASE_DIR = BASE_DIR

        self.set_menu_icons()

        # 模块注册开始
        self.about_page = AboutPage()
        self.Function_Main_Area.addWidget(self.about_page)

        self.ds_store_analyze = DSStoreAnalyze()
        self.Function_Main_Area.addWidget(self.ds_store_analyze)

        self.git_directory_analyze = GitDirectoryAnalyze()
        self.Function_Main_Area.addWidget(self.git_directory_analyze)

        self.svn_directory_analyze = SVNDirectoryAnalyze()
        self.Function_Main_Area.addWidget(self.svn_directory_analyze)

        self.page_map = {
            ".DS_Store 解析": self.ds_store_analyze,
            ".git 目录解析": self.git_directory_analyze,
            '.svn 目录解析': self.svn_directory_analyze,
            "关于": self.about_page,
        }
        # 模块注册结束

        self.Main_Window_Left_Menu_QListWidget.currentRowChanged.connect(self.switch_page)

    def switch_page(self, index):
        item = self.Main_Window_Left_Menu_QListWidget.item(index)
        if item:
            page = self.page_map.get(item.text())
            if page:
                self.Function_Main_Area.setCurrentWidget(page)

    def set_menu_icons(self):
        icons = {
            "关于": os.path.join(self.BASE_DIR, "ScorcsoftAssets", "about.png"),
            ".DS_Store 解析": os.path.join(self.BASE_DIR, "ScorcsoftAssets", "ds_store_parse.png"),
            '.git 目录解析': os.path.join(self.BASE_DIR,"ScorcsoftAssets", "git_parse.png"),
            ".svn 目录解析": os.path.join(self.BASE_DIR,"ScorcsoftAssets", "svn_parse.png")
        }
        for index in range(self.Main_Window_Left_Menu_QListWidget.count()):
            item = self.Main_Window_Left_Menu_QListWidget.item(index)
            text = item.text()
            if text in icons:
                item.setIcon(QIcon(icons[text]))

    def resizeEvent(self, event):
        self.Main_Window_Left_Menu_QListWidget.setMinimumHeight(self.height())
        super().resizeEvent(event)

