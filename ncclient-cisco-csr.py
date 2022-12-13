#!/usr/bin/env python

from argparse import ArgumentParser
from jinja2 import Environment, FileSystemLoader
from ncclient import manager
from ncclient.operations.rpc import RPCError
import xml.dom.minidom
import sys

IETF_INTERFACES  = '<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces" />'
IETF_ROUTING     = '<routing xmlns="urn:ietf:params:xml:ns:yang:ietf-routing" />'
CISCO_INTERFACES = '<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"> <interface /> </native>'

# Jinja environment
environment = Environment(loader=FileSystemLoader("templates/"))

# ============================================================================
def user_select_datastore():
    datastore = input("Running or Candidate? [R/c] ")
    # Running is default
    datastore = 'candidate' if datastore == 'c' else 'running'
    return datastore
    
# ============================================================================
def get_config(manager, datastore, filter=None):
    try:
        reply = manager.get_config(source=datastore, filter=filter).data_xml
        xml_minidom = xml.dom.minidom.parseString(reply)
        xml_pretty_str = xml_minidom.toprettyxml(indent="  ")
        return xml_pretty_str
    except RPCError as rpcerror:
        print(rpcerror)    

# ============================================================================
def edit_config(manager, datastore, config):
    try:
        manager.edit_config(target=datastore, config=config, test_option='test-then-set')
        print("edit-config --> OK")
    except RPCError as rpcerror:
        print("edit-config --> ERROR")
        print(rpcerror)


# ============================================================================
# ================== Functions called by the menu ============================
# ============================================================================

# ============================================================================
def print_config(manager):
    print("========== get-config ALL ========== ")
    datastore = user_select_datastore()
    # TODO print get_config with no filter


# ============================================================================
def print_config_ietf_if(manager):
    print("========== get-config / IETF_INTERFACES ========== ")
    datastore = user_select_datastore()
    # TODO print get_config with IETF_INTERFACES filter


# ============================================================================
def print_config_cisco_if(manager):
    print("========== get-config / CISCO_INTERFACE ========== ")
    datastore = user_select_datastore()
    # TODO print get_config with CISCO_INTERFACES filter


# ============================================================================
def lock(manager):
    print("========== lock ========== ")
    datastore = 'candidate'
    try:
        manager.lock(datastore)
        print("lock {} --> OK".format(datastore))
    except RPCError as rpcerror:
        print("lock {} --> ERROR".format(datastore))
        print(rpcerror)

# NOTE. If you unlock a non commited candidate datastore, then you lose
# your modifications on the candidate datastore
# ============================================================================
def unlock(manager):
    print("========== unlock ========== ")
    datastore = 'candidate'
    try:
        manager.unlock(datastore)
        print("unlock {} --> OK".format(datastore))
    except RPCError as rpcerror:
        print("unlock {} --> ERROR".format(datastore))
        print(rpcerror)

# ============================================================================
def create_delete_if(manager):
    print("========== edit-config create/delete interface ========== ")
    op = input("Create or Delete? [C/d] ")
    # Create is default
    op = 'delete' if op == 'd' else 'create'
    iface_id = input("Interface number? ")
    
    template = environment.get_template("edit-interface-base.jinja")
    config = template.render(operation=op, ifid=iface_id)
    edit_config(manager, 'candidate', config)

# ============================================================================
def enable_disable_if(manager):
    print("========== edit-config enable/disable interface ========== ")
    iface_id = input("Interface number? ")
    enabled = input("Enable or Disable? [E/d] ")
    enabled = 'false' if enabled == 'd' else 'true'
 
    template = environment.get_template("edit-interface-enable.jinja")
    config = template.render(ifid=iface_id, enable=enabled)
    edit_config(manager, 'candidate', config)   

# ============================================================================
def set_vlan(manager):
    print("========== edit-config set VLAN on interface ========== ")
    ifid = input("Interface number? ")
    vlan = input("VLAN number? ")
    
    template = environment.get_template("edit-interface-vlan.jinja")
    config = template.render(ifid=ifid, vlan_id=vlan)
    edit_config(manager, 'candidate', config)
    
