import packer

packerfile = './windows_10_x64_1703.json'
exc = []
only = ['vmware-iso']
vars = {"iso_url": "./iso/en-gb_windows_10_multiple_editions_version_1703_updated_june_2017_x64_dvd_10725222.iso", "iso_checksum": "133aac5804e18b32ae9f74f37d1172aa", "autounattend": "./answer_files/windows/10/Autounattend.xml"}
#var_file = 'path/to/var/file'
packer_exec_path = '/Users/jmartin/bin/packer'

p = packer.Packer(packerfile, exc=exc, only=only, vars=vars,
                  var_file=var_file, exec_path=packer_exec_path)
p.build(parallel=True, debug=False, force=False)

