import logging
import base64
import re
import time

from utils.config import Config


def run_command(device, cmd):
    i = 0
    while i < len(cmd):
        # req = device.session.get(
        #     'https://' + device.ip + ':' + device.port + '/api/v2/cmdb/webfilter/profile/wf_standard-backup')
        # print(req)
        # rjson = req.json()
        # print(rjson)
        # exit()

        if 'delete' in cmd[i].action:
            run_delete(device, cmd[i])
        elif 'clone' in cmd[i].action:
            run_clone(device, cmd[i])
        elif 'rename' in cmd[i].action:
            run_rename(device, cmd[i])
        elif 'cmdb' in cmd[i].api:
            run_config(device, cmd[i])
        elif 'upload' in cmd[i].action:
            run_upload(device, cmd[i])
        else:
            logging.error('executor: error with the command')
        i += 1


def run_delete(device, cmd):
    # req = device.session.delete('https://' + device.ip + ':' + device.port + '/api/v2/' +
    #                            cmd.api + '/' + cmd.path + '/' + cmd.name + '?vdom=root')
    if check_existence(device, cmd) == 404:
        logging.warning('executor: object not exist, nothing to delete')
    elif check_existence(device, cmd) == 200:
        logging.info('executor: object exist, delete it')
        req = device.session.delete('https://' + device.ip + ':' + device.port + '/api/v2/' +
                                    cmd.api + '/' + cmd.path + '/' + cmd.name + '?vdom=root')
        check_req(req)


def run_rename(device, cmd):
    req = device.session.put('https://' + device.ip + ':' + device.port + '/api/v2/' +
                             cmd.api + '/' + cmd.path + '?vdom=root', data=cmd.body)
    check_req(req)


def run_upload(device, cmd):
    logging.warning('executor: certificate upload is not supported yet')
    # url = 'https://' + device.ip + ':' + device.port + '/api/v2/' + cmd.api + '/' + cmd.path
    # file = Config().input_folder + '/ca.cer'
    # cmd.body = re.sub(r'}', ',"ca":"-----BEGIN CERTIFICATE----- MIIDfTCCAuagAwIBAgIDErvmMA0GCSqGSIb3DQEBBQUAME4xCzAJBgNVBAYTAlVT MRAwDgYDVQQKEwdFcXVpZmF4MS0wKwYDVQQLEyRFcXVpZmF4IFNlY3VyZSBDZXJ0 aWZpY2F0ZSBBdXRob3JpdHkwHhcNMDIwNTIxMDQwMDAwWhcNMTgwODIxMDQwMDAw WjBCMQswCQYDVQQGEwJVUzEWMBQGA1UEChMNR2VvVHJ1c3QgSW5jLjEbMBkGA1UE AxMSR2VvVHJ1c3QgR2xvYmFsIENBMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB CgKCAQEA2swYYzD99BcjGlZ+W988bDjkcbd4kdS8odhM+KhDtgPpTSEHCIjaWC9m OSm9BXiLnTjoBbdqfnGk5sRgprDvgOSJKA+eJdbtg/OtppHHmMlCGDUUna2YRpIu T8rxh0PBFpVXLVDviS2Aelet8u5fa9IAjbkU+BQVNdnARqN7csiRv8lVK83Qlz6c JmTM386DGXHKTubU1XupGc1V3sjs0l44U+VcT4wt/lAjNvxm5suOpDkZALeVAjmR Cw7+OC7RHQWa9k0+bw8HHa8sHo9gOeL6NlMTOdReJivbPagUvTLrGAMoUgRx5asz PeE4uwc2hGKceeoWMPRfwCvocWvk+QIDAQABo4HwMIHtMB8GA1UdIwQYMBaAFEjm aPkr0rKV10fYIyAQTzOYkJ/UMB0GA1UdDgQWBBTAephojYn7qwVkDBF9qn1luMrM TjAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjA6BgNVHR8EMzAxMC+g LaArhilodHRwOi8vY3JsLmdlb3RydXN0LmNvbS9jcmxzL3NlY3VyZWNhLmNybDBO BgNVHSAERzBFMEMGBFUdIAAwOzA5BggrBgEFBQcCARYtaHR0cHM6Ly93d3cuZ2Vv dHJ1c3QuY29tL3Jlc291cmNlcy9yZXBvc2l0b3J5MA0GCSqGSIb3DQEBBQUAA4GB AHbhEm5OSxYShjAGsoEIz/AIx8dxfmbuwu3UOx//8PDITtZDOLC5MH0Y0FWDomrL NhGc6Ehmo21/uBPUR/6LWlxz/K7ZGzIZOKuXNBSqltLroxwUCEm2u+WR74M26x1W b8ravHNjkOR/ez4iyz0H7V84dJzjA1BOoa+Y7mHyhD8S -----END CERTIFICATE-----"}', cmd.body)
    # print(cmd.body)
    # req = device.session.post('https://' + device.ip + ':' + device.port + '/api/v2/cmdb/' + cmd.path, data=cmd.body)
    # # req = device.session.post(url=url, params={"vdom": "root"}, data={"source": "upload", "scope": "vdom",
    # #                                                             "file_content": base64.b64encode(
    # #                                                                 open(file, 'rb').read())})
    #
    # print(req)

