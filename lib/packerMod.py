import json
import re
import mmap


class packerMod:
    local_packer = {}

    def __init__(self, packer_file):
        with open(packer_file) as packer_source:
            self.local_packer = json.load(packer_source)

    def update_config(self, template):
        if 'custom_scripts' in template:
            for provisioner in self.local_packer['provisioners']:
                if 'scripts' in provisioner:
                    for script in template['custom_scripts']:
                        provisioner['scripts'].append(script)
                    break
        for processor in self.local_packer["post-processors"]:
            if processor['type'] == 'vagrant':
                processor.update({
                    "output": template['output']
                })
                break

    def update_linux_config(self, template):
        for prov in self.local_packer['provisioners']:  # this block allows us to customize the scripts for
            if 'scripts' in prov:                       # all linux os types without the use of large data structures
                prov.update({
                    "scripts": [
                        "{{user `update_script`}}",
                        "{{user `desktop_script`}}",
                        "{{user `vagrant_script`}}",
                        "{{user `sshd_script`}}",
                        "{{user `vmware_script`}}",
                        "{{user `virtualbox_script`}}",
                        "{{user `parallels_script`}}",
                        "{{user `motd_script`}}",
                        "{{user `custom_script`}}",
                        "{{user `minimize_script`}}",
                        "{{user `cleanup_script`}}"
                    ]
        })
                
        for processor in self.local_packer["post-processors"]:
            if processor['type'] == 'vagrant':
                processor.update({
                    "output": template['output']
                })
                break

    def update_url(self, template):  # this method will be expanded to account for url's of other os types
        if "ubuntu" in template['iso_name']:
            version = template['iso_name']
            version = re.compile("(?!ubuntu-)(\d\d\.\d\d\.\d|\d\d\.\d\d)")
            url = '/'.join([template['update_url_template'], version.pattern, template['iso_name']])
            template.update({
                            "iso_url": url
                        })


    def use_esxi_config(self):
        for builder in self.local_packer['builders']:
            if builder['type'] == "vmware-iso":
                builder.update({
                    "remote_type": "esx5",
                    "remote_host": "{{user `esxi_host`}}",
                    "remote_datastore": "{{user `esxi_datastore`}}",
                    "remote_username": "{{user `esxi_username`}}",
                    "remote_password": "{{user `esxi_password`}}",
                    "skip_export": True,
                    "keep_registered": True,
                    "vnc_port_min": "5900",
                    "vnc_port_max": "5911",
                    "vnc_bind_address": "0.0.0.0",
                    "vnc_disable_password": True,
                    "disk_type_id": "thin",
                    "output_directory": "{{user `vm_name`}}",
                    "remote_cache_datastore": "{{user `esxi_cache_datastore`}}"
                })
                if 'vmx_remove_ethernet_interfaces' in builder:
                    del builder['vmx_remove_ethernet_interfaces']
                builder['vmx_data'].update({
                  "ethernet0.networkName": "{{user `esxi_network`}}"
                })
        self.local_packer["post-processors"] = []

    def save_config(self, path):
        with open(path, "w") as packer_handle:
            json.dump(self.local_packer, packer_handle, indent=2, sort_keys=False)
