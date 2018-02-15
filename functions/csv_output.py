import sys
import os
import csv
import logging
import time
import subprocess


def save_info(devices):
    if getattr(sys, 'frozen', False):
        output_file = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'fortigate.csv')
    else:
        output_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'fortigate.csv')
    try:
        with open(output_file, 'w') as csvfile:
            header = ['Kundenname', 'IP-Adresse', 'Port', 'Seriennummer', 'Firmware', 'FortiCare', 'FortiGuard',
                      'AV-DB', 'FortiManager', 'VDOM', 'Local-in-policy', 'SSIDs', 'AP-Name', 'AP-Serials', 'AP-Firmware']
            writer = csv.DictWriter(csvfile, fieldnames=header, delimiter=';', lineterminator='\n')
            writer.writeheader()

            i = 0
            while i < len(devices):
                writer.writerow({'Kundenname': devices[i].customer, 'IP-Adresse': devices[i].ip,
                                 'Port': devices[i].port, 'Seriennummer': devices[i].serial,
                                 'Firmware': devices[i].firmware, 'FortiCare': devices[i].forticare,
                                 'FortiGuard': devices[i].fortiguard, 'AV-DB': devices[i].av_db,
                                 'FortiManager': devices[i].fortimanager, 'VDOM': devices[i].vdom_mode,
                                 'Local-in-policy': devices[i].local_in,
                                 'SSIDs': ','.join(map(str, set(devices[i].ssid))),
                                 'AP-Name': ','.join(map(str, devices[i].ap_name)),
                                 'AP-Serials': ','.join(map(str, devices[i].ap_serial)),
                                 'AP-Firmware': ','.join(map(str, devices[i].ap_firmware))})
                i += 1
            csvfile.close()
    except IOError:
        logging.error('csv: file is in use, terminate excel')
        subprocess.call('taskkill /f /im excel.exe >> null', shell=True)
        time.sleep(2)
        save_info(devices)
