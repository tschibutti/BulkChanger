import logging
import getpass
from PyQt5.QtCore import QThread
from functions import csv_output, customers, executor, sslvpn
from utils.config import Config


class InfoCollector(QThread):
    is_aborted = False

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
        logging.basicConfig(filemode='w', filename='C:/BulkChanger/infocollector.log',
                            level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        if Config().log_level == 'debug':
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
        i = 0
        while i < len(devices) and self.runs:
            print('Current device: ' + devices[i].customer)
            self.status_callback(len(devices) + duplicates, len(success_devices), len(failed_devices), duplicates)
            logging.info('******************************************************************')
            logging.info('IP: ' + devices[i].ip + '\t Port:' + devices[i].port + '\t Customer: ' + devices[i].customer)
            if devices[i].check_ip():
                # check if local device
                devices[i].ping()
                if devices[i].online == 1:
                    index = sslvpn.match(devices[i].customer, sslprofile)
                    if index == -1:
                        logging.warning('sslvpn: found no matching ssl profile')
                        failed_devices.append(devices[i])
                        devices[i].reason = 'private ip and no sslvpn profile'
                        self.append_callback('red', devices[i].customer)
                        i += 1
                        continue
                    sslvpn.connect(sslprofile[index].ip, sslprofile[index].port, self.sslvpn_user, self.sslvpn_password)
                    sslconnected = True
            devices[i].ping()
            if devices[i].online == 1:
                logging.warning('ping: device is offline, skip device')
                failed_devices.append(devices[i])
                devices[i].reason = 'no ping response'
                self.append_callback('red', devices[i].customer)
                i += 1
                continue
            logging.debug('ping: device is online')
            devices[i].login(self.firewall_user, self.firewall_password)
            if not devices[i].connected:
                devices[i].reason = 'wrong username or password'
            if not devices[i].connected:
                failed_devices.append(devices[i])
                self.append_callback('red', devices[i].customer)
                i += 1
                continue
            if devices[i].check_duplicate(devices, i):
                devices.remove(devices[i])
                duplicates += 1
                self.append_callback('blue', devices[i].customer)
                continue
            executor.fmg_check(devices[i])
            if Config().backup_enable.upper() == 'TRUE':
                executor.perform_backup(devices[i])
            executor.collect_info(devices[i])
            devices[i].logout()
            devices[i].ping()
            if devices[i].online == 1:
                logging.warning('ping: no response after command execution')
                failed_devices.append(devices[i])
                self.append_callback('red', devices[i].customer)
                i += 1
                continue
            logging.debug('ping: device is still online')
            success_devices.append(devices[i])
            if sslconnected:
                sslconnected = False
                sslvpn.disconnect()
            self.append_callback('green', devices[i].customer)
            i += 1

        self.status_callback(len(devices) + duplicates, len(success_devices), len(failed_devices), duplicates)

        if sslconnected:
            sslconnected = False
            sslvpn.disconnect()

        # PRINT RESULT
        csv_output.save_info(devices, 'output.csv')
        executor.run_summary(len(devices), len(success_devices), failed_devices, duplicates)

        # REMOVE LOGGING HANDLERS
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        print('check log file for details')
        self.end_callback()
