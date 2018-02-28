import subprocess
import os
import sys
from bulk_changer import BulkChanger
from bulk_verify import BulkVerify
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGridLayout, QTextEdit, QDialog, QLineEdit, QInputDialog, QCheckBox, QMessageBox, qApp
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import QSize, QEvent, Qt

class Bulk(QWidget):

    def __init__(self, parent=None):
        super(Bulk, self).__init__(parent)
        qApp.installEventFilter(self)
        self.initUI()

    def initUI(self):
        self.setFixedSize(800, 500)
        self.setWindowTitle('BulkChanger')
        if getattr(sys, 'frozen', False):
            app_icon_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'icon.png')
        else:
            app_icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'icon.png')
        app_icon = QIcon()
        app_icon.addFile(app_icon_path, QSize(256, 256))
        self.setWindowIcon(app_icon)

        if getattr(sys, 'frozen', False):
            self.bulk_log_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'bulkchanger.log')
        else:
            self.bulk_log_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'bulkchanger.log')
        if not os.path.isfile(self.bulk_log_path):
            temp_file = open(self.bulk_log_path, 'w+')
            temp_file.close()

        if getattr(sys, 'frozen', False):
            self.config_file_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'config.ini')
        else:
            self.config_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'config.ini')
        if not os.path.isfile(self.config_file_path):
            temp_file = open(self.config_file_path, 'w+')
            temp_file.close()

        if getattr(sys, 'frozen', False):
            self.input_file_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'input.txt')
        else:
            self.input_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'input', 'input.txt')
        if not os.path.isfile(self.input_file_path):
            temp_file = open(self.input_file_path, 'w+')
            temp_file.close()

        # Variables
        self.firewall_user = ''
        self.firewall_password = ''
        self.sslvpn_user = ''
        self.sslvpn_password = ''
        self.ipaddress = '192.168.8.2'
        self.port = '8443'

        # Dialog
        self.start_dialog = QDialog()
        self.start_dialog.setWindowIcon(app_icon)
        self.load_start_dialog()

        # Buttons
        self.btn_start = QPushButton('Start Run', self)
        self.btn_start.clicked.connect(self.start_run)
        self.btn_start.resize(self.btn_start.sizeHint())
        self.btn_start.setAutoDefault(True)

        btn_config = QPushButton('Show Config', self)
        btn_config.clicked.connect(self.show_config)
        btn_config.resize(btn_config.sizeHint())

        btn_input = QPushButton('Show Input', self)
        btn_input.clicked.connect(self.show_input)
        btn_input.resize(btn_input.sizeHint())

        btn_b_log = QPushButton('Show BulkChanger Log', self)
        btn_b_log.clicked.connect(self.show_bulklog)
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
        self.txt_skipped = QLabel('Skipped: 0', self)
        self.txt_duplicates = QLabel('Duplicates: 0', self)

        self.txt_total.setStyleSheet('color: black; font-size: 14px; font: bold')
        self.txt_success.setStyleSheet('color: green; font-size: 14px; font: bold')
        self.txt_failed.setStyleSheet('color: red; font-size: 14px; font: bold')
        self.txt_skipped.setStyleSheet('color: #8d44ad; font-size: 14px; font: bold')
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
        grid_status.addWidget(self.txt_skipped, 0, 4)
        grid_status.addWidget(self.txt_duplicates, 0, 5)

        grid_output.addWidget(self.output_area, 0, 0)

        grid_buttons.addWidget(btn_config, 3, 0)
        grid_buttons.addWidget(btn_input, 3, 1)
        grid_buttons.addWidget(btn_b_log, 3, 2)
        grid_buttons.addWidget(self.btn_abort, 3, 3)
        grid_buttons.addWidget(btn_quit, 3, 4)
        self.setLayout(grid)

    def show_config(self):
        program = 'C:/Program Files (x86)/Notepad++/notepad++.exe'
        subprocess.Popen([program, self.config_file_path])

    def show_input(self):
        program = 'C:/Program Files (x86)/Notepad++/notepad++.exe'
        subprocess.Popen([program, self.input_file_path])

    def show_bulklog(self):
        program = 'C:/Program Files (x86)/Notepad++/notepad++.exe'
        subprocess.Popen([program, self.bulk_log_path])


    def start_run(self):
        self.start_dialog.setVisible(True)
        # text, result = QInputDialog.getText(self, 'Credentials', 'FortiGate User', QLineEdit.Normal)
        # if result:
        #     self.firewall_user = str(text)
        #     text, result = QInputDialog.getText(self, 'Credentials', 'FortiGate Password', QLineEdit.Password)
        #     if result:
        #         self.firewall_password = str(text)
        #         text, result = QInputDialog.getText(self, 'Credentials', 'SSL VPN User', QLineEdit.Normal,
        #                                             self.firewall_user)
        #         if result:
        #             self.sslvpn_user = str(text)
        #             text, result = QInputDialog.getText(self, 'Credentials', 'SSL VPN Password', QLineEdit.Password,
        #                                                 self.firewall_password)
        #             if result:
        #                 self.sslvpn_password = str(text)
        #                 self.btn_start.setEnabled(False)
        #                 self.btn_abort.setEnabled(True)
        #                 self.output_append('black', 'START RUN')
        #                 self.changer = BulkChanger(self.output_append, self.update_status, self.end_run,
        #                                            self.exception_occured, self.firewall_user,
        #                                            self.firewall_password, self.sslvpn_user,
        #                                            self.sslvpn_password)
        #                 self.changer.start()

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
        self.changer.stop()
        self.output_append('black', 'RUN ABORTED, please wait...')

    def update_status(self, total, success, failed, skipped, duplicates):
        self.txt_total.setText('Total: ' + str(total))
        self.txt_success.setText('Success: ' + str(success))
        self.txt_failed.setText('Failed: ' + str(failed))
        self.txt_skipped.setText('Skipped: ' + str(skipped))
        self.txt_duplicates.setText('Duplicates: ' + str(duplicates))

    def quit_gui(self):
        self.update_status(0, 0, 0, 0, 0)
        self.output_area.clear()
        self.close()

    def exception_occured(self, reason):
        text = 'ERROR WITH ' + reason.upper()
        self.output_append('black', text)

    def output_append(self, color, text):
        if color.upper() == 'RED':
            self.output_area.setTextColor(QColor(255, 0, 0))
        elif color.upper() == 'GREEN':
            self.output_area.setTextColor(QColor(0, 128, 0))
        elif color.upper() == 'BLUE':
            self.output_area.setTextColor(QColor(0, 0, 250))
        elif color.upper() == 'PURPLE':
            self.output_area.setTextColor(QColor(141, 68, 173))
        else:
            self.output_area.setTextColor(QColor(0, 0, 0))
        self.output_area.append(text)

    def load_start_dialog(self):
        self.start_dialog.setFixedSize(700, 250)
        self.start_dialog.setWindowTitle('Credentials')

        # Buttons
        btn_dialog_cancle = QPushButton('Cancle', self)
        btn_dialog_cancle.clicked.connect(self.close_dialog)
        btn_dialog_cancle.resize(btn_dialog_cancle.sizeHint())

        self.btn_dialog_ok = QPushButton('OK', self)
        self.btn_dialog_ok.clicked.connect(self.ok_dialog)
        self.btn_dialog_ok.resize(self.btn_dialog_ok.sizeHint())


        # Labels
        txt_fgt = QLabel('FortiGate', self)
        txt_fgt.setStyleSheet('font-size: 12px; font: bold')
        txt_ssl = QLabel('SSL-VPN', self)
        txt_ssl.setStyleSheet('font-size: 12px; font: bold')
        txt_user1 = QLabel('Username:', self)
        txt_password1 = QLabel('Password:', self)
        txt_user2 = QLabel('Username:', self)
        txt_password2 = QLabel('Password:', self)
        txt_question = QLabel('Do you want to do a test run?', self)
        txt_question.setStyleSheet('font: bold; margin-bottom: 20px; margin-top: 20px')
        txt_ip = QLabel('IP-Address:', self)
        txt_port = QLabel('Port:', self)

        # Checkbox
        self.chk_question = QCheckBox(self)
        self.chk_question.setCheckState(Qt.Checked)
        self.chk_question.stateChanged.connect(self.invers_dialog_lines)

        # Inputs
        self.in_fgt_user = QLineEdit()
        self.in_fgt_user.setText(self.firewall_user)
        self.in_fgt_pwd = QLineEdit()
        self.in_fgt_pwd.setEchoMode(QLineEdit.Password)
        self.in_fgt_pwd.setText(self.firewall_password)
        self.in_ssl_user = QLineEdit()
        self.in_ssl_user.setText(self.sslvpn_user)
        self.in_ssl_pwd = QLineEdit()
        self.in_ssl_pwd.setEchoMode(QLineEdit.Password)
        self.in_ssl_pwd.setText(self.sslvpn_password)
        self.in_ip = QLineEdit()
        self.in_ip.setText(self.ipaddress)
        self.in_port = QLineEdit()
        self.in_port.setText(self.port)

        # Layout
        grid = QGridLayout(self)
        grid_credentials = QGridLayout()
        grid_question = QGridLayout()
        grid_firewall = QGridLayout()
        grid_buttons = QGridLayout()

        grid.addLayout(grid_credentials, 0, 0)
        grid.addLayout(grid_question, 1, 0)
        grid.addLayout(grid_firewall, 2, 0)
        grid.addLayout(grid_buttons, 3, 0)

        grid_credentials.addWidget(txt_fgt, 0, 0)
        grid_credentials.addWidget(txt_ssl, 0, 2)
        grid_credentials.addWidget(txt_user1, 1, 0)
        grid_credentials.addWidget(self.in_fgt_user, 1, 1)
        grid_credentials.addWidget(txt_user2, 1, 2)
        grid_credentials.addWidget(self.in_ssl_user, 1, 3)
        grid_credentials.addWidget(txt_password1, 2, 0)
        grid_credentials.addWidget(self.in_fgt_pwd, 2, 1)
        grid_credentials.addWidget(txt_password2, 2, 2)
        grid_credentials.addWidget(self.in_ssl_pwd, 2, 3)

        grid_credentials.addWidget(txt_question, 3, 1)
        grid_credentials.addWidget(self.chk_question, 3, 2)

        grid_credentials.addWidget(txt_ip, 4, 0)
        grid_credentials.addWidget(self.in_ip, 4, 1)
        grid_credentials.addWidget(txt_port, 4, 2)
        grid_credentials.addWidget(self.in_port, 4, 3)

        grid_buttons.addWidget(self.btn_dialog_ok, 0, 0)
        grid_buttons.addWidget(btn_dialog_cancle, 0, 1)

        self.start_dialog.setLayout(grid)

    def ok_dialog(self):
        self.start_dialog.setVisible(False)
        self.btn_start.setEnabled(False)
        self.btn_abort.setEnabled(True)
        self.output_append('black', 'START RUN')
        if self.chk_question.isChecked():
            self.verifier = BulkVerify(self.output_append, self.exception_occured, self.in_fgt_user.text(),
                                       self.in_fgt_pwd.text(), self.in_ssl_user.text(), self.in_ssl_pwd.text(),
                                       self.in_ip.text(), self.in_port.text())
            self.verifier.start()
            reply = QMessageBox.question(self, 'Verification', 'Are you happy with the changes?',
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.changer = BulkChanger(self.output_append, self.update_status, self.end_run, self.exception_occured,
                                           self.in_fgt_user.text(), self.in_fgt_pwd.text(), self.in_ssl_user.text(),
                                           self.in_ssl_pwd.text())
                self.changer.start()
            else:
                self.btn_start.setEnabled(True)
                self.btn_abort.setEnabled(False)
                self.output_append('black', 'VERIFICATION FAILED')
                self.output_append('black', '---------------------------------------------------------------------------')
        else:
            self.changer = BulkChanger(self.output_append, self.update_status, self.end_run, self.exception_occured,
                                       self.in_fgt_user.text(), self.in_fgt_pwd.text(), self.in_ssl_user.text(),
                                       self.in_ssl_pwd.text())
            self.changer.start()


    def close_dialog(self):
        self.start_dialog.close()

    def update_dialog(self):
        if self.in_ssl_user.text() == '' and self.in_fgt_user.text() != '':
            self.in_ssl_user.setText(self.in_fgt_user.text())
        if self.in_ssl_pwd.text() == '' and self.in_fgt_pwd.text() != '':
            self.in_ssl_pwd.setText(self.in_fgt_pwd.text())

    def invers_dialog_lines(self):
        if self.in_ip.isEnabled():
            self.in_ip.setEnabled(False)
            self.in_port.setEnabled(False)
        else:
            self.in_ip.setEnabled(True)
            self.in_port.setEnabled(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                self.update_dialog()
        return super(Bulk, self).eventFilter(obj, event)

