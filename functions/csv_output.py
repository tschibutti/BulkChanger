import csv
import logging
from utils.config import Config


def save_info(devices):
    file = Config().output_folder + '/output.csv'
    try:
        with open(file, 'w') as csvfile:
            header = ['Kundenname', 'IP-Adresse', 'Port', 'Seriennummer', 'Firmware', 'FortiCare', 'FortiGuard',
                      'AV-DB', 'FortiManager', 'Uptime', 'SSIDs', 'AP-Name', 'AP-Serials', 'AP-Firmware']
            writer = csv.DictWriter(csvfile, fieldnames=header, delimiter=';')
            writer.writeheader()

            i = 0
            while i < len(devices):
                writer.writerow({'Kundenname': devices[i].customer, 'IP-Adresse': devices[i].ip,
                                 'Port': devices[i].port, 'Seriennummer': devices[i].serial,
                                 'Firmware': devices[i].firmware, 'FortiCare': devices[i].forticare,
                                 'FortiGuard': devices[i].fortiguard, 'AV-DB': devices[i].av_db,
                                 'FortiManager': devices[i].fortimanager, 'Uptime': devices[i].uptime,
                                 'SSIDs': ','.join(map(str, set(devices[i].ssid))),
                                 'AP-Name': ','.join(map(str, devices[i].ap_name)),
                                 'AP-Serials': ','.join(map(str, devices[i].ap_serial)),
                                 'AP-Firmware': ','.join(map(str, devices[i].ap_firmware))})
                i += 1
            csvfile.close()
    except IOError:
        logging.error('csv: file is in use')
