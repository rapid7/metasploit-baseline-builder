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
                        template['boot_command']
                    ],
                    "floppy_files": [
                        '{{ user `http_directory` }}/{{ user `kickstart` }}'
                    ]
                })

        for prov in self.local_packer['provisioners']:
            if 'scripts' in prov:
                update_scripts = []
                for script in prov['scripts']:
                    if "script/" in script:
                        script_name = script[script.index("/") + 1:script.index(".")] + "_script"
                    else:
                        script_name = "custom_script"
                    if script_name in template:
                        update_scripts.append(template[script_name])
                    else:
                        update_scripts.append(script)
                prov.update({
                        "scripts": update_scripts
                    })
                
        for processor in self.local_packer["post-processors"]:
            if processor['type'] == 'vagrant':
                processor.update({
                    "output": template['output']
                })
                break

    def update_url(self, template):

        base = template['update_url_template']

        if "VERSION" in template['update_url_template']: # this essentially just deals with ubuntu url's (or other difficult ones that pop up)
            version = re.search('\d\d\.\d\d\.\d', template['iso_name'])
            if version:
                base = base[:base.index("VERSION")] + version.group(0)
            else:
                version = re.search('\d\d.\d\d', template['iso_name'])
                if version and 'live' in template['iso_name']:
                    version = version.group(0)
                else:
                    version = version.group(0) + ".0"
                base = base[:base.index("VERSION")] + version
            url = '/'.join([base, template['iso_name']])
        else: # this should handle all other os url's
            url = '/'.join([base, template['iso_url'][template['iso_url'].index(template['url_base_common'])+len(template['url_base_common']):]])
        
        template.update({
                    "iso_url": url
            })
                               


    def use_esxi_config(self):
        for builder in self.local_packer['builders']:
            if builder['type'] == "vmware-iso":
                if "tools_upload_flavor" in builder:
                    builder.pop("tools_upload_flavor")
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
