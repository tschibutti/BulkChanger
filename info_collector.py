import logging
import getpass
from PyQt5.QtCore import QThread
from functions import csv_output, customers, executor, sslvpn
from utils.config import Config

class InfoCollector(QThread):

    is_aborted = False

    def __init__(self, append_callback, status_callback, end_callback):
        QThread.__init__(self)
        self.append_callback = append_callback
        self.status_callback = status_callback
        self.end_callback = end_callback

    def run(self):
        self.start_info()

    def stop(self):
        self.is_aborted = True

    def start_info(self):
        # VARIABLES
        devices = []
        sslprofile = []
        sslconnected = False
        failed_devices = []
        success_devices = []
        duplicates = 0
        sslvpn_user = None
        sslvpn_password = None
        is_aborted = False

        # LOG FILE
        logging.basicConfig(filemode='w', filename='C:/BulkChanger/infocollector.log',
                            level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        if Config().log_level == 'debug':
            logging.getLogger().setLevel(logging.DEBUG)


        # CONFIG FILE
        if (Config().firewall_user == '') or (Config().firewall_password == ''):
            # USER AND PASSWORD INPUT
            print('user or password not defined in config file')
            firewall_user = input('firewall username: ')
            # not working with PyCharm
            firewall_password = getpass.getpass(prompt='Firewall password: ', stream=None)
            # firewall_password = input('firewall password: ')
        else:
            firewall_user = Config().firewall_user
            firewall_password = Config().firewall_password

        # GET FIREWALL LIST
        devices = customers.collect_firewalls()
        customers.remove_umlaut(devices)

        # COLLECT SSL VPN PROFILES:
        sslprofile = sslvpn.collect()

        # START EXECUTION
        i = 0
        while i < len(devices):
            print('Current device: ' + devices[i].customer)
            self.status_callback(len(devices)+duplicates, len(success_devices), len(failed_devices), duplicates)
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
                    if sslvpn_user == None and sslvpn_password == None:
                        # CREDENTIALS FOR SSL VPN
                        sslvpn_user = input('sslvpn username: ')
                        sslvpn_password = input('sslvpn password: ')
                        # sslvpn_password = getpass.getpass(prompt='sslvpn password: ', stream=None)
                    sslvpn.connect(sslprofile[index].ip, sslprofile[index].port, sslvpn_user, sslvpn_password)
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
            devices[i].login(firewall_user, firewall_password)
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
            # executor.perform_backup(devices[i])
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
            if self.is_aborted:
                break
            i += 1

        self.status_callback(len(devices)+duplicates, len(success_devices), len(failed_devices), duplicates)

        if sslconnected:
            sslconnected = False
            sslvpn.disconnect()

        # PRINT RESULT
        csv_output.save_info(devices, 'output.csv')
        executor.run_summary(len(devices), failed_devices, duplicates)

        # REMOVE LOGGING HANDLERS
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        print('check log file for details')
        self.end_callback()