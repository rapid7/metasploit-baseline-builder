import packer
import sys
import re
from xml.etree import ElementTree


def create_autounattend(vm_name, os_parts=None, index="1"):
    os_keys = {
        "10": "W269N-WFGWX-YVC9B-4J6C9-T83GX",
        "2003": None,
        "2003r2": None,
        "2008": "TM24T-X9RMF-VWXK6-X8JC9-BFGM2",
        "2008r2": "YC6KT-GKW9T-YTKYR-T4X34-R7VHC",
        "2012": "XC9B7-NBPP2-83J2H-RHMBY-92BT4",
        "2012r2": "D2N9P-3P6X9-2R39C-7RTCD-MDVJX",
        "2016": "WC2BQ-8NRM3-FDDYY-2BFGV-KHKQY",
        "7": "FJ82H-XT6CR-J8D7P-XQJJ2-GPDD4",
        "8": "NG4HW-VH26C-733KW-K6F98-J8CK4",
        "8.1": "GCRJD-8NW9H-F2CDX-CCM8D-9D6T9",
        "xp": None
    }

    ElementTree.register_namespace('', "urn:schemas-microsoft-com:unattend")

    if os_parts is not None and os_parts['arch'] is not None:
        unattend_template = "./answer_files/windows/Autounattend_"+ os_parts['arch'] + ".xml"
    else:
        unattend_template = "./answer_files/windows/Autounattend_x64.xml"

    with open(unattend_template, 'rt') as file:
        tree = ElementTree.parse(file)

    if os_parts is not None and os_keys[os_parts['version']] is not None:
        for key in tree.findall(
                './/{urn:schemas-microsoft-com:unattend}ProductKey/{urn:schemas-microsoft-com:unattend}Key'):
            print "changing " + key.text + " to " + os_keys[os_parts['version']]
            key.text = os_keys[os_parts['version']]
    else:
        for key in tree.findall('.//{urn:schemas-microsoft-com:unattend}ProductKey'):
            for child in list(key):
                if child.tag == "{urn:schemas-microsoft-com:unattend}Key":
                    key.remove(child)
            print "Removed product key"


    for name in tree.findall('.//{urn:schemas-microsoft-com:unattend}ComputerName'):
        print "changing " + name.text + " to " + vm_name
        name.text = vm_name

    if index != "1":
        for value in tree.findall('.//{urn:schemas-microsoft-com:unattend}MetaData/{urn:schemas-microsoft-com:unattend}Value'):
            print "setting index value to " + index
            value.text = index

    file_name = "./answer_files/windows/Autounattend.xml"
    tree.write(file_or_filename=file_name)

    return file_name


def parse_iso(file_name):
    print "processing " + file_name
    version_pattern = re.compile("en_win.*?_(\d_\d|\d.\d|\d+)_.*")
    v = version_pattern.match(file_name)
    if v is None:
        version = "xp"
    else:
        version = v.group(1).replace("_", ".")

    p = re.compile("en_win.*_(r2)_.*")
    m = p.match(file_name)
    if m is not None:
        version += "r2"

    p = re.compile("en_win.*_(x86|x64).*")
    m = p.match(file_name)
    if m is None:
        arch = "x86"
    else:
        arch = m.group(1)

    p = re.compile("en_win.*_with.*?(\d)_.*")
    m = p.match(file_name)
    if m is None:
        patch_level = None
    else:
        if int(m.group(1)) > 3:
            patch_level = "sp1"
        else:
            patch_level = "sp" + m.group(1)

    p = re.compile("en_win.*_version_(\d+)_.*")
    m = p.match(file_name)
    if m is None:
        build_version = None
    else:
        build_version = m.group(1)

    return {
        "version": version,
        "arch": arch,
        "patch_level": patch_level,
        "build_version": build_version
    }


