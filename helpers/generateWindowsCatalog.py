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
    version_pattern = re.compile(".*Win(\d+).*")
    v = version_pattern.match(vm_name)
    if v is None:
        version = "xp"
    else:
        version = v.group(1)
        if len(version) > 1 and version.startswith("8"):
            version = "8.1"

    p = re.compile(".*(r2).*")
    m = p.match(vm_name)
    if m is None:
        revision = None
    else:
        revision = "r2"

    p = re.compile(".*(x86|x64).*")
    m = p.match(vm_name)
    if m is None:
        arch = "x86"
    else:
        arch = m.group(1)

    p = re.compile(".*sp(\d)$")
    m = p.match(vm_name)
    if m is None:
        patch_level = None
    else:
        if int(m.group(1)) > 3:
            patch_level = "sp1"
        else:
            patch_level = "sp" + m.group(1)

    p = re.compile(".*_(\d+)$")
    m = p.match(vm_name)
    if m is None:
        build_version = None
    else:
        build_version = m.group(1)

    # NOTE: very specific to the current windows baseline build vm names
    cpe_str = "cpe:/o:" + "microsoft:" + "windows_"
    if version.startswith('20'):
        cpe_str += "server_"
    cpe_str += version + ":"
    if build_version is not None:
        cpe_str += build_version
    elif revision is not None and patch_level is not None:
        cpe_str += revision
    cpe_str += ":"

    if patch_level is not None:
        cpe_str += patch_level
    else:
        if revision is not None:
            cpe_str += revision
    cpe_str += ":" + arch

    return cpe_str

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
        cpe_str = vm_as_cpe_string(name)
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
