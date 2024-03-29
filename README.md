# metasploit-baseline-builder
## Purpose
This project provides baseline virtual machines for creation of testing environments requiring primarily windows based targets.

## Pre-Requisites
Prior to usage of the utility provided here the following must be obtained or configured:

* A virtualization platform (i.e. VMWare Fusion, VMWare Workstation, VirtualBox)
* Packer (https://www.packer.io/) version >= 1.9.4
* Installation media for the desired operating systems.
* Python >= 2.7.11
* You may need to install the VMware plugin for Packer: `packer plugins install github.com/hashicorp/vmware`

## Installation
```
python -m pip install -r requirements.txt
````

## Usage
### General
Obtain all required iso files listed in `iso_list.json` make them available
at `<install location>/iso`
To build the msf_host be sure to init submodules
```
git submodule init
git submodule update
```


### VMWare Fusion and Workstation
```
python build_baselines.py [options]
python build_msf_host.py [options]
```

### VMWare ESXI (vsphere)
Create an `esxi_config.json` with the required parameters.
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

#### Configure the ESXI server:
Purloined from [Nick Charlton's December 2016 writeup.](https://nickcharlton.net/posts/using-packer-esxi-6.html) Thank you! 

##### Enable SSH

Inside the web UI, navigate to “Manage”, then the “Services” tab. Find the entry called: “TSM-SSH”, and enable it.

You may wish to enable it to start up with the host by default. You can do this inside the “Actions” dropdown (it’s nested inside “Policy”).

##### Enable “Guest IP Hack”

Run the following command on the ESXi host:

```
esxcli system settings advanced set -o /Net/GuestIPHack -i 1
```

This allows Packer to infer the guest IP from ESXi, without the VM needing to report it itself.

##### Execute the build
```
python build_baselines.py [options]
python build_msf_host.py [options]
```

## Docker Environment
Create a local user `jenkins` with UID=1001

```
docker build -t rapid7/build:payload-lab -f docker/Dockerfile
```

To execute the build process:
```
docker run --rm=true --tty -u jenkins \
    --volume=${FULL_PATH_TO_WORKING_DIR}:/r7-source \
    --workdir=/r7-source/metasploit-baseline-builder rapid7/build:payload-lab \
    bash -l -c "python build_baselines.py [options]"
docker run --rm=true --tty -u jenkins \
    --volume=${FULL_PATH_TO_WORKING_DIR}:/r7-source \
    --workdir=/r7-source/metasploit-baseline-builder rapid7/build:payload-lab \
    bash -l -c "python build_msf_host.py [options]"
```

### Logging Output
When executed output for each VM will have logs in <WORKING_DIR>/tmp/<VM_NAME>

### It Did Not Work?
Check the output log files in each <VM_NAME>
`ls -lrt metasploit-baseline-builder/*/output.log` will give the output logs in time order.  The most recent log is the one you should check.
