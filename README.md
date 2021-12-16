# netbox-to-pyats

A tool for generating a testbed yaml from Netbox inventory

## Installation

1. Clone the repo to your local machine:
```shell
git clone https://github.com/jeremypng/netbox-to-pyats.git
```
2. Change into the cloned folder, create a virtual environment, activate the environment, and install the dependencies and cli tool
```shell
cd netbox-to-pyats
python3 -m venv venv
source venv/bin/activate
pip install .
```

## Configuration

You can use a .env file in the directory, your own environment varialbes, or the command line options to pass in the required variables.

1. To use the .env file copy the provided .env.sammple file to .env and modify to fit your environment.
```shell
NETBOX_TOKEN=48b983965445a9f5bc0fe861c788bd0e36e63ebf
NETBOX_HOST=demo.netbox.dev
NETBOX_PORT=443
NETBOX_SSL_VERIFY=True
TESTBED_USER=cisco
TESTBED_PASS=cisco
TESTBED_ENABLE=cisco
```
2. To use the command line options enter the following command to see all of the flags:
```shell
>netbox-to-testbed get-devices-by-tag --help
Usage: netbox-to-testbed get-devices-by-tag [OPTIONS]

Options:
  --tag TEXT                      [required]
  --debug / --no-debug
  --netbox-token TEXT
  --netbox-host TEXT
  --netbox-port TEXT
  --netbox-ssl-verify / --no-netbox-ssl-verify
  --testbed-user TEXT
  --testbed-pass TEXT
  --testbed-enable TEXT
  --help                          Show this message and exit.
```

## Modifications

1. If desired, you can modify the get_testbed_details() function to look for your own device models, roles, etc to add additional detail to the testbed details.

## Usage

1. Run the CLI command with the --tag option to select devices to put in the testbed file by the associated tag in Netbox (Note: Sample data taken from demo.netbox.dev):
```shell
❯ netbox-to-testbed get-devices-by-tag --tag Testbed-Devices
devices:
  ncsu-coreswitch1:
    connections:
      cli:
        ip: 1.1.1.1
        protocol: ssh
    os: nos
    platform: network
    type: device
  ncsu-coreswitch2:
    connections:
      cli:
        ip: 1.1.1.2
        protocol: ssh
    os: nos
    platform: network
    type: device
  ncsu117-distswitch1:
    connections:
      cli:
        ip: 1.1.1.3
        protocol: ssh
    os: nos
    platform: network
    type: device
  ncsu118-distswitch1:
    connections:
      cli:
        ip: 1.1.1.4
        protocol: ssh
    os: nos
    platform: network
    type: device
  ncsu128-distswitch1:
    connections:
      cli:
        ip: 1.1.1.5
        protocol: ssh
    os: nos
    platform: network
    type: device
testbed:
  credentials:
    default:
      password: cisco
      username: cisco
    enable:
      password: cisco
  name: Testbed-Devices
topology:
  ncsu-coreswitch1:
    interfaces:
      xe-0/0/0:
        link: cable-104
        type: ethernet
      xe-0/0/1:
        link: cable-105
        type: ethernet
      xe-0/0/2:
        link: cable-108
        type: ethernet
      xe-0/0/3:
        link: cable-109
        type: ethernet
      xe-0/0/4:
        link: cable-112
        type: ethernet
      xe-0/0/5:
        link: cable-113
        type: ethernet
  ncsu-coreswitch2:
    interfaces:
      xe-0/0/0:
        link: cable-106
        type: ethernet
      xe-0/0/1:
        link: cable-107
        type: ethernet
      xe-0/0/2:
        link: cable-110
        type: ethernet
      xe-0/0/3:
        link: cable-111
        type: ethernet
      xe-0/0/4:
        link: cable-114
        type: ethernet
      xe-0/0/5:
        link: cable-115
        type: ethernet
  ncsu117-distswitch1:
    interfaces:
      xe-0/0/0:
        link: cable-116
        type: ethernet
      xe-0/0/1:
        link: cable-117
        type: ethernet
      xe-0/0/2:
        link: cable-118
        type: ethernet
      xe-0/0/3:
        link: cable-119
        type: ethernet
  ncsu118-distswitch1:
    interfaces:
      xe-0/0/0:
        link: cable-120
        type: ethernet
      xe-0/0/1:
        link: cable-121
        type: ethernet
      xe-0/0/2:
        link: cable-122
        type: ethernet
      xe-0/0/3:
        link: cable-123
        type: ethernet
  ncsu128-distswitch1:
    interfaces:
      xe-0/0/0:
        link: cable-124
        type: ethernet
      xe-0/0/1:
        link: cable-125
        type: ethernet
      xe-0/0/2:
        link: cable-126
        type: ethernet
      xe-0/0/3:
        link: cable-127
        type: ethernet
```
