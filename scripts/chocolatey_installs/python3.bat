chocolatey feature enable -n=allowGlobalConfirmation
choco install python --version 3.6.1
chocolatey feature disable -n=allowGlobalConfirmation
exit
