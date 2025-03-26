from PyQt5.QtWidgets import QWidget
from ScorcsoftUI.page_git_directory_analyze import Ui_git_directory_analyze


class GitDirectoryAnalyze(QWidget, Ui_git_directory_analyze):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
