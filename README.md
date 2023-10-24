# metasploit-baseline-builder
## Purpose
This project provides baseline virtual machines for creation of testing environments requiring primarily windows based targets.

## Pre-Requisites
Prior to usage of the utility provided here the following must be obtained or configured:

* A virtualization platform (i.e. VMWare Fusion, VMWare Workstation, VirtualBox)
* Packer (https://www.packer.io/)
* Installation media for the desired operating systems.
* Python >= 2.7.11

## Installation
```
pip install -r requirements.txt
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

##### Open VNC Ports on the Firewall

Packer connects to the VM using VNC, so open a range of ports to allow it to connect to it.

First, ensure you can edit the firewall configuration:

```
chmod 644 /etc/vmware/firewall/service.xml
chmod +t /etc/vmware/firewall/service.xml
```

Then append the range we want to open to the end of the file:

```
<service id="1000">
  <id>packer-vnc</id>
  <rule id="0000">
    <direction>inbound</direction>
    <protocol>tcp</protocol>
    <porttype>dst</porttype>
    <port>
      <begin>5900</begin>
      <end>6000</end>
    </port>
  </rule>
  <enabled>true</enabled>
  <required>true</required>
</service>
```

Finally, restore the permissions and reload the firewall:

```
chmod 444 /etc/vmware/firewall/service.xml
esxcli network firewall refresh
```

##### Execute the build
```
python build_baselines.py [options]
python build_msf_host.py [options]
```

## Docker Environment
From the root directory:
```
docker build -t rapid7/build:payload-lab -f docker/Dockerfile .
```

To execute the build process:
```
docker run --rm=true --tty -u jenkins \
    --volume=${FULL_PATH_TO_WORKING_DIR}:/r7-source \
    --workdir=/r7-source/metasploit-baseline-bulder rapid7/build:payload-lab \
    bash -l -c "python build_baselines.py [options]"
docker run --rm=true --tty -u jenkins \
    --volume=${FULL_PATH_TO_WORKING_DIR}:/r7-source \
    --workdir=/r7-source/metasploit-baseline-bulder rapid7/build:payload-lab \
    bash -l -c "python build_msf_host.py [options]"
```

### Logging Output
When executed output for each VM will have logs in <WORKING_DIR>/tmp/<VM_NAME>

### It Did Not Work?
Check the output log files in each <VM_NAME>
`ls -lrt metasploit-baseline-builder/*/output.log` will give the output logs in time order.  The most recent log is the one you should check.
