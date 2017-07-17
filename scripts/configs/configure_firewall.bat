netsh advfirewall firewall add rule name="Open TCP Port 4444 for Meterpreter" dir=in action=allow protocol=TCP localport=4444
netsh advfirewall firewall add rule name="Open UDP Port 4444 for Meterpreter" dir=in action=allow protocol=UDP localport=4444
