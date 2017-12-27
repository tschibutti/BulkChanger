import logging
import os
import getpass
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

    def __init__(self, append_callback, status_callback, end_callback, exception_callback):
        QThread.__init__(self)
        self.append_callback = append_callback
        self.status_callback = status_callback
        self.end_callback = end_callback
        self.exception_callback = exception_callback
        self.runs = True

    def run(self):
        self.start_bulk()

    def stop(self):
        self.runs = False

    def start_bulk(self):
        # VARIABLES
        devices = []
        failed_devices = []
        skipped_devices = []
        success_devices = []
        duplicates = 0
        cmd = []
        sslvpn_user = None
        sslvpn_password = None
        sslconnected = False

        # LOG FILE
        logging.basicConfig(filemode='w', filename='C:/BulkChanger/bulkchanger.log',
                            level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        if Config().log_level.upper() == 'DEBUG':
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
        if not devices:
            self.exception_callback('devices')
            self.stop()

        # COLLECT SSL VPN PROFILES:
        sslprofile = sslvpn.collect()
        if sslprofile == None:
            self.exception_callback('ssl vpn profile')
            self.stop()

        # GET COMMANDS
        cmd = cli_converter.convert_command('input.txt', Config().input_folder)
        if not cmd:
            self.exception_callback('command line input')
            self.stop()
        # print_cmd(cmd)
        # exit()

        # START EXECUTION
        i = 0
        while i < len(devices) and self.runs:
            print('Current device: ' + devices[i].customer)
            self.status_callback(len(devices) + duplicates, len(success_devices), len(failed_devices),
                                 len(skipped_devices), duplicates)
            logging.info('******************************************************************')
            logging.info('IP: ' + devices[i].ip + '\t Port:' + devices[i].port + '\t Customer: ' + devices[i].customer)
            if devices[i].check_ip():
                # check if local device
                devices[i].ping()
                if devices[i].online == -1:
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
                devices[i].reason = 'no ping resonse'
                self.append_callback('red', devices[i].customer)
                i += 1
                continue
            logging.debug('ping: device is online')
            devices[i].login(firewall_user, firewall_password)
            if not devices[i].connected:
                devices[i].reason = 'wrong username or password'
            elif devices[i].connected:
                devices[i].firmware_check()
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
            # todo 5.2 does not support the check -> other options?
            if devices[i].fortimanager and devices[i].fortimanager != 'unknown':
                skipped_devices.append(devices[i])
                self.append_callback('purple', devices[i].customer)
                i += 1
                continue
            if Config().backup_enable:
                executor.perform_backup(devices[i])
            if '5.2' in devices[i].firmware:
                cli_converter.v52_marshalling(cmd)
            executor.run_command(devices[i], cmd)
            if '5.2' in devices[i].firmware:
                cli_converter.v52_unmarshalling(cmd)
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
            self.append_callback('green', devices[i].customer)
            i += 1

        self.status_callback(len(devices) + duplicates, len(success_devices), len(failed_devices),
                             len(skipped_devices), duplicates)

        if sslconnected:
            sslconnected = False
            sslvpn.disconnect()

        # DELTE TEMPORARY FILES
        file = Config().input_folder + '/ca.cer'
        try:
            os.remove(file)
        except FileNotFoundError:
            logging.debug('certifiacte: source file not exist')

        # PRINT RESULT
        executor.run_summary(len(devices), len(success_devices), failed_devices, duplicates, skipped_devices)

        # REMOVE LOGGING HANDLERS
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        print('check log file for details')
        self.end_callback()