def build_base(iso, md5):
    os_types_vmware = {
        "10": "windows9-64",
        "2003": "winnetstandard",
        "2003r2": "winnetstandard-64",
        "2008": "longhorn-64",
        "2008r2": "windows7srv-64",
        "2012": "windows8srv-64",
        "2012r2": "windows8srv-64",
        "2016": "windows9srv-64",
        "7": "windows7-64",
        "8": "windows8-64",
        "8.1": "windows8-64",
        "xp": "winXPPro-64",
    }

    os_parts = parse_iso(iso)

    vm_name = "Win" + os_parts["version"].replace(".", "") + os_parts["arch"]
    output = "windows_" + os_parts['version'] + "_" + os_parts['arch']

    if os_parts["patch_level"] is not None:
        vm_name += os_parts["patch_level"]
        output += "_" + os_parts["patch_level"]

    if os_parts["build_version"] is not None:
        vm_name += "_" + os_parts["build_version"]
        output += "_" + os_parts["build_version"]

    # building vmware only for now
    output += "_vmware.box"

    if len(vm_name) > 15:
        print "**********************" + vm_name + " TOO LONG" + "**********************"
    else:
        print vm_name

    packerfile = './windows_packer.json'
    #TODO: create custom vagrant file for the box being created for now packages a generic file
    vagrant_template = 'vagrantfile-windows_packer.template'

    only = ['vmware-iso']
    vars = {
        "iso_checksum_type": "md5"
    }

    # if os_parts['version'] == "7":
    #     autounattend = create_autounattend(vm_name, None, index="3", version=None)
    # else:
    autounattend = create_autounattend(vm_name, os_parts)

    vars.update({
        "iso_url": "./iso/" + iso,
        "iso_checksum": md5,
        "autounattend": autounattend,
        "output": "./box/" + output,
        "vagrantfile_template": vagrant_template,
        "guest_os_type": os_types_vmware[os_parts['version']],
        "vm_name": vm_name
    })

    p = packer.Packer(packerfile, only=only, vars=vars,
                      out_iter=sys.stdout, err_iter=sys.stderr)
    p.build(parallel=True, debug=False, force=False)

    return p

iso_map = {
    "en_windows_10_multiple_editions_version_1511_updated_apr_2016_x64_dvd_8705583.iso": "3ca03a2c59ae5b58ca965a345d4f2ae1",
    "en_windows_10_multiple_editions_version_1511_updated_apr_2016_x86_dvd_8735185.iso": "91565f54dc7a4e1df8a5f2b913d869b1",

    "en_windows_10_multiple_editions_version_1607_updated_jan_2017_x64_dvd_9714399.iso": "2d738dcde0fadec9dd687363bc9c98e8",
    "en_windows_10_multiple_editions_version_1607_updated_jan_2017_x86_dvd_9714393.iso": "f17f69a8fb6df79d83939811ac38dfee",

    "en_windows_10_multiple_editions_x64_dvd_6846432.iso": "23e397a21a9e01f141c64b7e1260314a",

    "en_windows_7_professional_with_sp1_x64_dvd_u_676939.iso": "ed15956fe33c13642a6d2cb2c7aa9749",
    "en_windows_7_professional_with_sp1_x86_dvd_u_677056.iso": "0bff99c8310ba12a9136e3d23606f3d4",
    "en_windows_7_professional_x64_dvd_x15-65805.iso": "7b7af5fe3a01e9fd76de4dacb45a796b",
    "en_windows_7_professional_x86_dvd_x15-65804.iso": "d8f675aaeb48057452666b0cd686d7f5",
    "en_windows_8.1_with_update_x64_dvd_6051480.iso": "e0d4594e56c0545d379340e0db9519a5",
    "en_windows_8.1_with_update_x86_dvd_6051550.iso": "46ce6553a0e0abc264b77c1fc59dfb29",
    "en_windows_8_1_x64_dvd_2707217.iso": "f104b78019e86e74b149ae5e510f7be9",
    "en_windows_8_1_x86_dvd_2707392.iso": "7dd36fea0d004acfedbdb3a5521ef5ff",
    "en_windows_8_x64_dvd_915440.iso": "0e8f2199fae18fe510c23426e68f675a",
    "en_windows_8_x86_dvd_915417.iso": "4252407333706df89a0c654924dd3f06",

    "en_windows_server_2008_r2_with_sp1_x64_dvd_617601.iso": "8dcde01d0da526100869e2457aafb7ca",
    "en_windows_server_2008_r2_x64_dvd_x15-50365.iso": "0ffbae83327f0ad8c2ab4d5dfa754c09",

    "en_windows_server_2012_r2_with_update_x64_dvd_6052708.iso": "78bff6565f178ed08ab534397fe44845",
    "en_windows_server_2012_r2_x64_dvd_2707946.iso": "0e7c09aab20dec3cd7eab236dab90e78",
    "en_windows_server_2012_x64_dvd_915478.iso": "da91135483e24689bfdaf05d40301506",
    "en_windows_server_2016_x64_dvd_9718492.iso": "e02d2e482b0f3dab915435e9040c13b4",
}

