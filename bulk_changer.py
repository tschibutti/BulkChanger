import logging
import os
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
    success_devices = []
    cmd = []
    run_failed = 0

    # LOG FILE
    logging.basicConfig(filemode='w',
                        filename='D:/Daten/Dropbox/Florian/50 FortiNet/REST API/BulkChanger/bulkchanger.log',
                        level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # CONFIG FILE
    if (Config().firewall_user == '') or (Config().firewall_password == ''):
        # USER AND PASSWORD INPUT
        print('user or password not defined in config file')
        firewall_user = input('firewall username: ')
        # not working with PyCharm
        # firewall_password = getpass.getpass(prompt='Firewall password: ', stream=None)
        firewall_password = input('firewall password: ')
    else:
        firewall_user = Config().firewall_user
        firewall_password = Config().firewall_password

    # GET FIREWALL LIST
    devices = customers.collect_firewalls()

    # GET COMMANDS
    cmd = cli_converter.convert_command('input.txt', Config().input_folder)
    print_cmd(cmd)
    # exit()

    # START EXECUTION
    i = 0
    while i < len(devices):
        print('Current device: ' + devices[i].customer)
        logging.info('******************************************************************')
        logging.info('IP: ' + devices[i].ip + '\t Port:' + devices[i].port + '\t Customer: ' + devices[i].customer)
        devices[i].ping()
        if devices[i].online == 1:
            logging.warning('ping: device is offline, skip device')
            run_failed += 1
            failed_devices.append(devices[i])
            devices[i].reason = 'no ping resonde'
            i += 1
            continue
        logging.debug('ping: device is online')
        devices[i].login(firewall_user, firewall_password)
        if not devices[i].connected:
            devices[i].reason = 'wrong username or password'
        elif devices[i].connected:
            devices[i].firmware_check()
        if not devices[i].connected:
            run_failed += 1
            failed_devices.append(devices[i])
            i += 1
            continue
        executor.fmg_check(devices[i])
        if devices[i].fortimanager:
            run_failed += 1
            failed_devices.append(devices[i])
            i += 1
            continue
        executor.perform_backup(devices[i])
        executor.run_command(devices[i], cmd)
        devices[i].logout()
        devices[i].ping()
        if devices[i].online == 1:
            logging.warning('ping: no response after command execution')
            run_failed += 1
            failed_devices.append(devices[i])
            i += 1
            continue
        logging.debug('ping: device is still online')
        success_devices.append(devices[i])
        i += 1

    # PRINT RESULT
    executor.run_summary(len(devices), run_failed, failed_devices)

    # DELTE TEMPORARY FILES
    file = Config().input_folder + '/ca.cer'
    try:
        os.remove(file)
    except FileNotFoundError:
        logging.debug('certifiacte: source file not exist')

    print('check log file for details')
    exit()
