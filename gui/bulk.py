import subprocess
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout


class Bulk(QWidget):
    def __init__(self):
        super(Bulk, self).__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(800, 500)
        self.setWindowTitle('BulkChanger by Florian Gemperle')

        # Layout
        grid = QGridLayout()
        self.setLayout(grid)

        # Buttons
        btn_config = QPushButton('Show Config', self)
        btn_config.clicked.connect(self.showConfig)
        btn_config.resize(btn_config.sizeHint())
        grid.addWidget(btn_config, 0, 0)

        btn_b_log = QPushButton('Show BulkChanger Log', self)
        btn_b_log.clicked.connect(self.showBulkLog)
        btn_b_log.resize(btn_b_log.sizeHint())
        grid.addWidget(btn_b_log, 0, 1)

        btn_quit = QPushButton('Quit', self)
        btn_quit.clicked.connect(self.close)
        btn_quit.resize(btn_quit.sizeHint())
        grid.addWidget(btn_quit, 0, 2)

    def showConfig(self):
        program = 'C:/Program Files (x86)/Notepad++/notepad++.exe'
        file = 'C:/BulkChanger/config.ini'
        subprocess.Popen([program, file])

    def showBulkLog(self):
        program = 'C:/Program Files (x86)/Notepad++/notepad++.exe'
        file = 'C:/BulkChanger/bulkchanger.log'
        subprocess.Popen([program, file])
