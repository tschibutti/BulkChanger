import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QGridLayout
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from gui.bulk import Bulk
from gui.info import Info

class Start(QWidget):
    def __init__(self):
        super(Start, self).__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(300, 300)
        self.setWindowTitle('Startscreen')

        # Layout
        grid = QGridLayout()
        self.setLayout(grid)

        # Buttons
        btn_s_bulk = QPushButton('Start Bulk Changer', self)
        btn_s_bulk.clicked.connect(self.startBulk)
        btn_s_bulk.setFixedSize(250, 75)
        grid.addWidget(btn_s_bulk)

        btn_s_info = QPushButton('Start Info Collector', self)
        btn_s_info.clicked.connect(self.startInfo)
        btn_s_info.setFixedSize(250, 75)
        grid.addWidget(btn_s_info)

        btn_quit = QPushButton('Quit', self)
        btn_quit.clicked.connect(self.close)
        btn_quit.setFixedSize(250, 75)
        grid.addWidget(btn_quit)

    def startBulk(self):
        self.bulk = Bulk()
        self.bulk.show()

    def startInfo(self):
        self.info = Info()
        self.info.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    start = Start()
    start.show()
    sys.exit(app.exec_())
