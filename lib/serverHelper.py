import json
import os
import vm_automation


class serverHelper:
    esxi_config = None

    def __init__(self, esxi_file):
        if os.path.isfile(esxi_file):
            with open(esxi_file) as config_file:
                self.esxi_config = json.load(config_file)

    def get_esxi(self):
        if self.esxi_config is not None:
            # TODO: make this more efficient than an new object per call
            vmServer = vm_automation.esxiServer(self.esxi_config["esxi_host"],
                                                self.esxi_config["esxi_username"],
                                                self.esxi_config["esxi_password"],
                                                '443',  # default port for interaction
                                                'esxi_automation.log')
            vmServer.connect()
            return vmServer
        return None

    def get_config(self):
        return self.esxi_config

    def get_vm(self, vm_name):
        vm_server = self.get_esxi()
        if vm_server is not None:
            return vm_server.getVmByName(vm_name)
        return None

    def remove_vm(self, vm_name):
        vm = self.get_vm(vm_name)
        if vm is not None:
            vm.powerOff
            vm.waitForTask(vm.vmObject.Destroy_Task())
            return True
        return False
