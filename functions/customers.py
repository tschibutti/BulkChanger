import configparser
import logging
import os

from classes.device import Device
from utils.config import Config


def collect_firewalls() -> []:
    devices = []

    if (Config().firewall_ip == '') or (Config().firewall_port == ''):
        logging.info('devices: using folder as source')
    else:
        logging.info('devices: using config file as source')
        devices.append(Device('Config File', Config().firewall_ip, Config().firewall_port))
        logging.info('devices: found ' + str(len(devices)) + ' firewalls')
        return devices
    try:
        os.chdir(Config().devices_folder)
    except FileNotFoundError:
        logging.error('devices: folder not found')
        return

    for fileName in os.listdir("."):
        if '#nobulk' in fileName:
            continue
        if "FGT" in fileName:
            customer = fileName.split("FGT")[0]
            customer = customer[:(len(customer) - 3)]
            url = configparser.RawConfigParser()
            url.read(fileName)
            fgt_ip = url.get('InternetShortcut', 'URL')
            fgt_ip = fgt_ip.split("//")[1]
            fgt_ip = fgt_ip.split(":")[0]
            fgt_ip = fgt_ip.split("/")[0]
            fgt_port = url.get('InternetShortcut', 'URL')
            fgt_port = fgt_port.split("//")[1]
            if ":" in fgt_port:
                fgt_port = fgt_port.split(":")[1]
                fgt_port = fgt_port.split("/")[0]
            else:
                if "https" in url.get('InternetShortcut', 'URL'):
                    fgt_port = "443"
                else:
                    fgt_port = "80"
            devices.append(Device(customer,fgt_ip,fgt_port))
        if "FWF" in fileName:
            customer = fileName.split("FWF")[0]
            customer = customer[:(len(customer) - 3)]
            url = configparser.RawConfigParser()
            url.read(fileName)
            fgt_ip = url.get('InternetShortcut', 'URL')
            fgt_ip = fgt_ip.split("//")[1]
            fgt_ip = fgt_ip.split(":")[0]
            fgt_ip = fgt_ip.split("/")[0]
            fgt_port = url.get('InternetShortcut', 'URL')
            fgt_port = fgt_port.split("//")[1]
            if ":" in fgt_port:
                fgt_port = fgt_port.split(":")[1]
                fgt_port = fgt_port.split("/")[0]
            else:
                if "https" in url.get('InternetShortcut', 'URL'):
                    fgt_port = "443"
                else:
                    fgt_port = "80"
            devices.append(Device(customer, fgt_ip, fgt_port))
    if not devices:
        logging.error('devices: no firewalls found, abort execution')
        print('error: check log file for details')
        exit()
    logging.info('devices: collected all firewalls from source folder')
    logging.info('devices: found ' + str(len(devices)) + ' firewalls')
    return devices