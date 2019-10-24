import configparser
import logging
import os
import re

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

    if not os.path.exists(Config().devices_folder):
        logging.error('devices: folder not found')
        return

    os.chdir(Config().devices_folder)
    for fileName in os.listdir('.'):
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
    logging.info('devices: collected all firewalls from folder -> found ' + str(len(devices)) + ' firewalls')
    return remove_umlaut(devices)


def remove_umlaut(devices):
    for dev in devices:
        dev.customer = re.sub(r'ä', 'ae', dev.customer)
        dev.customer = re.sub(r'ö', 'oe', dev.customer)
        dev.customer = re.sub(r'ü', 'ue', dev.customer)
        dev.customer = re.sub(r'Ä', 'AE', dev.customer)
        dev.customer = re.sub(r'Ö', 'OE', dev.customer)
        dev.customer = re.sub(r'Ü', 'UE', dev.customer)