not_working = {
    # "en_win_srv_2003_r2_standard_cd2.iso": "8985b1c1aac829f0d46d6aae088ecd67",
    # "en_win_srv_2003_r2_standard_with_sp2_cd1_x13-04790.iso": "7c2e96e050d14def056e62d806da79e1",
    # "en_win_srv_2003_r2_standard_with_sp2_cd2_x13-68583.iso": "099b4dea552813fbf07bc202cfbca39d",
    # "en_win_srv_2003_r2_standard_x64_cd1.iso": "e7c31ef556396da7e2aa9a8f3c2ca7c3",
    # "en_win_srv_2003_r2_standard_x64_cd2.iso": "917a53630b81f7e3364e3c651118f319",
    # "en_win_srv_2003_r2_standard_x64_with_sp2_cd1_x13-05757.iso": "384f54fbd0f3524d4cc262f5892de230",
    # "en_win_srv_2003_r2_standard_x64_with_sp2_cd2_x13-68587.iso": "f0dc235b52daa9a36de90c93703c466d",

    # "en_windows_10_multiple_editions_version_1511_updated_feb_2016_x64_dvd_8379634.iso": "a4fde74732557d75ffc5354d0271832e",

    # "en_windows_10_multiple_editions_version_1703_updated_march_2017_x64_dvd_10189288.iso": "effccfda8a8dcf0b91bb3878702ae2d8",
    # "en_windows_10_multiple_editions_version_1703_updated_march_2017_x86_dvd_10188977.iso": "6c8bd404dd95a286b3b3ef3a90e2cb34",


    # "en_windows_server_2003_standard.iso": "332aee5cf2ab3000de1c6bd0ff4e25a1",
    # "en_windows_server_2003_standard_x64.iso": "d688d6ac0986a32d45b26e437a4259d2",
    # "en_windows_server_2003_with_sp1_standard.iso": "5e7232fda658dbff9195f2fd7a302793",

    # "en_windows_server_2008_with_sp2_x64_dvd_342336.iso": "e94943ef484035b3288d8db69599a6b5",
    # "en_windows_server_2008_with_sp2_x86_dvd_342333.iso": "b9201aeb6eef04a3c573d036a8780bdf",
    # "en_windows_server_2008_x64_dvd_x14-26714.iso": "27c58cdb3d620f28c36333a5552f271c",
    # "en_windows_server_2008_x86_dvd_x14-26710.iso": "0bfca49f0164de0a8eba236ced47007d",

    # windows XP needs default scsi in vmware fusion to detect drive
    # "en_windows_xp_professional_with_service_pack_3_x86_cd_x14-80428.iso": "f424a52153e6e5ed4c0d44235cf545d5",
    # "en_windows_xp_professional_x64.iso": "d089dd4e7529219186e355e0306e94b0",
    # "en_winxp_pro_with_sp2.iso": "5cc832a862c4075cf6bea6c6f0f69725",
    # "en_winxp_pro_x86_build2600_iso": "91b6f82efda6b4a8b937867f20f5011b"
}

for file_name in iso_map:
    build_base(file_name, iso_map[file_name])
