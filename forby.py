import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont, QIcon
from ScorcsoftCore.main_window_function import monkeyStringApp


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # font_id = QFontDatabase.addApplicationFont(os.path.abspath("ScorcsoftAssets/YaHei_Consolas_Hybrid.ttf"))
    # if font_id != -1:
    #     font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    # else:
    #     font_family = "Arial"
    if not os.path.isdir("ScorcsoftTemp"):
        os.mkdir("ScorcsoftTemp")

    font_family = "Arial"
    app.setWindowIcon(QIcon(os.path.abspath("ScorcsoftAssets/about.png")))
    app.setFont(QFont(font_family))

    if getattr(sys, 'frozen', False):
        BASE_DIR = sys._MEIPASS  # PyInstaller 运行时目录
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 正常运行时目录
    window = monkeyStringApp(BASE_DIR=BASE_DIR)
    window.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Good Bye.")
