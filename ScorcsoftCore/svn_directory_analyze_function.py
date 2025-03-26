from PyQt5.QtWidgets import QWidget
from ScorcsoftUI.page_svn_directory_analyze import Ui_svn_directory_analyze


class SVNDirectoryAnalyze(QWidget, Ui_svn_directory_analyze):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
