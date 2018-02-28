import subprocess
import os
import sys
from info_collector import InfoCollector
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGridLayout, QTextEdit, QLineEdit, QInputDialog, QScrollBar
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import QSize

class Info(QWidget):

    def __init__(self):
        super(Info, self).__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(800, 500)
        self.setWindowTitle('InfoCollector')
        if getattr(sys, 'frozen', False):
            app_icon_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'icon.png')
        else:
            app_icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'icon.png')
        app_icon = QIcon()
        app_icon.addFile(app_icon_path, QSize(256, 256))
        self.setWindowIcon(app_icon)

        if getattr(sys, 'frozen', False):
            self.info_log_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'infocollector.log')
        else:
            self.info_log_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'infocollector.log')
        if not os.path.isfile(self.info_log_path):
            temp_file = open(self.info_log_path, 'w+')
            temp_file.close()

        if getattr(sys, 'frozen', False):
            self.config_file_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'config.ini')
        else:
            self.config_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'config.ini')
        if not os.path.isfile(self.config_file_path):
            temp_file = open(self.config_file_path, 'w+')
            temp_file.close()

        # Buttons
        self.btn_start = QPushButton('Start Run', self)
        self.btn_start.clicked.connect(self.start_run)
        self.btn_start.resize(self.btn_start.sizeHint())
        self.btn_start.setAutoDefault(True)

        btn_config = QPushButton('Show Config', self)
        btn_config.clicked.connect(self.show_config)
        btn_config.resize(btn_config.sizeHint())

        btn_b_log = QPushButton('Show InfoCollector Log', self)
        btn_b_log.clicked.connect(self.show_infolog)
        btn_b_log.resize(btn_b_log.sizeHint())

        btn_quit = QPushButton('Quit', self)
        btn_quit.clicked.connect(self.quit_gui)
        btn_quit.resize(btn_quit.sizeHint())

        self.btn_abort = QPushButton('Abort Run', self)
        self.btn_abort.clicked.connect(self.abort_run)
        self.btn_abort.resize(self.btn_abort.sizeHint())
        self.btn_abort.setEnabled(False)

        # Text Area
        self.output_area = QTextEdit(self)
        self.output_area.setFixedSize(750, 375)
        self.output_area.setReadOnly(True)

        # Status
        self.txt_total = QLabel('Total: 0', self)
        self.txt_success = QLabel('Success: 0', self)
        self.txt_failed = QLabel('Failed: 0', self)
        self.txt_duplicates = QLabel('Duplicates: 0', self)

        self.txt_total.setStyleSheet('color: black; font-size: 14px; font: bold')
        self.txt_success.setStyleSheet('color: green; font-size: 14px; font: bold')
        self.txt_failed.setStyleSheet('color: red; font-size: 14px; font: bold')
        self.txt_duplicates.setStyleSheet('color: blue; font-size: 14px; font: bold')

        # Layout
        grid = QGridLayout(self)
        grid_status = QGridLayout()
        grid_output = QGridLayout()
        grid_buttons = QGridLayout()

        grid.addLayout(grid_status, 0, 0)
        grid.addLayout(grid_output, 1, 0)
        grid.addLayout(grid_buttons, 2, 0)

        grid_status.addWidget(self.btn_start, 0, 0)
        grid_status.addWidget(self.txt_total, 0, 1)
        grid_status.addWidget(self.txt_success, 0, 2)
        grid_status.addWidget(self.txt_failed, 0, 3)
        grid_status.addWidget(self.txt_duplicates, 0, 4)

        grid_output.addWidget(self.output_area, 0, 0)

        grid_buttons.addWidget(btn_config, 3, 0)
        grid_buttons.addWidget(btn_b_log, 3, 1)
        grid_buttons.addWidget(self.btn_abort, 3, 2)
        grid_buttons.addWidget(btn_quit, 3, 3)
        self.setLayout(grid)

    def show_config(self):
        program = 'C:/Program Files (x86)/Notepad++/notepad++.exe'
        subprocess.Popen([program, self.config_file_path])

    def show_infolog(self):
        program = 'C:/Program Files (x86)/Notepad++/notepad++.exe'
        subprocess.Popen([program, self.info_log_path])

    def start_run(self):
        text, result = QInputDialog.getText(self, 'Credentials', 'FortiGate User', QLineEdit.Normal)
        if result:
            self.firewall_user = str(text)
            text, result = QInputDialog.getText(self, 'Credentials', 'FortiGate Password', QLineEdit.Password)
            if result:
                self.firewall_password = str(text)
                text, result = QInputDialog.getText(self, 'Credentials', 'SSL VPN User', QLineEdit.Normal,
                                                    self.firewall_user)
                if result:
                    self.sslvpn_user = str(text)
                    text, result = QInputDialog.getText(self, 'Credentials', 'SSL VPN Password', QLineEdit.Password,
                                                        self.firewall_password)
                    if result:
                        self.sslvpn_password = str(text)
                        self.btn_start.setEnabled(False)
                        self.btn_abort.setEnabled(True)
                        self.output_append('black', 'START RUN')
                        self.collector = InfoCollector(self.output_append, self.update_status, self.end_run,
                                                       self.exception_occured, self.firewall_user,
                                                       self.firewall_password, self.sslvpn_user,
                                                       self.sslvpn_password)
                        self.collector.start()

    def end_run(self):
        self.btn_start.setEnabled(True)
        self.btn_start.setFocus()
        self.btn_abort.setEnabled(False)
        self.output_append('black', 'RUN FINISHED')
        self.output_append('black', '---------------------------------------------------------------------------')

    def abort_run(self):
        self.btn_start.setEnabled(True)
        self.btn_start.setFocus()
        self.btn_abort.setEnabled(False)
        self.collector.stop()
        self.output_append('black', 'RUN ABORTED, please wait...')

    def update_status(self, total, success, failed, duplicates):
        self.txt_total.setText('Total: ' + str(total))
        self.txt_success.setText('Success: ' + str(success))
        self.txt_failed.setText('Failed: ' + str(failed))
        self.txt_duplicates.setText('Duplicates: ' + str(duplicates))

    def quit_gui(self):
        self.update_status(0, 0, 0, 0)
        self.output_area.clear()
        self.close()

    def exception_occured(self, reason):
        text = 'ERROR WITH ' + reason.upper()
        self.output_append('black', text)
        self.btn_start.setEnabled(True)
        self.btn_abort.setEnabled(False)

    def output_append(self, color, text):
        if color.upper() == 'RED':
            self.output_area.setTextColor(QColor(255, 0, 0))
        elif color.upper() == 'GREEN':
            self.output_area.setTextColor(QColor(0, 128, 0))
        elif color.upper() == 'BLUE':
            self.output_area.setTextColor(QColor(0, 0, 250))
        else:
            self.output_area.setTextColor(QColor(0, 0, 0))
        self.output_area.append(text)
        self.output_area.ensureCursorVisible()



