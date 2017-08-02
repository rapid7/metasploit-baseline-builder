# metasploit-baseline-builder
## Purpose
This project provides baseline virtual machines for creation of testing environments requiring primarily windows based targets.

## Pre-Requisites
Prior to usage of the utility provided here the following must be obtained or configured:

* A visualization platform (i.e. VMWare Fusion, VMWare Workstation, VirtualBox)
* Vagrant (https://www.vagrantup.com/)
* Vagrant plugin for the visualization platform (for esxi `vagrant plugin install vagrant-vsphere`)
* Packer (https://www.packer.io/)
* Installation media for the desired operating systems.
* Python >= 2.7.11

## Installation
```
pip install tqdm
pip install vm-automation
````

## Usage
### General
Obtain all required iso files listed in `iso_list.json` make them available
at `<install location>/iso`


### VMWare Fusion and Workstation
python build_baselines.py [options]

### WMWare ESXI (vsphere)
Create an esxi_config.json with the required parameters.
```
{
  "esxi_host": "",
  "esxi_datastore": "",
  "esxi_cache_datastore": "",
  "esxi_username": "",
  "esxi_password": "",
  "esxi_network": ""
}
```

Configure the ESXI server:
* Enable ssh access
* Configure IP address hack
* Open VNC firewall on ESXI

python build_baselines.py [options]

## Docker Enviornment
Create a local user `jenkins` with UID=1001

```
cd docker
docker build -t rapid7/build:payload-lab .
```

To execute the build process:
```
docker run --rm=true --tty -u jenkins \
    --volume=${PATH_TO_WORKING_DIR}:/r7-source \
    --workdir=/r7-source/metasploit-baseline-bulder rapid7/build:payload-testing \
    bash -l -c "python build_baselines.py [options]"
```

### Logging Output
When executed output for each VM will have logs in <WORKING_DIR>/tmp/<VM_NAME>
