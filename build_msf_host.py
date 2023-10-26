import getopt
import glob
import json
import sys
import os
import packer
from tqdm import tqdm
from lib import packerMod
from lib import serverHelper


def build_base(packer_var_file, replace_existing, vmServer=None, prependString = ""):
    TEMP_DIR="tmp"

    vm_name = packer_var_file.strip("_packer.json")

    temp_path = os.path.join("..", "..", TEMP_DIR, prependString + vm_name)

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    output = vm_name + "_vmware.box"

    only = ['vmware-iso']

    with open(os.path.join("..", "..", packer_var_file)) as packer_var_source:
        packer_vars = json.load(packer_var_source)

    packer_vars.update({
        "vm_name": prependString + vm_name,
        "output": os.path.join("..", "..", "box", output)
    })

    packerfile = "ubuntu-legacy.json"

    packer_obj = packerMod(packerfile)
    packer_obj.update_config(packer_vars)

    if vmServer.get_esxi() is not None:
        packer_vars.update(vmServer.get_config())
        packer_obj.use_esxi_config()

    packerfile = os.path.join(temp_path, vm_name + ".json")
    packer_obj.save_config(packerfile)

    out_file = os.path.join(temp_path, "output.log")
    err_file = os.path.join(temp_path, "error.log")

    p = packer.Packer(str(packerfile), only=only, vars=packer_vars,
                      out_iter=out_file, err_iter=err_file)

    vm = vmServer.get_vm(prependString + vm_name)
    if vm is not None:
        if replace_existing:
            vmServer.remove_vm(prependString + vm_name)
        else:
            return p  # just return without exec since ret value is not checked anyways

    p.build(parallel=False, debug=False, force=False)

    if vmServer.get_esxi() is not None:
        vm = vmServer.get_vm(prependString + vm_name)
        if vm is not None:
            vm.takeSnapshot(snapshotName='baseline')

    return p


def main(argv):

    prependString = ""
    replace_vms = False
    esxi_file = "esxi_config.json"

    try:
        opts, args = getopt.getopt(argv[1:], "c:hp:r", ["prependString="])
    except getopt.GetoptError:
        print argv[0] + ' -n <numProcessors>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print argv[0] + " [options]"
            print '-c <file>, --esxiConfig=<file>   use alternate hypervisor config file'
            print '-p <string>, --prependString=<file>   prepend string to the beginning of VM names'
            print '-r, --replace                     replace existing msf_host'
            sys.exit()
        elif opt in ("-c", "--esxiConfig"):
            esxi_file = arg
        elif opt in ("-p", "--prependString"):
            prependString = arg
        elif opt in ("-r", "--replace"):
            replace_vms = True

    targets = glob.glob('msf_host_packer.json')

    vm_server = serverHelper(esxi_file)

    os.chdir("boxcutter/ubuntu")

    for target in tqdm(targets):
        build_base(target, replace_existing=replace_vms, vmServer=vm_server, prependString=prependString)

    return True

if __name__ == "__main__":
    main(sys.argv)

