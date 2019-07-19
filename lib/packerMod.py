import json
import re


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
        for builder in self.local_packer['builders']:
            if 'kickstart' in template and 'boot_command' in builder:
                builder.update({
                    "boot_command": [
                        "<tab> linux text biosdevname=0 ks=hd:fd0:/{{ user `kickstart` }}<enter><enter>"
                    ]
                })
                builder.update({'floppy_files': 'http/{{ user `kickstart` }}'})

        for prov in self.local_packer['provisioners']:
            if 'scripts' in prov:
                update_scripts = []
                for script in prov['scripts']:
                    if "script/" in script:
                        script_name = script[script.index("/") + 1:script.index(".")]
                        update_scripts.append("{{user `" + script_name + "_script`}}")
                    else:
                        update_scripts.append("{{user `custom_script`}}")
                prov.update({
                        "scripts": update_scripts
                    })
                
        for processor in self.local_packer["post-processors"]:
            if processor['type'] == 'vagrant':
                processor.update({
                    "output": template['output']
                })
                break

    def update_url(self, template): #this could be a lot better, I'll think on it
        version = re.search('(\d\d\.\d\d\.\d)', template['iso_name'])
        if version:
            v = version.group(0)
            url = '/'.join([template['update_url_template'], v, template['iso_name']])
        else:
            version = re.search('(\d\d\.\d\d)', template['iso_name'])
            if version:
                v = version.group(0)
                if 'live' in template['iso_name']: # handles more recent releases of ubuntu
                    url = '/'.join([template['update_url_template'], v, template['iso_name']])
                else:
                    v = v + ".0"
                    url = '/'.join([template['update_url_template'], v, template['iso_name']])
            else:
                version = re.search('\d\d', template['vm_name'])
                v = version.group(0)
                url = '/'.join([template['update_url_template'], version.group(0), "Server/x86_64/iso", template['iso_name']])

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
