#!/usr/bin/env python

from argparse import ArgumentParser
from ncclient import manager
import xml.dom.minidom

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
                         device_params={'name':"iosxe"})

    print("SSH connection to NETCONF serveur --> OK.")
    print("NETCONF serveur capabilities:")
    for c in m.server_capabilities:
        print(c)

    # IETF interfaces filter
    interfaces_filter = """
        <filter>
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces" />
        </filter>
        """

    # IETF routing filter
    # routing_filter = """
    #    <filter>
    #        <routing xmlns="urn:ietf:params:xml:ns:yang:ietf-routing" />
    #    </filter>
    #    """

    # NETCONF get-config
    c = m.get_config('running', interfaces_filter).data_xml

    # Pretty print the XML reply
    xml_dom = xml.dom.minidom.parseString(c)
    print(xml_dom.toprettyxml(indent = "  " ))

    # Close NETCONF session
    m.close_session()
    print("NETCONF session closed.")
