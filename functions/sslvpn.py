import time
import logging
import subprocess
import xml.etree.ElementTree as ET
from utils.config import Config
from classes.ssl_profile import SSLprofile


def connect(ip, port, username, password):
    program = '"' + Config().sslvpn_folder + '/FortiSSLVPNclient.exe" connect -m -i -q -h ' + ip + ':' \
              + port + ' -u ' + username + ':' + password
    subprocess.call(program, shell=True)
    logging.info('sslvpn: connection established')
    time.sleep(5)


def disconnect():
    program = '"' + Config().sslvpn_folder + '/FortiSSLVPNclient.exe" disconnect'
    subprocess.call(program, shell=True)
    logging.info('sslvpn: connection terminated')
    time.sleep(5)


def match(customername, profiles):
    i = 0
    while i < profiles.__len__():
        if profiles[i].customer.upper() in customername.upper():
            logging.info('sslvpn: found matching ssl profile at #' + str(i))
            return i
        if customername.upper() in profiles[i].customer.upper():
            logging.info('sslvpn: found matching ssl profile at #' + str(i))
            return i
        i += 1
    return -1


def collect() -> []:
    sslprofile = []
    customer = []
    ip = []
    port = []

    # Export current config
    program = '"C:/Program Files (x86)/Fortinet/FortiClient/FCConfig.exe" -f "' + Config().sslvpn_folder +\
              '/FortiClient_Profile.xml" -m vpn -o export -q'
    subprocess.call(program, shell=True)

    # Collect Profiles
    tree = ET.parse('C:/forticlient/FortiClient_Profile.xml')
    root = tree.getroot()
    for name in root.iter('name'):
        if name.text is not None:
            customer.append(name.text)

    for server in root.iter('server'):
        if server.text is not None:
            ip.append(server.text.split(':')[0])
            port.append(server.text.split(':')[1])

    if customer.__len__() != ip.__len__():
        logging.error('sslvpn: cannot collect sslvpn profiles, abort execution')
        return None

    i = 0
    while i < customer.__len__():
        sslprofile.append(SSLprofile(customer[i], ip[i], port[i]))
        i += 1

    if not sslprofile:
        logging.error('sslvpn: no profiles found, abort execution')
        return None

    logging.info('sslvpn: collected all profiles -> found ' + str(len(sslprofile)) + ' profiles')
    return sslprofile
