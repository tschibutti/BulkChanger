import logging
import os
import getpass
from functions import cli_converter, customers, executor
from utils.config import Config


def print_cmd(command):
    j = 0
    while j < len(command):
        print(command[j].path + ' ' + command[j].body + ' A:' + command[j].action + ' N:' + command[j].name + ' API:'
              + command[j].api)
        j += 1


if __name__ == '__main__':
    # VARIABLES
    devices = []
    failed_devices = []
    skipped_devices = []
    success_devices = []
    cmd = []

    # LOG FILE
    logging.basicConfig(filemode='w',
                        filename='C:/BulkChanger/bulkchanger.log',
                        level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # CONFIG FILE
    if (Config().firewall_user == '') or (Config().firewall_password == ''):
        # USER AND PASSWORD INPUT
        print('user or password not defined in config file')
        firewall_user = input('firewall username: ')
        # not working with PyCharm
        firewall_password = getpass.getpass(prompt='Firewall password: ', stream=None)
        #firewall_password = input('firewall password: ')
    else:
        firewall_user = Config().firewall_user
        firewall_password = Config().firewall_password

    # GET FIREWALL LIST
    devices = customers.collect_firewalls()

    # GET COMMANDS
    cmd = cli_converter.convert_command('input.txt', Config().input_folder)
    # print_cmd(cmd)
    # exit()

    # START EXECUTION
    i = 0
    while i < len(devices):
        print('Current device: ' + devices[i].customer)
        logging.info('******************************************************************')
        logging.info('IP: ' + devices[i].ip + '\t Port:' + devices[i].port + '\t Customer: ' + devices[i].customer)
        if devices[i].check_ip():
            logging.warning('ip-check: private ip, cannot handle right now')
            failed_devices.append(devices[i])
            devices[i].reason = 'private ip address range'
            i += 1
            continue
        devices[i].ping()
        if devices[i].online == 1:
            logging.warning('ping: device is offline, skip device')
            failed_devices.append(devices[i])
            devices[i].reason = 'no ping resonse'
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
            i += 1
            continue
        executor.fmg_check(devices[i])
        if devices[i].fortimanager:
            skipped_devices.append(devices[i])
            i += 1
            continue
        executor.perform_backup(devices[i])
        executor.run_command(devices[i], cmd)
        devices[i].logout()
        devices[i].ping()
        if devices[i].online == 1:
            logging.warning('ping: no response after command execution')
            failed_devices.append(devices[i])
            i += 1
            continue
        logging.debug('ping: device is still online')
        success_devices.append(devices[i])
        i += 1

    # DELTE TEMPORARY FILES
    file = Config().input_folder + '/ca.cer'
    try:
        os.remove(file)
    except FileNotFoundError:
        logging.debug('certifiacte: source file not exist')

    # PRINT RESULT
    executor.run_summary(len(devices), failed_devices, skipped_devices)

    print('check log file for details')
    exit()
