chocolatey feature enable -n=allowGlobalConfirmation
set ChocolateyUrlOverride=http://web.archive.org/web/20180206051312/https://www.python.org/ftp/python/2.7.11/python-2.7.11.msi
set ChocolateyUrl64bitOverride=http://web.archive.org/web/20180206051312/https://www.python.org/ftp/python/2.7.11/python-2.7.11.amd64.msi
choco install python --version 2.7.11
chocolatey feature disable -n=allowGlobalConfirmation
