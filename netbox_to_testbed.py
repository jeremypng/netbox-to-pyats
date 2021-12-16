import click
import dotenv
from rich import print
from rich.console import Console
console = Console()
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
NETBOX_PORT = os.getenv("NETBOX_PORT", 443)
NETBOX_SSL_VERIFY = eval(os.getenv("NETBOX_SSL_VERIFY", "True"))
TESTBED_USER = os.getenv("TESTBED_USER")
TESTBED_PASS = os.getenv("TESTBED_PASS")
TESTBED_ENABLE = os.getenv("TESTBED_ENABLE")

DEBUG = False

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
    return {
        "os": "nos",
        "platform": "network",
        "type": "device"
    }

        
@click.command("get-devices-by-tag")
@click.option("--tag", required=True)
@click.option("--debug/--no-debug", required=False, default=False)
@click.option("--netbox-token", required=False, default=NETBOX_TOKEN)
@click.option("--netbox-host", required=False, default=NETBOX_HOST)
@click.option("--netbox-port", required=False, default=NETBOX_PORT)
@click.option("--netbox-ssl-verify/--no-netbox-ssl-verify", required=False, default=NETBOX_SSL_VERIFY)
@click.option("--testbed-user", required=False, default=TESTBED_USER)
@click.option("--testbed-pass", required=False, default=TESTBED_PASS)
@click.option("--testbed-enable", required=False, default=TESTBED_ENABLE)
def get_devices_by_tag(tag,debug,netbox_token,netbox_host,netbox_port,netbox_ssl_verify,testbed_user,testbed_pass,testbed_enable):
    global DEBUG
    DEBUG=debug

    if not netbox_token or len(netbox_token) == 0:
        print("[bold][red]Netbox API token not defined. Add environment variable NETBOX_TOKEN or use --netbox-token command line option.[/red][/bold]")
        exit()
    if not netbox_host or len(netbox_host) == 0:
        print("[bold][red]Netbox host not defined. Add environment variable NETBOX_HOST or use --netbox-host command line option.[/red][/bold]")
        exit()

    nb = pynetbox.api(f"https://{netbox_host}:{netbox_port}",token=netbox_token)
    nb_session = requests.session()
    nb_session.verify=netbox_ssl_verify
    nb.http_session=nb_session
   
    device_list=nb.dcim.devices.filter(tag=tag.lower())
    testbed_testbed = {
        "name": tag,
        "credentials": {
            "default": {
                "username": testbed_user,
                "password": testbed_pass
            },
            "enable": {
                "password": testbed_enable
            }
        }
    }
    testbed_devices = {}
    testbed_topology = {}
    try:
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
            for interface in nb.dcim.interfaces.filter(device=device.name):
                if interface.cable:
                    interface.connected_endpoint.device.full_details()
                    #if interface.connected_endpoint.device.device_type.manufacturer.slug == "cisco":
                    if device.name not in testbed_topology.keys():
                        testbed_topology[device.name] = { "interfaces": {} }

                    testbed_topology[device.name]["interfaces"][interface.name] = {
                        "link": f"cable-{interface.cable.id}",
                        "type": "ethernet"
                    }
                    if nb.ipam.ip_addresses.get(device=device.name,interface=interface.name):
                        testbed_topology[device.name]["interfaces"][interface.name]["ipv4"] = nb.ipam.ip_addresses.get(device=device.name,interface=interface.name).address


    except Exception as e:
        print("[bold][red]Error retrieving device list from Netbox[/red][/bold]")
        print_traceback = input("Print traceback? [Y/N]: ")
        if print_traceback == "Y":
            console.print_exception(show_locals=True)
        exit()
 
    testbed = {
            "testbed": testbed_testbed,
            "devices": testbed_devices,
            "topology": testbed_topology
    }
    testbed_yaml = yaml.dump(testbed)
    print(testbed_yaml)
        
@click.group()
def cli():
    """A tool for generating a testbed yaml from Netbox inventory"""
    pass

cli.add_command(get_devices_by_tag)

if __name__ == "__main__":
    cli()
