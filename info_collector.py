import logging
import os
import sys
from PyQt5.QtCore import QThread
from functions import csv_output, customers, executor, sslvpn
from utils.config import Config


class InfoCollector(QThread):

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
        self.start_info()

    def stop(self):
        self.runs = False

    def start_info(self):
        # VARIABLES
        devices = []
        sslprofile = []
        sslconnected = False
        failed_devices = []
        success_devices = []
        duplicates = 0
        sslconnected = False

        # LOG FILE
        if getattr(sys, 'frozen', False):
            log_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'infocollector.log')
        else:
            log_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'infocollector.log')
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
            self.exception_callback('devices')
            self.stop()

        # COLLECT SSL VPN PROFILES:
        sslprofile = sslvpn.collect()
        if sslprofile == None:
            self.exception_callback('ssl vpn profile')
            self.stop()

        # START EXECUTION
        for device in devices:
            if not self.runs:
                break
            self.status_callback(len(devices), len(success_devices), len(failed_devices), duplicates)
            logging.info('******************************************************************')
            logging.info('IP: ' + device.ip + '\t Port:' + device.port + '\t Customer: ' + device.customer)
            if device.check_ip():
                # check if local device
                device.ping()
                if device.online == 1:
                    index = sslvpn.match(device.customer, sslprofile)
                    if index == -1:
                        logging.warning('sslvpn: found no matching ssl profile')
                        failed_devices.append(device)
                        device.reason = 'private ip and no sslvpn profile'
                        self.append_callback('red', device.customer)
                        continue
                    sslvpn.connect(sslprofile[index].ip, sslprofile[index].port, self.sslvpn_user, self.sslvpn_password)
                    sslconnected = True
            device.ping()
            if device.online == 1:
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
                failed_devices.append(device)
                self.append_callback('red', device.customer)
                continue
            if device.check_duplicate(devices, devices.index(device)):
                duplicates += 1
                self.append_callback('blue', device.customer)
                continue
            executor.fmg_check(device)
            executor.vdom_check(device)
            if Config().backup_enable.upper() == 'TRUE' and not '5.2' in device.firmware:
                executor.perform_backup(device)
            executor.collect_info(device)
            device.logout()
            device.ping()
            if device.online == 1:
                logging.warning('ping: no response after command execution')
                failed_devices.append(device)
                self.append_callback('red', device.customer)
                continue
            logging.debug('ping: device is still online')
            success_devices.append(device)
            if sslconnected:
                sslconnected = False
                sslvpn.disconnect()
            self.append_callback('green', device.customer)

        self.status_callback(len(devices), len(success_devices), len(failed_devices), duplicates)

        if sslconnected:
            sslconnected = False
            sslvpn.disconnect()

        # PRINT RESULT
        csv_output.save_info(success_devices)
        executor.run_summary(log_path, len(devices), len(success_devices), failed_devices, duplicates)

        # REMOVE LOGGING HANDLERS
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        self.end_callback()
