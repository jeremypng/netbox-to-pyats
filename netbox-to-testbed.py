import click
import dotenv
from rich import print
from dotenv import load_dotenv
load_dotenv()
import os
import pynetbox
import requests
import re
import yaml
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
NETBOX_HOST = os.getenv("NETBOX_HOST")
NETBOX_PORT = os.getenv("NETBOX_PORT")
TESTBED_USER = os.getenv("TESTBED_USER")
TESTBED_PASS = os.getenv("TESTBED_PASS")
TESTBED_ENABLE = os.getenv("TESTBED_ENABLE")

DEBUG = False

nb = pynetbox.api(f"https://{NETBOX_HOST}:{NETBOX_PORT}",token=NETBOX_TOKEN)
nb_session = requests.session()
nb_session.verify=False
nb.http_session=nb_session


def get_testbed_details(nb_device):
    if DEBUG:
        print(f"DEBUG: Device={nb_device.name}, Device Model={nb_device.device_type.model}")
    if nb_device.device_type.model.lower().startswith("ie-3"):
        return {
                "os": "iosxe",
                "platform": "cat3k",
                "type": "switch"
        }
    if nb_device.device_type.model.lower().startswith("ir1101"):
        return {
                "os": "iosxe",
                "platform": "sdwan",
                "type": "router"
        }

        

@click.command("get-devices-by-tag")
@click.option("--tag", required=True)
@click.option("--debug/--no-debug", required=False, default=False)
def get_devices_by_tag(tag,debug):
    global DEBUG
    DEBUG=debug
    device_list=nb.dcim.devices.filter(tag=tag.lower())
    testbed_testbed = {
        "name": tag,
        "credentials": {
            "default": {
                "username": "%ENV{TESTBED_USER}",
                "password": "%ENV{TESTBED_PASS}"
            },
            "enable": {
                "password": "%ENV{TESTBED_ENABLE}"
            }
        }
    }
    testbed_devices = {}
    testbed_topology = {}
    for device in device_list:
        device.full_details()
        details = get_testbed_details(device)
        testbed_devices[device.name] = {
            "type": details["type"],
            "os": details["os"],
            "platform": details["platform"],
            "connections": {
                "cli": {
                    "protocol": "ssh",
                    "ip": re.sub("\/.*$", "", device.primary_ip4.address)
                }
            }
        }
        if device.config_context.get("pyats_custom"):
            testbed_devices[device.name]["custom"] = device.config_context["pyats_custom"]
        for interface in nb.dcim.interfaces.filter(device=device.name):
            if interface.cable:
                interface.connected_endpoint.device.full_details()
                if interface.connected_endpoint.device.device_type.manufacturer.slug == "cisco":
                    if device.name not in testbed_topology.keys():
                        testbed_topology[device.name] = { "interfaces": {} }

                    testbed_topology[device.name]["interfaces"][interface.name] = {
                        "ipv4": nb.ipam.ip_addresses.get(device=device.name,interface=interface.name).address,
                        "link": f"cable-{interface.cable.id}",
                        "type": "ethernet"
                    }

            
    testbed = {
            "testbed": testbed_testbed,
            "devices": testbed_devices,
            "topology": testbed_topology
    }
    testbed_yaml = yaml.dump(testbed)
    print(testbed_yaml)
        
    


   
@click.command("test-netbox")
def test_netbox():
    device_list = nb.dcim.devices.all()
    for device in device_list:
        print(device)


@click.group()
def cli():
    """A tool for generating a testbed yaml from Netbox inventory"""
    pass

cli.add_command(test_netbox)
cli.add_command(get_devices_by_tag)

if __name__ == "__main__":
    cli()
