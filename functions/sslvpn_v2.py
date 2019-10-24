import os
import logging
import time
import subprocess
from classes.ssl_profile import SSLprofile

RASDIAL_EXE = os.path.expandvars("%SystemRoot%/System32/rasdial.exe")

def connect(connection, user, passwd):
    # rasdial.exe connection username password
    try:
        subprocess.check_call([RASDIAL_EXE, connection, user, passwd])
        logging.info('sslvpn: connection established')
        time.sleep(1)
        return True
    except subprocess.CalledProcessError:
        logging.error('sslvpn: could not connect sslvpn')
        time.sleep(1)
        return False

def disconnect():
    try:
        subprocess.check_call([RASDIAL_EXE, '/disconnect'])
        logging.info('sslvpn: connection terminated')
        time.sleep(1)
        return False
    except subprocess.CalledProcessError:
        logging.error('sslvpn: could not disconnect sslvpn')
        time.sleep(1)
        return True


def match(cust, con):
    for c in con:
        if (c.name.upper() in cust.upper()) or (cust.upper() in c.name.upper()):
            logging.info('sslvpn: found matching ssl profile at #' + str(con.index(c)))
            return con.index(c)
    return -1


def collect() -> []:
    connection = []
    rasphone = os.path.expandvars('%userprofile%/AppData/Roaming/Microsoft/Network/Connections/Pbk/rasphone.pbk')

    with open(rasphone, 'r') as file:
        for line in file:
            if ('[' in line) and (']' in line):
                connection.append(SSLprofile(line[1:-2]))

    logging.info('sslvpn: collected all profiles -> found ' + str(len(connection)) + ' profiles')
    return connection