def run_clone(device, cmd):
    req = device.session.post('https://' + device.ip + ':' + device.port + '/api/v2/' +
                              cmd.api + '/' + cmd.path + '?vdom=root&action=clone&nkey=' + cmd.name)
    check_req(req)


def run_config(device, cmd):
    # complex policy objects
    if 'firewall/policy' in cmd.path or 'firewall/local-in-policy' in cmd.path:
        req = device.session.post('https://' + device.ip + ':' + device.port + '/api/v2/' +
                                  cmd.api + '/' + cmd.path + '?vdom=root', data=cmd.body)
        check_req(req)
        return

    # device settings
    if cmd.name == '':
        logging.info('executor: updating device settings')
        req = device.session.put('https://' + device.ip + ':' + device.port + '/api/v2/' +
                                 cmd.api + '/' + cmd.path + '?vdom=root', data=cmd.body)
        check_req(req)
        # todo admin-sport anpassen
        return
    # policy settings
    if check_existence(device, cmd) == 404:
        logging.info('executor: object not exist, creating')
        req = device.session.post('https://' + device.ip + ':' + device.port + '/api/v2/' +
                                  cmd.api + '/' + cmd.path + '?vdom=root', data=cmd.body)
        check_req(req)
    elif check_existence(device, cmd) == 200:
        logging.info('executor: object exist, updating settings')
        req = device.session.put('https://' + device.ip + ':' + device.port + '/api/v2/' +
                                 cmd.api + '/' + cmd.path + '/' + cmd.name + '?vdom=root',
                                 data=cmd.body)
        check_req(req)


def collect_info(device):
    # COLLECT WIFI INFO
    if device.firmware[1:4] == '5.4' or device.firmware[1:4] == '5.6' or device.firmware[1:4] == '5.2':
        req = device.session.get(
            'https://' + device.ip + ':' + device.port + '/api/v2/monitor/wifi/managed_ap/select?vdom=root')
        if req.json()['status'] == 'success':
            rjson = req.json()
            if rjson['results'] == []:
                logging.info('executor: no accesspoints found')
                device.ap_name.append('None')
                device.ap_serial.append('None')
                device.ap_firmware.append('None')
                device.ssid.append('None')
            x = 0
            while x < len(rjson['results']):
                try:
                    device.ap_name.append(rjson['results'][x]['name'])
                except KeyError:
                    logging.warning('executor: collect ap name failed')
                    device.ap_name.append('error')
                try:
                    device.ap_firmware.append(rjson['results'][x]['os_version'])
                except KeyError:
                    logging.warning('executor: collect ap firmware failed')
                    device.ap_name.append('error')
                try:
                    device.ap_serial.append(rjson['results'][x]['serial'])
                except KeyError:
                    logging.warning('executor: collect ap serial failed')
                    device.ap_name.append('error')
                y = 0
                while y < len(rjson['results'][x]['ssid']):
                    z = 0
                    while z < len(rjson['results'][x]['ssid'][y]['list']):
                        device.ssid.append(rjson['results'][x]['ssid'][y]['list'][z])
                        z += 1
                    y += 1
                x += 1

    # COLLECT VDOM INFO
    if device.firmware[1:4] == '5.4':
        req = device.session.get(
            'https://' + device.ip + ':' + device.port + '/api/v2/monitor/system/csf-fgt-info/select?vdom=root')
        rjson = req.json()
        try:
            device.vdom_mode = rjson['results']['vdom_mode']
        except KeyError:
            logging.warning('executor: vdom check failed')
            device.vdom_mode = False
        if device.vdom_mode:
            vdom_check(device)

    # COLLECT FORTIGUARD INFO
    if device.firmware[1:4] == '5.2':
        req = device.session.get('https://' + device.ip + ':' + device.port + '/p/system/widget/license_info/')
        rjson = req.json()
        device.forticare = 'unknown'
        if rjson['antivirus']['expiry_date'] == '':
            device.fortiguard = 'expired'
        else:
            device.fortiguard = rjson['antivirus']['expiry_date']
        device.av_db = str(rjson['antivirus']['major_version'])
        device.av_db = device.av_db + '.00' + str(rjson['antivirus']['minor_version'])
    if device.firmware[1:4] == '5.4':
        req = device.session.get('https://' + device.ip + ':' + device.port + '/p/system/widget/license_info/')
        rjson = req.json()
        if rjson['forticare']['support'] == None: # todo maybe solve warning
            device.forticare = 'expired'
        else:
            device.forticare = rjson['forticare']['support']['hardware']['expiry_date']
        if rjson['antivirus']['expiry_date'] == '':
            device.fortiguard = 'expired'
        else:
            device.fortiguard = rjson['antivirus']['expiry_date']
        device.av_db = str(rjson['antivirus']['version'])
    if device.firmware[1:4] == '5.6':
        req = device.session.get('https://' + device.ip + ':' + device.port + '/api/v2/monitor/license/status/')
        rjson = req.json()
        if rjson['results']['forticare']['support'] == None:
            device.forticare = 'expired'
        else:
            device.forticare = rjson['results']['forticare']['support']['hardware']['expires']
            device.forticare = time.strftime("%d.%m.%Y", time.localtime(device.forticare))
        if rjson['results']['antivirus']['expires'] == '':
            device.fortiguard = 'expired'
        else:
            device.fortiguard = rjson['results']['antivirus']['expires']
            device.fortiguard = time.strftime("%d.%m.%Y", time.localtime(device.fortiguard))
        device.av_db = str(rjson['results']['antivirus']['version'])

    # COLLECT Local-in-policy
    if device.firmware[1:4] == '5.4':
        req = device.session.get('https://' + device.ip + ':' + device.port + '/api/v2/cmdb/firewall/local-in-policy')
        rjson = req.json()
        if rjson['results'] != []:
            device.local_in = True

