import argparse
import json
import multiprocessing
import os
import signal
import time
from tqdm import tqdm
import vm_automation

WINDOWS_REQUIRED = "Win"
UAC_ENABLE_COMMAND = ['cmd.exe',
                      '/k',
                      '%SystemRoot%\System32\\reg.exe',
                      'ADD',
                      'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System',
                      '/v',
                      'EnableLUA',
                      '/t',
                      'REG_DWORD',
                      '/d',
                      '1',
                      '/f']
DISABLE_SMB1_COMMAND = ['cmd.exe',
                        '/k',
                        '%SystemRoot%\System32\\reg.exe',
                        'ADD',
                        'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters',
                        '/v',
                        'SMB1',
                        '/t',
                        'REG_DWORD',
                        '/d',
                        '0',
                        '/f']



def get_vm_server(config_file):
    if os.path.isfile(config_file):
        with open(config_file) as config_file_handle:
            config_map = json.load(config_file_handle)
            if config_map['HYPERVISOR_TYPE'].lower() == "esxi":
                vmServer = vm_automation.esxiServer.createFromConfig(config_map, 'esxi_autoamtion.log')
                vmServer.connect()
            if config_map['HYPERVISOR_TYPE'].lower() == "workstation":
                vmServer = vm_automation.workstationServer(config_map, 'workstation_automation.log')
        return vmServer
    return None


def enable_uac(vm_config, vm_name, command):
    schedule_delay = 30
    vm_server = get_vm_server(config_file=vm_config)
    vm_server.enumerateVms()
    for vm in vm_server.vmList:
        if vm_name == vm.vmName:
            vm.powerOn()
            vm_ready = False
            while vm_ready is False:
                vm_ready = vm_server.waitForVmsToBoot([vm])
            vm.setUsername('vagrant')
            vm.setPassword('vagrant')
            vm.runCmdOnGuest(command)
            time.sleep(schedule_delay)
            vm.vmObject.ShutdownGuest()
            time.sleep(10)
            vm.powerOff()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keyword", help="VM search parameter")
    parser.add_argument("-a", "--action", help="action [enable_uac|disable_smb1]")
    parser.add_argument("hypervisorConfig", help="json hypervisor config")

    args = parser.parse_args()

    validActions = ['enable_uac', 'disable_smb1']

    prefix = args.keyword

    if args.action.lower() not in validActions:
        print('INVALID ACTION')
    if args.action.lower() == 'enable_uac':
        command = UAC_ENABLE_COMMAND
    elif args.action.lower() == 'disable_smb1':
        command = UAC_ENABLE_COMMAND

    vm_server = get_vm_server(config_file=args.hypervisorConfig)
    if vm_server is None:
        print ("Failed to connect to VM environment")
        exit(1)

    vm_list = []
    vm_server.enumerateVms()
    for vm in vm_server.vmList:
        if prefix in vm.vmName and WINDOWS_REQUIRED in vm.vmName:
            vm_list.append(vm.vmName)

    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

    pool = None
    try:
        pool = multiprocessing.Pool(3)

        signal.signal(signal.SIGINT, original_sigint_handler)

        results = []
        for vm_name in vm_list:
            pool.apply_async(enable_uac, [args.hypervisorConfig, vm_name, command], callback=results.append)

        with tqdm(total=len(vm_list)) as progress:
            current_len = 0
            while len(results) < len(vm_list):
                if (len(results) > current_len):
                    progress.update(len(results) - current_len)
                    current_len = len(results)
                time.sleep(5)
            progress.update(len(results))

    except KeyboardInterrupt:
        print("User cancel received, terminating all task")
        if pool is not None:
            pool.terminate()

    print("Processing complete " + str(len(vm_list)) + " systems updated")
    if pool is not None:
        pool.close()
        pool.join()



if __name__ == "__main__":
    main()
