chocolatey feature enable -n=allowGlobalConfirmation
choco install python --version 2.7.11
chocolatey feature disable -n=allowGlobalConfirmation
exit
