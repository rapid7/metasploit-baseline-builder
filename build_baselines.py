import getopt
import json
import multiprocessing
import os.path
import packer
import re
import signal
import sys
import time
from tqdm import tqdm
import vm_automation

from xml.etree import ElementTree

TEMP_DIR = "./tmp"
esxi_file = "esxi_config.json"


def create_autounattend(vm_name, os_parts=None, index="1"):
    # Product Keys from http://technet.microsoft.com/en-us/library/jj612867.aspx
    os_keys = {
        "10": "W269N-WFGWX-YVC9B-4J6C9-T83GX",
        "2003": None,
        "2003r2": None,
        "2008": "TM24T-X9RMF-VWXK6-X8JC9-BFGM2",
        "2008r2": "YC6KT-GKW9T-YTKYR-T4X34-R7VHC",
        "2012": "XC9B7-NBPP2-83J2H-RHMBY-92BT4",
        "2012r2": "D2N9P-3P6X9-2R39C-7RTCD-MDVJX",
        "2016": "WC2BQ-8NRM3-FDDYY-2BFGV-KHKQY",
        "7": "FJ82H-XT6CR-J8D7P-XQJJ2-GPDD4",
        "8": "NG4HW-VH26C-733KW-K6F98-J8CK4",
        "8.1": "GCRJD-8NW9H-F2CDX-CCM8D-9D6T9",
        "xp": None
    }

    ElementTree.register_namespace('', "urn:schemas-microsoft-com:unattend")

    if os_parts is not None and os_parts['arch'] is not None:
        unattend_template = "./answer_files/windows/Autounattend_" + os_parts['arch'] + ".xml"
    else:
        unattend_template = "./answer_files/windows/Autounattend_x64.xml"

    with open(unattend_template, 'rt') as unattend_file:
        tree = ElementTree.parse(unattend_file)

    if os_parts is not None and os_keys[os_parts['version']] is not None:
        for key in tree.findall(
                './/{urn:schemas-microsoft-com:unattend}ProductKey/{urn:schemas-microsoft-com:unattend}Key'):
            key.text = os_keys[os_parts['version']]
    else:
        for key in tree.findall('.//{urn:schemas-microsoft-com:unattend}ProductKey'):
            for child in list(key):
                if child.tag == "{urn:schemas-microsoft-com:unattend}Key":
                    key.remove(child)

    for name in tree.findall('.//{urn:schemas-microsoft-com:unattend}ComputerName'):
        name.text = vm_name

    if index != "1":
        for value in tree.findall('.//{urn:schemas-microsoft-com:unattend}MetaData/{urn:schemas-microsoft-com:unattend}Value'):
            value.text = index

    if os_parts['version'] == "10":
        for os_image in tree.findall('.//{urn:schemas-microsoft-com:unattend}OSImage'):
            for metadata in tree.findall('.//{urn:schemas-microsoft-com:unattend}InstallFrom'):
                os_image.remove(metadata)

    temp_path = os.path.join(TEMP_DIR, vm_name)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    file_name = os.path.join(temp_path, "Autounattend.xml")
    tree.write(file_or_filename=file_name)

    return file_name

def get_esxi(esxi_file):
    if os.path.isfile(esxi_file):
        with open(esxi_file) as config_file:
            esxi_config = json.load(config_file)

            # TODO: make this more efficient than an new object per call
            vmServer = vm_automation.esxiServer(esxi_config["esxi_host"],
                                                esxi_config["esxi_username"],
                                                esxi_config["esxi_password"],
                                                '443',  # default port for interaction
                                                'esxi_automation.log')
            vmServer.connect()
            return vmServer
    return None

def remove_baseline(vmServer, iso):
    os_parts = parse_iso(iso)
    vm_name = get_vm_name(os_parts)
    vm = get_vm(vmServer, vm_name)
    if vm is not None:
        vm.powerOff
        vm.waitForTask(vm.vmObject.Destroy_Task())

