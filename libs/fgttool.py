#!/usr/bin/env python
import requests
import argparse
import sys
import json
from pprint import pprint


class FGT(object):
    """
    Base class to send GET/POST/PUT/DELETE request to FGT
      . All requests are from the same session initiated by each login
    """
    def __init__(self, host):
        self.host = host
        self.url_prefix = "https://" + self.host

    def update_csrf(self):
        # retrieve server csrf and update session's headers
        for cookie in self.session.cookies:
            if cookie.name == "ccsrftoken":
                csrftoken = cookie.value[1:-1]  # token stored as a list
                self.session.headers.update({"X-CSRFTOKEN": csrftoken})

    def login(self, name="admin", key="", csrf=True):
        # close existing session if any
        self.logout()

        # start fresh new session
        self.session = requests.session()
        url = self.url_prefix + "/logincheck"
        try:
            res = self.session.post(
                url,
                data="username=" + name + "&secretkey=" + key,
                verify=False)
        except requests.exceptions.RequestException as e:
            print(e)
            print("LOGIN failed")
            exit()

        if res.text.find("error") != -1:
            # found some error in the response, consider login failed
            print("LOGIN failed")
            return False

        # update session's csrftoken
        if csrf:
            self.update_csrf()
        return True

    def logout(self):
        if hasattr(self, "session"):
            url = self.url_prefix + "/logout"
            self.session.post(url)

    def get(self, url, **options):
        url = self.url_prefix + url
        try:
            res = self.session.get(
                url,
                params=options.get("params"))
        except requests.exceptions.RequestException as e:
            print(e)
            exit()
        return res

    def post(self, url, override=None, **options):
        url = self.url_prefix + url
        data = options.get("data") if options.get("data") else None

        # override session's HTTP method if needed
        if override:
            self.session.headers.update({"X-HTTP-Method-Override": override})
        try:
            res = self.session.post(
                url,
                params=options.get("params"),
                data=json.dumps(data),
                files=options.get("files"))
        except requests.exceptions.RequestException as e:
            print(e)
            exit()

        # restore original session
        if override:
            del self.session.headers["X-HTTP-Method-Override"]
        return res

    def put(self, url, **options):
        url = self.url_prefix + url
        data = options.get("data") if options.get("data") else None
        try:
            res = self.session.put(
                url,
                params=options.get("params"),
                data=json.dumps(data),
                files=options.get("files"))
        except requests.exceptions.RequestException as e:
            print(e)
            exit()
        return res

    def delete(self, url, **options):
        url = self.url_prefix + url
        try:
            res = self.session.delete(
                url,
                params=options.get("params"))
        except requests.exceptions.RequestException as e:
            print(e)
            exit()
        return res

