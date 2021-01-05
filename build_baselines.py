import getopt
import json
import multiprocessing
import os.path
import packer
import re
import sh
import signal
import sys
import time
from tqdm import tqdm
from lib import packerMod
from lib import serverHelper

from xml.etree import ElementTree

TEMP_DIR = "./tmp"
esxi_file = "esxi_config.json"


def create_autounattend(vm_name, os_parts=None, index="1", prependString=""):
    # Product Keys from http://technet.microsoft.com/en-us/library/jj612867.aspx
    # Newer keys from https://docs.microsoft.com/en-us/windows-server/get-started/kmsclientkeys
    os_keys = {
        "10": "W269N-WFGWX-YVC9B-4J6C9-T83GX",
        "1709": "DPCNP-XQFKJ-BJF7R-FRC8D-GF6G4",
        "1803": "PTXN8-JFHJM-4WC78-MPCBR-9W4KR",
        "1809": "N2KJX-J94YW-TQVFB-DG9YT-724CC",
        "2003": None,
        "2003r2": None,
        "2008": "TM24T-X9RMF-VWXK6-X8JC9-BFGM2",
        "2008r2": "YC6KT-GKW9T-YTKYR-T4X34-R7VHC",
        "2012": "XC9B7-NBPP2-83J2H-RHMBY-92BT4",
        "2012r2": "D2N9P-3P6X9-2R39C-7RTCD-MDVJX",
        "2016": "WC2BQ-8NRM3-FDDYY-2BFGV-KHKQY",
        "2019": "N69G4-B89J2-4G8F4-WWYCC-J464C",
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

    temp_path = os.path.join(TEMP_DIR, prependString + vm_name)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    file_name = os.path.join(temp_path, "Autounattend.xml")
    tree.write(file_or_filename=file_name)

    return file_name


def remove_baseline(vmServer, iso, prependString = ""):
    os_parts = parse_iso(iso)
    vm_name = prependString + get_vm_name(os_parts)
    vm = vmServer.get_vm(vm_name)
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
    if m is None or m.group(1) == version:
        build_version = None
    else:
        build_version = m.group(1)

    return {
        "version": version,
        "arch": arch,
        "patch_level": patch_level,
        "build_version": build_version
    }


def build_base(iso, md5, replace_existing, vmServer=None, prependString = "", index = "1", factory_image = False):
    global esxi_file

    os_types_vmware = {
        "10": "windows9-64",
        "1709": "windows9srv-64",
        "1803": "windows9srv-64",
        "1809": "windows9srv-64",
        "2003": "winnetstandard",
        "2003r2": "winnetstandard-64",
        "2008": "longhorn-64",
        "2008r2": "windows7srv-64",
        "2012": "windows8srv-64",
        "2012r2": "windows8srv-64",
        "2016": "windows9srv-64",
        "2019": "windows9srv-64",
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

    temp_path = os.path.join(TEMP_DIR, prependString + vm_name)

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

    packer_obj = packerMod(packerfile)
    # if an esxi_config file is found add to the packer file params needed for esxi
    if vmServer.get_esxi() is not None:
        packer_vars.update(vmServer.get_config())
        packer_obj.use_esxi_config()
    else:
        packer_obj.update_config({
                        "output": "./../../box/" + output
                    })

    packerfile = os.path.join(temp_path, "current_packer.json")

    if factory_image:
        # Software we don't want on our factory image
        software = ["python", "java", "ruby"]
        for provisioner in packer_obj.local_packer['provisioners']:
            if any(x in str(provisioner.values()) for x in software):
                provisioner['except'] = only

    packer_obj.save_config(packerfile)

    packer_vars.update({
        "vm_name": prependString + vm_name
    })

    autounattend = create_autounattend(vm_name, os_parts, index=index, prependString=prependString)

    os_type = os_types_vmware[os_parts['version']]
    if os_parts['arch'] == 'x86':
        os_type = os_type.replace("-64", "")

    packer_vars.update({
        "iso_url": "./iso/" + iso,
        "iso_checksum": md5,
        "autounattend": autounattend,
        "output": "./box/" + output,
        "vagrantfile_template": vagrant_template,
        "guest_os_type": os_type,
        "vm_name": prependString + vm_name
    })

    out_file = os.path.join(temp_path, "output.log")
    err_file = os.path.join(temp_path, "error.log")

    p = packer.Packer(str(packerfile), only=only, vars=packer_vars,
                      out_iter=out_file, err_iter=err_file)
    vm = vmServer.get_vm(prependString + vm_name)
    if vm is not None:
        if replace_existing:
            vmServer.remove_vm(vm_name)
        else:
            return p  # just return without exec since ret value is not checked anyways

    try:
        p.build(parallel=True, debug=False, force=False)
    except sh.ErrorReturnCode:
        print "Error: build of " + prependString + vm_name + " returned non-zero"
        return p

    if vmServer.get_esxi() is not None:
        vm = vmServer.get_vm(prependString + vm_name)
        if vm is not None:
            vm.takeSnapshot(snapshotName='baseline')
            # possibly change the network in future
    return p


def main(argv):
    num_processors = 1
    prependString = ""
    factory_image = False
    replace_vms = False

    try:
        opts, args = getopt.getopt(argv[1:], "c:fhn:p:r", ["esxiConfig=", "factory", "help", "numProcessors=", "prependString=", "replace"])
    except getopt.GetoptError:
        print argv[0] + ' -n <numProcessors>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print argv[0] + " [options]"
            print '-c <file>, --esxiConfig=<file>       use alternate hypervisor config file'
            print '-f, --factory                        builds system without additional packages'
            print '-n <int>, --numProcessors=<int>      execute <int> parallel builds'
            print '-p <string>, --prependString=<file>  prepend string to the beginning of VM names'
            print '-r, --replace                        replace existing baselines'
            sys.exit()
        elif opt in ("-c", "--esxiConfig"):
            global esxi_file
            esxi_file = arg
        elif opt in ("-f", "--factory"):
            factory_image = True # Build with minimum required software, users and vm tools.
        elif opt in ("-n", "--numProcessors"):
            num_processors = int(arg)
        elif opt in ("-p", "--prependString"):
            prependString = arg
        elif opt in ("-r", "--replace"):
            replace_vms = True

    with open("iso_list.json", 'r') as iso_config:
        iso_map = json.load(iso_config)

    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

    pool = None
    try:
        vmServer = serverHelper(esxi_file)
        if replace_vms and vmServer.get_esxi() is not None:
            print "removing baselines"
            for file_name in tqdm(iso_map):
                remove_baseline(vmServer, file_name, prependString)

        print "generating baselines"
        if num_processors > 1:
            pool = multiprocessing.Pool(num_processors)

            signal.signal(signal.SIGINT, original_sigint_handler)

            results = []
            for file_name in iso_map:
                pool.apply_async(build_base, [file_name, iso_map[file_name]['md5'], replace_vms, vmServer, prependString, iso_map[file_name]['install_index']], factory_image, callback=results.append)

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
                build_base(file_name, iso_map[file_name]['md5'], replace_vms, vmServer, prependString, iso_map[file_name]['install_index'], factory_image)

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
