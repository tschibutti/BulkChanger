import fileinput
import logging
import os
import re

from classes.command import Command
from shutil import copyfile


def convert_command(input_file, input_folder) -> []:
    cmd = []
    cpath = ''
    cbody = ''
    capi = ''
    caction = ''
    cname = ''
    inner_config = False
    inner_inner_config = False
    inner_edit = False
    outer_edit = False
    rename_flag = False
    clone_flag = False

    source = input_folder + '/' + input_file

    if not os.path.isfile(source):
        logging.error('command: file not found')
        return

    for line in fileinput.input(source):
        line = re.sub(r'"', '', line)
        if '#' in line:
            # skip comments
            continue
        if 'config' in line:
            line = re.findall(r'\S+', line)
            if line.__len__() == 2:
                if inner_config:
                    inner_inner_config = True
                    if cbody == '':
                        cbody = '{'
                    cbody = cbody + ',"' + line[1] + '":[{'
                else:
                    inner_config = True
                    if cbody == '':
                        cbody = '{'
                    cbody = cbody + ',"' + line[1] + '":{'
            else:
                for entry in line:
                    if 'config' in entry:
                        capi = 'cmdb'
                        continue
                    if cpath == '':
                        cpath = entry
                    else:
                        cpath = cpath + '/'
                        cpath = cpath + entry
                if 'vpn/ssl' in cpath:
                    cpath = re.sub(r'vpn/ssl', 'vpn.ssl', cpath)
                    cpath = re.sub(r'/web/portal', '.web/portal', cpath)
                if 'vpn/certificate' in cpath:
                    cpath = re.sub(r'vpn/certificate', 'vpn.certificate', cpath)
                if 'firewall/service' in cpath:
                    cpath = re.sub(r'firewall/service', 'firewall.service', cpath)
                if 'application/casi' in cpath:
                    cpath = re.sub(r'application/casi', 'application.casi', cpath)
        if 'delete' in line:
            cname = line.split()[1]
            caction = 'delete'
            cmd.append(Command(cpath, cbody, capi, caction, cname))
            cname = ''
            caction = ''
        if 'rename' in line:
            rename_flag = True
            cname = cname + line.split()[3]
            caction = 'rename'
            cpath_add = '/' + str(line.split()[1])
            cpath = cpath + cpath_add
            cbody = '{"name":"' + str(cname) + '"}'
            if 'webfilter/ftgd-local-cat' in cpath:
                cbody = re.sub(r'name', 'desc', cbody)
            cmd.append(Command(cpath, cbody, capi, caction, cname))
            cname = ''
            caction = ''
            cpath = re.sub(str(cpath_add), '', cpath)
        if 'clone' in line:
            clone_flag = True
            cname = cname + line.split()[3]
            caction = 'clone'
            cpath_add = '/' + str(line.split()[1])
            cpath = cpath + cpath_add
            cmd.append(Command(cpath, cbody, capi, caction, cname))
            cname = ''
            caction = ''
            cpath = re.sub(str(cpath_add), '', cpath)
        if 'show' in line:
            line = re.findall(r"[\w']+", line)
            for entry in line:
                if 'show' in entry:
                    capi = 'monitor'
                    continue
                if cpath == '':
                    cpath = entry
                else:
                    cpath = cpath + '/'
                    cpath = cpath + entry
        if 'edit' in line:
            rename_flag = False
            clone_flag = False
            if outer_edit:
                inner_edit = True
                if 'webfilter/profile' in cpath:
                    second = line.split()[1]
                    cbody = cbody + ',"id":"' + str(second) + '"'
                else:
                    cbody = re.sub(r'":{', '":[{', cbody)
            else:
                if not ('firewall/policy' in cpath or 'firewall/local-in-policy' in cpath):
                    cbody = '{"name":"' + str(line.split()[1]) + '"'
                cname = line.split()[1]
                caction = 'edit'
                outer_edit = True
        if ('set' in line) and not ('unset' in line):
            if cbody == '':
                cbody = '{'
            if 'member' in line or 'srcintf' in line or 'dstintf' in line or 'srcaddr' in line or 'dstaddr' in line \
                    or 'service' in line or 'tunnel-ip-pools' in line \
                    or ('category' in line and 'category-override' not in line and 'webfilter' not in cpath) \
                    or 'source-interface' in line \
                    or 'source-address' in line or 'interface' in line or 'source-address6' in line:
                # complex object
                first = line.split()[1]
                second = line.split(first)[1]
                second = second[1:]
                # split all entries to an array
                second = re.findall(r'\S+', second)
                third = ''
                for entry in second:
                    third = third + '{"name":"' + str(entry) + '"},'
                    # special names
                    if 'system/zone' in cpath:
                        third = re.sub(r'"name"', '"interface-name"', third)
                    if 'application/list' in cpath:
                        third = re.sub(r'"name"', '"id"', third)
                cbody = cbody + ',"' + str(first) + '":[' + str(third) + ']'
            elif 'vpn.certificate/ca' in cpath:
                # certificate upload
                caction = 'upload'
                capi = 'monitor'
                destination = input_folder + '/ca.cer'
                copyfile(source, destination)
                f = open(destination, 'r')
                content = f.readlines()
                f.close()
                f = open(destination, 'w')
                need_content = False
                for subline in content:
                    if 'END CERTIFICATE' in subline:
                        need_content = False
                        subline = re.sub(r'"', '', subline)
                        f.write(subline)
                    if need_content:
                        f.write(subline)
                    if 'BEGIN CERTIFICATE' in subline:
                        need_content = True
                        subline = subline.split('"')[1]
                        f.write(subline)
                f.close()
            else:
                # simple object
                first = line.split()[1]
                second = line.split(first)[1]
                second = second[1:]
                cbody = cbody + ',"' + str(first) + '":"' + str(second) + '"'
                if 'webfilter/ftgd-local-cat' in cpath:
                    cbody = re.sub(r'name', 'desc', cbody)
        if 'unset' in line:
            if cbody == '':
                cbody = '{'
            first = line.split()[1]
            cbody = cbody + ',"' + str(first) + '":null'
        if 'next' in line:
            cbody = cbody + '}'
            cbody = re.sub(r'\n+', '', cbody)
            cbody = re.sub(r',]', ']', cbody)
            cbody = re.sub(r'{,', '{', cbody)
            cbody = re.sub(r',{}', '', cbody)
            if inner_edit:
                cbody = cbody + ',{'
                inner_edit = False
            else:
                if 'firewall/policy' in cpath or 'firewall/local-in-policy' in cpath:# or 'webfilter/profile' in cpath:
                    cbody = '{\'json\':' + cbody + '}'
                cmd.append(Command(cpath, cbody, capi, caction, cname))
                if 'null' in cbody:
                    # "unset" command needs to be executed twice
                    cmd.append(Command(cpath, cbody, capi, caction, cname))
                cbody = ''
                cname = ''
                caction = ''
                outer_edit = False
        if 'end' in line:
            if inner_inner_config:
                inner_inner_config = False
                if 'webfilter/profile' in cpath and 'filters' in cbody:
                    cbody = cbody + '}]'
            elif inner_config:
                inner_config = False
                cbody = cbody + '}'
                if 'application/list' in cpath or 'ips/sensor' in cpath:
                    cbody = cbody + ']'
            else:
                if 'null' in cbody:
                    # "unset" command need to be executed twice
                    cmd.append(Command(cpath, cbody, capi, caction, cname))
                elif rename_flag:
                    rename_flag = False
                elif clone_flag:
                    clone_flag = False
                elif cbody != '':
                    cbody = cbody + '}'
                    cbody = re.sub(r'\n+', '', cbody)
                    cbody = re.sub(r',]', ']', cbody)
                    cbody = re.sub(r'{,', '{', cbody)
                    cmd.append(Command(cpath, cbody, capi, caction, cname))
                cpath = ''
                cbody = ''
    if not cmd:
        logging.error('command: error, abort execution')
        print('error: check log file for details')
        exit()
    logging.info('command: converted cli command to rest api command')
    logging.info('command: parsed ' + str(len(cmd)) + ' commands')
    return cmd


def print_command(cmd):
    j = 0
    while j < len(cmd):
        print('commands: ' + cmd[j].body)
        j = j + 1