def get_vm_name(os_parts):
    vm_name = "Win" + os_parts["version"].replace(".", "") + os_parts["arch"]
    if os_parts["patch_level"] is not None:
        vm_name += os_parts["patch_level"]
    if os_parts["build_version"] is not None:
        vm_name += "_" + os_parts["build_version"]
    return vm_name

def get_vm(vm_server, vm_name):
    if vm_server is not None:
        vm_server.enumerateVms()
        # ick side effects maybe this object can just check for a vm with name
        # doing this every time is also very inefficient but going with it for now
        for vm in vm_server.vmList:
            if vm.vmName == vm_name:
                return vm
    return None


def parse_iso(file_name):
    version_pattern = re.compile("en_win.*?_(\d_\d|\d.\d|\d+)_.*")
    v = version_pattern.match(file_name)
    if v is None:
        version = "xp"
    else:
        version = v.group(1).replace("_", ".")

    p = re.compile("en_win.*_(r2)_.*")
    m = p.match(file_name)
    if m is not None:
        version += "r2"

    p = re.compile("en_win.*_(x86|x64).*")
    m = p.match(file_name)
    if m is None:
        arch = "x86"
    else:
        arch = m.group(1)

    p = re.compile("en_win.*_with.*?(\d)_.*")
    m = p.match(file_name)
    if m is None:
        patch_level = None
    else:
        if int(m.group(1)) > 3:
            patch_level = "sp1"
        else:
            patch_level = "sp" + m.group(1)

    p = re.compile("en_win.*_version_(\d+)_.*")
    m = p.match(file_name)
    if m is None:
        build_version = None
    else:
        build_version = m.group(1)

    return {
        "version": version,
        "arch": arch,
        "patch_level": patch_level,
        "build_version": build_version
    }


def build_base(iso, md5, replace_existing, vmServer=None):
    global esxi_file

    os_types_vmware = {
        "10": "windows9-64",
        "2003": "winnetstandard",
        "2003r2": "winnetstandard-64",
        "2008": "longhorn-64",
        "2008r2": "windows7srv-64",
        "2012": "windows8srv-64",
        "2012r2": "windows8srv-64",
        "2016": "windows9srv-64",
        "7": "windows7-64",
        "8": "windows8-64",
        "8.1": "windows8-64",
        "xp": "winXPPro-64",
    }

    os_parts = parse_iso(iso)

    vm_name = get_vm_name(os_parts)
    output = "windows_" + os_parts['version'] + "_" + os_parts['arch']

    if os_parts["patch_level"] is not None:
        output += "_" + os_parts["patch_level"]

    if os_parts["build_version"] is not None:
        output += "_" + os_parts["build_version"]

    temp_path = os.path.join(TEMP_DIR, vm_name)

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    # building vmware only for now
    output += "_vmware.box"

    packerfile = './windows_packer.json'
    # TODO: create custom vagrant file for the box being created for now packages a generic file
    vagrant_template = 'vagrantfile-windows_packer.template'

    only = ['vmware-iso']
    packer_vars = {
        "iso_checksum_type": "md5"
    }

    # if an esxi_config file is found add to the packer file params needed for esxi
    if vmServer is not None:
        with open(esxi_file) as config_file:
            esxi_config = json.load(config_file)
            packer_vars.update(esxi_config)

        with open(packerfile) as packer_source:
            packer_config = json.load(packer_source)
            for builder in packer_config['builders']:
                if builder['type'] == "vmware-iso":
                    builder.update({
                        "remote_type": "esx5",
                        "remote_host": "{{user `esxi_host`}}",
                        "remote_datastore": "{{user `esxi_datastore`}}",
                        "remote_username": "{{user `esxi_username`}}",
                        "remote_password": "{{user `esxi_password`}}",
                        "keep_registered": True,
                        "vnc_port_min": "5900",
                        "vnc_port_max": "5911",
                        "vnc_bind_address": "0.0.0.0",
                        "vnc_disable_password": True,
                        "disk_type_id": "thin",
                        "output_directory": vm_name
                    })
                    if esxi_config['esxi_cache_datastore'] is not None:
                        builder.update({
                            "remote_cache_datastore": "{{user `esxi_cache_datastore`}}"
                        })
                    builder['vmx_data'].update({
                      "ethernet0.networkName": "{{user `esxi_network`}}"
                    })
            packer_config["post-processors"] = []

            packerfile = os.path.join(temp_path, "current_packer.json")
            with open(packerfile, "w") as packer_current:
                json.dump(packer_config, packer_current)

    autounattend = create_autounattend(vm_name, os_parts)

    os_type = os_types_vmware[os_parts['version']]
    if os_parts['arch'] == 'x86':
        os_type.replace("64", "32")

    packer_vars.update({
        "iso_url": "./iso/" + iso,
        "iso_checksum": md5,
        "autounattend": autounattend,
        "output": "./box/" + output,
        "vagrantfile_template": vagrant_template,
        "guest_os_type": os_type,
        "vm_name": vm_name
    })

    out_file = os.path.join(temp_path, "output.log")
    err_file = os.path.join(temp_path, "error.log")

    p = packer.Packer(str(packerfile), only=only, vars=packer_vars,
                      out_iter=out_file, err_iter=err_file)
    vm = get_vm(vmServer, vm_name)
    if vm is not None:
        if replace_existing:
            vm.powerOff
            vm.waitForTask(vm.vmObject.Destroy_Task())
        else:
            return p  # just return without exec since ret value is not checked anyways


    p.build(parallel=True, debug=False, force=False)

    if vmServer is not None:
        vmServer.connect()
        vm = get_vm(vmServer, vm_name)
        if vm is not None:
            vm.takeSnapshot(snapshotName='baseline')
            # possibly change the network in future
    return p


