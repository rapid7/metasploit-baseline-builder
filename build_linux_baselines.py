import getopt
import glob
import json
import sys
import sh
import os
import packer
import requests
import fnmatch
from tqdm import tqdm
from lib import packerMod
from lib import serverHelper


def build_base(packer_var_file, common_vars, packerfile, replace_existing, vmServer=None, prependString = "", factory_image = False):
    TEMP_DIR="tmp"

    vm_name = packer_var_file.strip(".json")
    if "-server" in vm_name:
        vm_name = vm_name[:vm_name.index("-server")]
    vm_name = "Linux" + vm_name.capitalize() + "x64"

    temp_path = os.path.join("..", "..", TEMP_DIR, prependString + vm_name)

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    output = vm_name + "_vmware.box"

    only = ['vmware-iso']

    with open(os.path.join("", packer_var_file)) as packer_var_source:
        packer_vars = json.load(packer_var_source)

    packer_vars.update({
        "vm_name": prependString + vm_name,
        "output": os.path.join("..", "..", "box", output)
    })

    packer_vars.update(common_vars)
    if factory_image:
        del packer_vars["custom_script"]
        
    packer_obj = packerMod(packerfile)
    packer_obj.update_linux_config(packer_vars)

    request = requests.head(packer_vars['iso_url'])
    if request.status_code != 200:
        packer_obj.update_url(packer_vars)

    if vmServer.get_esxi() is not None:
        packer_vars.update(vmServer.get_config())
        packer_obj.use_esxi_config()
    else:
        packer_obj.update_config({
                        "output": "./../../box/" + output
                    })

    packerfile = os.path.join(temp_path, "current_packer.json")
    packer_obj.save_config(packerfile)

    out_file = os.path.join(temp_path, "output.log")
    err_file = os.path.join(temp_path, "error.log")

    p = packer.Packer(str(packerfile), only=only, vars=packer_vars,
                      out_iter=out_file, err_iter=err_file)

    vm = vmServer.get_vm(prependString + vm_name)
    if vm is not None:
        if replace_existing:
            vm.powerOff
            vm.waitForTask(vm.vmObject.Destroy_Task())
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

    return p


def main(argv):

    prependString = ""
    replace_vms = False
    factory_image = False
    esxi_file = "esxi_config.json"

    try:
        opts, args = getopt.getopt(argv[1:], "c:fhp:r", ["esxiConfig=", "factory", "help", "prependString=", "replace"])
    except getopt.GetoptError:
        print argv[0] + ' -n <numProcessors>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print argv[0] + " [options]"
            print '-c <file>, --esxiConfig=<file>       use alternate hypervisor config file'
            print '-f, --factory                        builds system without additional packages'
            print '-p <string>, --prependString=<file>  prepend string to the beginning of VM names'
            print '-r, --replace                        replace existing msf_host'
            sys.exit()
        elif opt in ("-c", "--esxiConfig"):
            esxi_file = arg
        elif opt in ("-f", "--factory"):
            factory_image = True # Build with minimum required software, users and vm tools.
        elif opt in ("-p", "--prependString"):
            prependString = arg
        elif opt in ("-r", "--replace"):
            replace_vms = True

    vm_server = serverHelper(esxi_file)

    os.chdir("boxcutter")

    for os_dir in os.listdir("."):
        if os.path.isdir(os.path.join(".", os_dir)):
            common_var_file = os.path.join("..", "linux_vars", os_dir + "_common.json")
            with open(os.path.join("", common_var_file)) as common_var_source:
                common_vars = json.load(common_var_source)

            os.chdir(os.path.join("", os_dir))
            packer_file = os_dir + ".json"

            targets = []
            for pattern in common_vars['file_patterns']:
                targets.extend(glob.glob(pattern))

            print "\nBuilding " + str(len(targets)) + " " + os_dir.capitalize() + " baselines:"
            for target in tqdm(targets):
                build_base(target, common_vars, packer_file, replace_existing=replace_vms, vmServer=vm_server, prependString=prependString, factory_image=factory_image)

            os.chdir("../")

    return True

if __name__ == "__main__":
    main(sys.argv)
