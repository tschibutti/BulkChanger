import sys
import os
import webbrowser
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QGridLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize
from gui.bulk import Bulk
from gui.info import Info

class Start(QWidget):
    def __init__(self):
        super(Start, self).__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(300, 300)
        self.setWindowTitle('Startscreen')
        if getattr(sys, 'frozen', False):
            app_icon_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'icon.png')
            ffn_icon_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'ffn.png')
        else:
            app_icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'icon.png')
            ffn_icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ffn.png')
        app_icon = QIcon()
        app_icon.addFile(app_icon_path, QSize(256, 256))
        self.setWindowIcon(app_icon)

        # Layout
        grid = QGridLayout()
        self.setLayout(grid)

        # Buttons
        btn_s_bulk = QPushButton('Start Bulk Changer', self)
        btn_s_bulk.clicked.connect(self.startBulk)
        btn_s_bulk.setFixedSize(250, 60)
        btn_s_bulk.setAutoDefault(True)
        grid.addWidget(btn_s_bulk)

        btn_s_info = QPushButton('Start Info Collector', self)
        btn_s_info.clicked.connect(self.startInfo)
        btn_s_info.setFixedSize(250, 60)
        grid.addWidget(btn_s_info)

        btn_quit = QPushButton('Quit', self)
        btn_quit.clicked.connect(self.close)
        btn_quit.setFixedSize(250, 60)
        grid.addWidget(btn_quit)

        btn_ffn = QPushButton(self)
        ffn_icon = QIcon()
        ffn_icon.addPixmap(QPixmap(ffn_icon_path))
        btn_ffn.setIcon(ffn_icon)
        btn_ffn.setIconSize(QSize(133, 40))
        btn_ffn.clicked.connect(self.openWebsite)
        btn_ffn.setFixedSize(250, 60)
        grid.addWidget(btn_ffn)

    def startBulk(self):
        bulk.show()

    def startInfo(self):
        info.show()

    def openWebsite(self):
        webbrowser.open('https://www.firstframe.net')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    start = Start()
    info = Info()
    bulk = Bulk()
    start.show()
    sys.exit(app.exec_())
