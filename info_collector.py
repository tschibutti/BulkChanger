import logging
from functions import csv_output, customers, executor
from utils.config import Config

if __name__ == '__main__':
    # VARIABLES
    devices = []
    failed_devices = []
    success_devices = []
    run_failed = 0

    # LOG FILE
    logging.basicConfig(filemode='w', filename='C:/BulkChanger/infocollector.log',
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

    # START EXECUTION
    i = 0
    while i < len(devices):
        print('Current device: ' + devices[i].customer)
        logging.info('******************************************************************')
        logging.info('IP: ' + devices[i].ip + '\t Port:' + devices[i].port + '\t Customer: ' + devices[i].customer)
        if devices[i].check_ip():
            logging.warning('ip-check: private ip, cannot handle right now')
            run_failed += 1
            failed_devices.append(devices[i])
            devices[i].reason = 'private ip address range'
            i += 1
            continue
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
        if devices[i].connected == 0:
            devices[i].reason = 'wrong username or password'
        elif devices[i].connected == 1:
            devices[i].firmware_check()
        if devices[i].connected == 0:
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
        executor.collect_info(devices[i])
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
    csv_output.save_info(devices)
    executor.run_summary(len(devices), run_failed, failed_devices)

    print('check log file for details')
    exit()