def main(argv):
    num_processors = 1
    replace_vms = False

    try:
        opts, args = getopt.getopt(argv[1:], "hn:r", ["numProcessors="])
    except getopt.GetoptError:
        print argv[0] + ' -n <numProcessors>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print argv[0] + " [options]"
            print '-n <int>, --numProcessors=<int>   execute <int> parallel builds'
            print '-r, --replace                     replace existing baselines'
            sys.exit()
        elif opt in ("-n", "--numProcessors"):
            num_processors = int(arg)
        elif opt in ("-r", "--replace"):
            replace_vms = True

    with open("iso_list.json", 'r') as iso_config:
        iso_map = json.load(iso_config)

    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

    pool = None
    try:
        vmServer = get_esxi(esxi_file)
        if replace_vms and vmServer is not None:
            print "removing baselines"
            for file_name in tqdm(iso_map):
                remove_baseline(vmServer, file_name)

        print "generating baselines"
        if num_processors > 1:
            pool = multiprocessing.Pool(num_processors)

            signal.signal(signal.SIGINT, original_sigint_handler)

            results = []
            for file_name in iso_map:
                pool.apply_async(build_base, [file_name, iso_map[file_name], replace_vms, vmServer], callback=results.append)

            with tqdm(total=len(iso_map)) as progress:
                current_len = 0
                while len(results) < len(iso_map):
                    if (len(results) > current_len):
                        progress.update(len(results) - current_len)
                        current_len = len(results)
                    else:
                        progress.refresh()
                    time.sleep(5)
                progress.update(len(results))
        else:
            signal.signal(signal.SIGINT, original_sigint_handler)
            for file_name in tqdm(iso_map):
                vmServer = get_esxi(esxi_file)
                build_base(file_name, iso_map[file_name], replace_vms, vmServer)

    except KeyboardInterrupt:
        print("User cancel received, terminating all builds")
        if pool is not None:
            pool.terminate()
    else:
        print("Build complete")
        if pool is not None:
            pool.close()
            pool.join()

if __name__ == "__main__":
    main(sys.argv)