# function to process command arguments
def process_commands():
    # inititate command parsers
    tool = argparse.ArgumentParser(description="Python tool to interact with FGT via rest api")
    commands = tool.add_subparsers(title="commands")

    # common arguments
    tool.add_argument("-v", "--verbose", help="increase output verbosity",
                      action="store_true")
    tool.add_argument("-d", "--dryrun", help="dryrun the command without committing any changes",
                      action="store_true")
    tool.add_argument('--version', help="show version number and exit", action='version', version='%(prog)s 0.1')

    # get command (get firewall.address.test --vdom root)
    command_get = commands.add_parser("get", help="get object or table")
    command_get.add_argument("resource", help="full path to the object or table, ie. firewall/address or firewall/address/test or firewall.service/custom/test")
    command_get.add_argument("-V", "--vdom", default="root", help="vdom of the resource, default is root")
    command_get.set_defaults(func=get_command)

    # delete command (delete firewall.address.test --vdom root)
    command_delete = commands.add_parser("delete", help="delete object or table")
    command_delete.add_argument("resource", help="full path to the object or table, ie. firewall/address or firewall/address/test or firewall.service/custom/test")
    command_delete.add_argument("-V", "--vdom", default="root", help="vdom of the resource, default is root")
    command_delete.set_defaults(func=delete_command)

    # create command (create firewall.address.test {"comment":"test"} --vdom root)
    command_create = commands.add_parser("create", help="create object")
    command_create.add_argument("resource", help="full path to the object or table, ie. firewall/address or firewall/address/test or firewall.service/custom/test")
    command_create.add_argument("-D", "--data", type=json.loads, default=None, help="object data in string format '{\"comment\":\"test\"}'")
    command_create.add_argument("-V", "--vdom", default="root", help="vdom of the resource, default is root")
    command_create.set_defaults(func=create_command)

    # edit command (create firewall.address.test {"comment":"test"} --vdom root)
    command_edit = commands.add_parser("edit", help="edit object")
    command_edit.add_argument("resource", help="full path to the object or table, ie. firewall/address or firewall/address/test or firewall.service/custom/test")
    command_edit.add_argument("-D", "--data", type=json.loads, default=None, help="object data in string format '{\"comment\":\"test\"}'")
    command_edit.add_argument("-V", "--vdom", default="root", help="vdom of the resource, default is root")
    command_edit.set_defaults(func=edit_command)

    # copy command
    command_copy = commands.add_parser("copy", help="copy object or table from one vdom to another including referenced objects")
    command_copy.add_argument("resource", help="full path to the object or table, ie. firewall/address or firewall/address/test or firewall.service/custom/test")
    command_copy.add_argument("oldvdom", help="vdom of the original resource, ie. root")
    command_copy.add_argument("newvdom", help="vdom of the new resource, ie. vdom1")
    command_copy.set_defaults(func=copy_command)

    # import command (import firewall.address.test --vdom root --file path/to/file)
    # export command (export firewall.address.test --vdom root --file path/to/file)

    # process commands
    args = tool.parse_args()
    args.func(args)

# function to retrieve resource
def get_command(args):
    # parse URI path
    path, name, mkey = parse_resource(args.resource)
    print("get", path, name, mkey, "in vdom", args.vdom)

    # only send request if not dryrun
    if not args.dryrun:
        # retrieve resource
        res = fgt.get(
            url="/api/v2/cmdb/" + path + "/" + name + "/" + mkey,
            params={"vdom": args.vdom})
        check_response(res, True)  # always print JSON response for get

# function to delete resource
def delete_command(args):
    # parse URI path
    path, name, mkey = parse_resource(args.resource)
    print("delete", path, name, mkey, "in vdom", args.vdom)

    # only send request if not dryrun
    if not args.dryrun:
        # delete resource
        res = fgt.delete(
            url="/api/v2/cmdb/" + path + "/" + name + "/" + mkey,
            params={"vdom": args.vdom})
        check_response(res, args.verbose)

# function to create resource
def create_command(args):
    # parse URI path
    path, name, mkey = parse_resource(args.resource)
    print("create", path, name, mkey, "in vdom", args.vdom)

    # add mkey to resource data
    # TODO: mkey should be retrieve from schema
    if args.data:
        args.data["name"] = mkey
    else:
        args.data = {"name":mkey}

    # only send request if not dryrun
    if not args.dryrun:
        # create resource
        res = fgt.post(
            url="/api/v2/cmdb/" + path + "/" + name,
            params={"vdom": args.vdom},
            data=args.data)
        check_response(res, args.verbose)

# function to edit resource
def edit_command(args):
    # parse URI path
    path, name, mkey = parse_resource(args.resource)
    print("edit", path, name, mkey, "in vdom", args.vdom)

    # only send request if not dryrun
    if not args.dryrun:
        # edit resource
        res = fgt.put(
            url="/api/v2/cmdb/" + path + "/" + name + "/" + mkey,
            params={"vdom": args.vdom},
            data=args.data)
        check_response(res, args.verbose)

