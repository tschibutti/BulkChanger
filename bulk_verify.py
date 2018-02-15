import os
import urllib3
import sys
import subprocess
import logging
from PyQt5.QtCore import QThread
from functions import cli_converter, executor
from requests import RequestException
from requests import Session
from utils.config import Config
from classes.device import Device

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BulkVerify(QThread):

    def __init__(self, append_callback, exception_callback, fwuser, fwpassword, ssluser, sslpassword,
                 device_ip, device_port):
        QThread.__init__(self)
        self.append_callback = append_callback
        self.exception_callback = exception_callback

        self.firewall_user = fwuser
        self.firewall_password = fwpassword
        self.sslvpn_user = ssluser
        self.sslvpn_password = sslpassword

        self.device = Device('Trial Device', device_ip, device_port)

    def run(self):
        self.start_bulk()

    def start_bulk(self):
        # LOG FILE
        if getattr(sys, 'frozen', False):
            log_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'bulkchanger.log')
        else:
            log_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bulkchanger.log')
        if not os.path.isfile(log_path):
            temp_file = open(log_path, 'w+')
            temp_file.close()
        logging.basicConfig(filemode='w', filename=log_path,
                            level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        if Config().log_level.upper() == 'DEBUG':
            logging.getLogger().setLevel(logging.DEBUG)

        # CREDENTIALS
        if not ((Config().firewall_user == '') or (Config().firewall_password == '')):
            self.firewall_user = Config().firewall_user
            self.firewall_password = Config().firewall_password

        if not ((Config().sslvpn_user == '') or (Config().sslvpn_password == '')):
            self.sslvpn_user = Config().sslvpn_user
            self.sslvpn_password = Config().sslvpn_password

        # GET COMMANDS
        if getattr(sys, 'frozen', False):
            input_file_path = os.path.abspath(os.path.dirname(sys.executable))
        else:
            input_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'input')
        cmd = cli_converter.convert_command('input.txt', input_file_path)
        if not cmd:
            self.exception_callback('command line input')
            self.stop()
        cli_converter.marshalling(cmd)

        # START EXECUTION
        self.device.session = Session()
        bodyhash = {'username': self.firewall_user, 'secretkey': self.firewall_password}
        try:
            self.device.session.post('https://' + self.device.ip + ':' + self.device.port + '/logincheck',
                                     data=bodyhash, verify=False, timeout=self.device.timeout)
        except RequestException:
            self.append_callback('red', self.device.customer)
            print('execption during login')
            return
        for cookie in self.device.session.cookies:
            try:
                if cookie.name == 'ccsrftoken':
                    csrftoken = cookie.value[1:-1]
                    self.device.session.headers.update({'X-CSRFTOKEN': csrftoken})
            except:
                self.append_callback('red', self.device.customer)
                print('error with cookie')
                return
        executor.perform_backup(self.device, 'before')
        executor.run_command(self.device, cmd)
        executor.perform_backup(self.device, 'after')
        self.device.session.post('https://' + self.device.ip + ':' + self.device.port + '/logout')
        self.append_callback('green', self.device.customer)
        program = 'C:/Program Files (x86)/Notepad++/plugins/ComparePlugin/compare.exe'
        file1 = Config().backup_folder + '/' + 'before.conf'
        file2 = Config().backup_folder + '/' + 'after.conf'
        subprocess.Popen([program, file1, file2], shell = True)