# ============================================================================
def set_ip_addr(manager):
    print("========== edit-config IP addr on interface ========== ")
    ifid = input("Interface number? ")
    ip = input("IPv4 addr? ")
    mask = input("Netmask? ")
    op = input("Create (c) ou delete (d)? ")
    op = 'create' if op == 'c' else 'delete'
    
    template = environment.get_template("edit-interface-ip-addr.jinja")
    config = template.render(ifid=ifid, ip=ip, netmask=mask, operation=op)
    edit_config(manager, 'candidate', config)

# ============================================================================
def discard_changes(manager):
    print("========== discard changes on candidate ========== ")
    reply = manager.discard_changes()
    if reply.ok:
        print("discard changes --> OK")
    else:
        print("discard changes --> ERROR")
        print(reply.error.xml)

# ============================================================================
def validate_candidate(manager):
    print("========== validate candidate ========== ")
    reply = manager.validate("candidate")
    if reply.ok:
        print("validate --> OK")
    else:
        print("validate --> ERROR")
        print(reply.error.xml)

# ============================================================================
def commit(manager):
    print("========== commit ========== ")
    try:
        reply = manager.commit()
        if reply.ok:
            print("commit --> OK")
        else:
            print("commit --> ERROR")
            print(reply.error.xml)
    except RPCError as rpcerror:
        print("commit --> ERROR")
        print(rpcerror)

# ============================================================================
# <commit>
#     <confirmed/>
#     <confirm-timeout>60</confirm-timeout>
# </commit>
def commit_confirmed(manager):
    print("========== commit with confirmed option (timeout 1min) ========== ")
    # TODO confirmed-commit operation


# ============================================================================
# ================================== MENU ====================================
# ============================================================================

def print_invalid_choice():
    print("Invalid choice!")

def print_menu():
    print("******************** Menu ********************")
    print(" 1) get-config ALL")
    print(" 2) get-config filter ietf-interfaces")
    print(" 3) get-config filter cisco-interface\n")
    
    print("10) lock candidate")
    print("11) unlock candidate\n")

    print("20) edit-config create/delete interface")
    print("21) edit-config enable/disable interface")
    print("22) edit-config set VLAN")
    print("23) edit-config set IP addr\n")
    
    print("30) discard changes")
    print("31) validate candidate")
    print("32) commit (candidate --> running)")
    print("33) commit confirmed (candidate --> running)")
    print(" 0) exit\n")
    print("Your choice : ", end="", flush=True)

def switcher(arg, manager):
    dict = {
        1: print_config,
        2: print_config_ietf_if,
        3: print_config_cisco_if,
        10: lock,
        11: unlock,
        20: create_delete_if,
        21: enable_disable_if,
        22: set_vlan,
        23: set_ip_addr,
        30: discard_changes,
        31: validate_candidate,
        32: commit,
        33: commit_confirmed
    }
    # Get the function from switcher dictionary
    func = dict.get(arg, "invalid choice")
    # Execute function
    if type(func)==str:
        print("Invalid choice")
    else:
        func(manager)

# ============================================================================
# ================================ MAIN CODE =================================
# ============================================================================
if __name__ == '__main__':

    parser = ArgumentParser(description='Select options.')
    parser.add_argument('--host', type=str, required=True,
                        help="device IP address")
    parser.add_argument('--port', type=int, default=830,
                        help="non-default port")
    parser.add_argument('-u', '--username', type=str, default='etu',
                        help="username")
    parser.add_argument('-p', '--password', type=str, default='-etu-',
                        help="password")

    args = parser.parse_args()

    print("Trying to connect to NETCONF serveur via SSH...")
    m =  manager.connect(host=args.host,
                         port=args.port,
                         username=args.username,
                         password=args.password,
                         hostkey_verify=False,
                         device_params={'name':'iosxe'})

    print("SSH connection to NETCONF serveur --> OK.")
    # print("NETCONF serveur capabilities:")
    # for c in m.server_capabilities:
    #     print(c)
    
    try:
        end=False
        while not end:
            print_menu()
            try:
                choice = int(sys.stdin.readline())
                # print("you chose {}".format(choice))
                if (choice==0):
                    end=True
                else:
                    switcher(choice, m)
            except ValueError:
                print("Enter a menu item!")
    finally:
        m.close_session()
        print("NETCONF session closed.")