def vdom_check(device):
    req = device.session.get(
        'https://' + device.ip + ':' + device.port + '/api/v2/monitor/system/vdom-resource/select?global=1')
    rjson = req.json()
    # print(rjson)


def fmg_check(device):
    req = device.session.get('https://' + device.ip + ':' + device.port + '/api/v2/monitor/system/fortimanager/status')
    rjson = req.json()
    if device.firmware[1:4] == '5.2':
        logging.warning('executor: fortimanager check not supported')
        device.fortimanager = 'unknown'
        return
    try:
        if rjson['results'] != {}:
            logging.info('executor: device is managed by fortimanager')
            device.fortimanager = True
            device.reason = 'managed by fortimanager'
        else:
            logging.debug('executor: device is not managed by fortimanager')
    except KeyError:
        logging.warning('executor: fortimanager check failed')


def perform_backup(device):
    req = device.session.get(
        'https://' + device.ip + ':' + device.port + '/api/v2/monitor/system/config/backup/download?scope=global')
    file = Config().backup_folder + '/' + req.headers.get('Content-Disposition').split('"')[1]
    file = file[:-10]
    file = file + '.conf'
    if req.headers.get('Content-Disposition'):
        open(file, 'wb').write(req.content)
        logging.debug('executor: config backup successful performed')
    else:
        logging.warning('executor: config backpu was not successful')


def check_existence(device, cmd):
    req = device.session.get('https://' + device.ip + ':' + device.port + '/api/v2/' +
                             cmd.api + '/' + cmd.path + '/' + cmd.name + '?vdom=root')
    return req.json()['http_status']

def check_req(request):
    try:
        rjson = request.json()
        if rjson["http_status"] == 200:
            logging.debug('executor: command successfull executed')
        else:
            logging.warning('executor: command not executed')
    except:
        logging.error('executor: unknown response for request')

def run_summary(total, failed_devices, skipped_devices = None):
    if skipped_devices == None:
        f = open('C:/BulkChanger/infocollector.log', 'a')
        f.write('\n*********************************')
        f.write('\n*\tTotal\tSuccess\t\tFailed\t*')
        f.write('\n*\t' + str(total) + '\t\t' + str(total - len(failed_devices)) + '\t\t' +
                '\t' + str(len(failed_devices)) + '\t\t*')
        f.write('\n*********************************\n\nPlease check the following devices manually:')
        i = 0
        while i < len(failed_devices):
            f.write('\n' + str(failed_devices[i].customer) + ',' + str(failed_devices[i].ip) + ',' + str(
                failed_devices[i].port) + '\tBecause: ' + str(failed_devices[i].reason))
            i += 1
        f.close()
    else:
        f = open('C:/BulkChanger/bulkchanger.log', 'a')
        f.write('\n*********************************************')
        f.write('\n*\tTotal\tSuccess\t\tFailed\tSkipped\t\t*')
        f.write('\n*\t' + str(total) + '\t\t' + str(total - len(failed_devices) - len(skipped_devices)) + '\t\t' +
                '\t' + str(len(failed_devices)) + '\t\t' + str(len(skipped_devices)) + '\t\t\t*')
        f.write('\n*********************************************\n\nPlease check the following devices manually:')
        i = 0
        while i < len(failed_devices):
            f.write('\n' + str(failed_devices[i].customer) + ',' + str(failed_devices[i].ip) + ',' + str(
                failed_devices[i].port) + '\tBecause: ' + str(failed_devices[i].reason))
            i += 1
        f.close()