from vmanage.api.authentication import Authentication
from vmanage.api.device import Device
import json
import os

def create_file(json_to_write):
    f = open("status.json", "w")
    f.write(json_to_write)
    f.close()
    return


vmanage_host = os.environ['VMANAGE_HOST']
vmanage_username = os.environ['VMANAGE_USERNAME']
vmanage_password = os.environ['VMANAGE_PASSWORD']

auth = Authentication(vmanage_host, vmanage_username, vmanage_password).login()

vmanage_devices = Device(auth, vmanage_host)

device_status_list = vmanage_devices.get_device_status_list()

# Create a new status dictionary key is system-ip - value is "reachable" or "dormant".

status_dict = {}

# Take the output of the API and extract system-ip and reachability information

for d in device_status_list:

    if d['reachability'] == "reachable":
        status_dict[d['system-ip']] = d['reachability']
    else:
        # If not reachable - marking as dormant as potentially unused device
        status_dict[d['system-ip']] = "dormant"

create_file(json.dumps(status_dict, indent=2))
print(status_dict)

