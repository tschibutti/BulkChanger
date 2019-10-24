import logging
import os
import sys
from PyQt5.QtCore import QThread
from functions import cli_converter, customers, executor, sslvpn
from utils.config import Config


def print_cmd(command):
    j = 0
    while j < len(command):
        print(command[j].path + ' ' + command[j].body + ' A:' + command[j].action + ' N:' + command[j].name + ' API:'
              + command[j].api)
        j += 1


class BulkChanger(QThread):

    def __init__(self, append_callback, status_callback, end_callback, exception_callback, fwuser, fwpassword,
                 ssluser, sslpassword):
        QThread.__init__(self)
        self.append_callback = append_callback
        self.status_callback = status_callback
        self.end_callback = end_callback
        self.exception_callback = exception_callback

        self.runs = True

        self.firewall_user = fwuser
        self.firewall_password = fwpassword
        self.sslvpn_user = ssluser
        self.sslvpn_password = sslpassword

    def run(self):
        self.start_bulk()

    def stop(self):
        self.runs = False

    def start_bulk(self):
        # VARIABLES
        # devices = []
        failed_devices = []
        skipped_devices = []
        success_devices = []
        duplicates = 0
        # cmd = []
        # sslvpn_user = None
        # sslvpn_password = None
        sslconnected = False

        # LOG FILE
        # REMOVE LOGGING HANDLERS
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

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

        # GET FIREWALL LIST
        devices = customers.collect_firewalls()
        if not devices:
            logging.error('devices: no firewalls found, abort execution')
            self.exception_callback('devices')
            self.stop()

        # COLLECT SSL VPN PROFILES:
        sslprofile = sslvpn.collect()
        if not sslprofile:
            logging.error('sslvpn: no profiles found, abort execution')
            self.exception_callback('ssl vpn profile')
            self.stop()

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
        # print_cmd(cmd)
        # exit()

        # START EXECUTION
        for device in devices:
            if not self.runs:
                break
            self.status_callback(len(devices), len(success_devices), len(failed_devices),
                                 len(skipped_devices), duplicates)
            logging.info('******************************************************************')
            logging.info('IP: ' + device.ip + '\t Port:' + device.port + '\t Customer: ' + device.customer)
            if device.check_ip():
                # check if local device
                if device.ping():
                    index = sslvpn.match(device.customer, sslprofile)
                    if index == -1:
                        logging.warning('sslvpn: found no matching ssl profile')
                        failed_devices.append(device)
                        device.reason = 'private ip and no sslvpn profile'
                        self.append_callback('red', device.customer)
                        continue
                    if not sslvpn.connect(sslprofile[index].ip, sslprofile[index].port, self.sslvpn_user, self.sslvpn_password):
                        self.exception_callback('sslvpn connect')
                        self.stop()
            if device.ping():
                # try to login anyway
                device.login(self.firewall_user, self.firewall_password)
                if not device.connected:
                    logging.warning('ping: device is offline, skip device')
                    failed_devices.append(device)
                    device.reason = 'no ping response'
                    self.append_callback('red', device.customer)
                    continue
            logging.debug('ping: device is online')
            device.login(self.firewall_user, self.firewall_password)
            if not device.connected:
                device.reason = 'wrong username or password'
            elif device.connected:
                device.firmware_check()
            if not device.connected:
                failed_devices.append(device)
                self.append_callback('red', device.customer)
                continue
            if device.check_duplicate(devices, devices.index(device)):
                duplicates += 1
                self.append_callback('blue', device.customer)
                continue
            executor.fmg_check(device)
            if device.fortimanager == 'enable':
                skipped_devices.append(device)
                self.append_callback('purple', device.customer)
                continue
            executor.vdom_check(device)
            if device.vdom_mode == 'enable':
                skipped_devices.append(device)
                self.append_callback('purple', device.customer)
                continue
            if Config().backup_enable.upper() == 'TRUE' and not '5.2' in device.firmware:
                executor.perform_backup(device)
            executor.run_command(device, cmd)
            device.logout()
            logging.debug('ping: device is still online')
            success_devices.append(device)
            self.append_callback('green', device.customer)

        self.status_callback(len(devices), len(success_devices), len(failed_devices),
                             len(skipped_devices), duplicates)

        if sslconnected:
            sslconnected = False
            sslvpn.disconnect()

        # DELTE TEMPORARY FILES
        file = input_file_path + '/ca.cer'
        try:
            os.remove(file)
        except FileNotFoundError:
            logging.debug('certifiacte: source file not exist')

        # PRINT RESULT
        executor.run_summary(log_path, len(devices), len(success_devices), failed_devices, duplicates, skipped_devices)

        # REMOVE LOGGING HANDLERS
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        self.end_callback()