# function to copy resource (recursive)
def copy_command(args):
    # parse URI path
    path, name, mkey = parse_resource(args.resource)
    print("copy", path, name, mkey, "from", args.oldvdom, "to", args.newvdom)

    # retrieve resource in old vdom
    res = fgt.get(
        url="/api/v2/cmdb/" + path + "/" + name + "/" + mkey,
        params={"vdom": args.oldvdom,
                "skip": 1,  # skip inapplicable fields
                "datasource": 1})  # need datasource for deep copy
    rjson = get_json(res)
    if args.verbose: pprint(rjson)

    # skip if cannot get json result
    if not rjson or "results" not in rjson:
        print("fail to retrieve resource", args.resource, "in vdom", args.oldvdom)
        return

    # retrieve resource in new vdom
    res = fgt.get(
        url="/api/v2/cmdb/" + path + "/" + name + "/" + mkey,
        params={"vdom": args.newvdom,
                "skip": 1,
                "datasource": 1})
    new = get_json(res)
    if args.verbose: pprint(new)

    # skip if resource already exists in new vdom
    if new["http_status"] != 404 and mkey is not "":
        print(args.resource, "already existed in vdom", args.newvdom)
        return

    # copy all objects in table
    for data in rjson["results"]:
        # TODO: mkey should be retrieve from schema
        mkey = data["name"]

        # copy all object attributes
        for key, value in data.items():
            # recursively copy all non-empty referenced objects
            if value and type(value) is list:
                # copy all referenced objects
                for item in value:
                    # only copy object that has valid datasource
                    if "datasource" in item:
                        child_path = item["datasource"].replace(".", "/")
                        # handle special case like firewall.service/custom
                        if len(child_path.split("/")) > 2:
                            child_path = child_path.replace("/", ".", 1)
                        child_resource = child_path + "/" + item["name"]
                        args.resource = child_resource
                        copy_command(args)

        # only send request if not dryrun
        if not args.dryrun:
            # create resource in another vdom
            res = fgt.post(
                url="/api/v2/cmdb/" + path + "/" + name,
                params={'vdom': args.newvdom},
                data=(data))
            check_response(res, args.verbose)

# function to parse resource path, name and mkey
def parse_resource(resource):
    obj_list = resource.split('/')
    if len(obj_list) == 2:
        path = obj_list[0]
        name = obj_list[1]
        mkey = ""
    elif len(obj_list) == 3:
        path = obj_list[0]
        name = obj_list[1]
        mkey = obj_list[2]
    else:
        print("Invalid resource", resource, "please use / to separate path/name/mkey")
        exit()
    return (path, name, mkey)

# function to retrieve json data from HTTP response (return False if fails)
def get_json(response):
    try:
        rjson = response.json()
    except UnicodeDecodeError as e:
        print("Cannot decode json data in HTTP response")
        return False
    except:
        e = sys.exc_info()[0]
        print(e)
        return False
    else:
        return rjson

# function to check response
def check_response(res, verbose) -> str:
    rjson = get_json(res)
    if verbose: pprint(rjson)
    if not rjson:
        print("fail to retrieve JSON response")
    else:
        status = rjson["http_status"]
        if status == 200:
            if verbose: print("200 successful request")
            return '200'
        elif status == 400:
            if verbose: print("400 Invalid request format")
            return '400'
        elif status == 403:
            if verbose: print("403 Permission denied")
            return '403'
        elif status == 404:
            if verbose: print("404 None existing resource")
            return '404'
        elif status == 405:
            if verbose: print("405 Unsupported method")
            return '405'
        elif status == 424:
            if verbose: print("424 Dependency error")
            return '424'
        elif status == 500:
            if verbose: print("500 Internal server error")
            return '500'
        else:
            if verbose: print(status, "Unknown error")
            return '000'


###############################################################################
if __name__ == "__main__":
    # initilize fgt connection
    fgt_ip = "1.1.1.1"
    fgt = FGT(fgt_ip)
    fgt.login("admin","")

    # parse commandline arguments
    process_commands()

    # always logout after testing is done
    fgt.logout()
