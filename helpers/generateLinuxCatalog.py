import argparse
import cpe_utils
import json
import os
import re
from tqdm import tqdm
import vm_automation


def get_vm_server(config_file):
    if os.path.isfile(config_file):
        with open(config_file) as config_file_handle:
            config_map = json.load(config_file_handle)
            if config_map['HYPERVISOR_TYPE'].lower() == "esxi":
                vmServer = vm_automation.esxiServer.createFromConfig(config_map, 'esxi_automation.log')
                vmServer.connect()
            if config_map['HYPERVISOR_TYPE'].lower() == "workstation":
                vmServer = vm_automation.workstationServer(config_map, 'workstation_automation.log')
        return vmServer
    return None


def vm_as_cpe_string(vm_name):
    cpe_parts = {
        "ubuntu" : {
            "vendor" : "canonical",
            "product" : "ubuntu_linux",
            "version_pattern" : ".*ubuntu(\d+).*",
            "update" : ""
        },
        "fedora" : {
            "vendor" : "fedoraproject",
            "product" : "fedora",
            "version_pattern" : ".*fedora(\d+).*",
            "update" : ""
        },
        "centos" : {
            "vendor" : "centos",
            "product" : "centos",
            "version_pattern" : ".*centos(\d+).*",
            "update" : ""
        }
    }

    if "x64" in vm_name:
        arch = "x64"
    else:
        arch = "x86"
        
    vm_name = vm_name[vm_name.index("linux") + len("linux"):]
    os_pattern = re.compile("[a-z]+")
    os_name = os_pattern.match(vm_name)
    if os_name:
        os_name = os_name.group(0)
    else: exit

    if os_name in cpe_parts:
        version_pattern = re.compile(cpe_parts[os_name]['version_pattern'])
        v = version_pattern.match(vm_name)
        version = v.group(1)

        if "ubuntu" in os_name:
            version = version[:2] + "." + version[2:]

        cpe_str = ":".join(["cpe:/o", cpe_parts[os_name]['vendor'], cpe_parts[os_name]['product'],
                           version, cpe_parts[os_name]['update'], arch])

        return cpe_str
    else: exit

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keyword", help="VM search parameter")
    parser.add_argument("-o", "--output", help="output file location [defaults to catalog.json]")
    parser.add_argument("hypervisorConfig", help="json hypervisor config")

    args = parser.parse_args()

    prefix = args.keyword

    catalog_file = "catalog.json"
    if args.output is not None:
        catalog_file = args.output

    vm_server = get_vm_server(config_file=args.hypervisorConfig)
    if vm_server is None:
        print ("Failed to connect to VM environment")
        exit(1)

    vm_list = []
    vm_server.enumerateVms()
    for vm in vm_server.vmList:
        if prefix in vm.vmName:
            vm_list.append(vm.vmName)
    cpe_catalog = {}

    if os.path.isfile(catalog_file):
        with open(catalog_file) as catalog_handle:
            cpe_catalog = json.load(catalog_handle)

    for name in tqdm(vm_list):
        if "linux" in name.lower(): 
            cpe_str = vm_as_cpe_string(name.lower())
            if cpe_str:
                cpe = cpe_utils.CPE(cpe_str)
                vm_entry = {
                    'NAME': name,
                    'CPE': cpe_str,
                    'USERNAME': "vagrant",
                    'PASSWORD': "vagrant",
                    'OS': cpe.human()
                }
                cpe_catalog[vm_server.hostname + "_" + name] = vm_entry

    with open(catalog_file, "w") as catalog_handle:
        json.dump(cpe_catalog, catalog_handle, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
