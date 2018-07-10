chocolatey feature enable -n=allowGlobalConfirmation
set ChocolateyUrlOverride=https://baseline-builder.s3.amazonaws.com/python-2.7.11.msi
set ChocolateyUrl64bitOverride=https://baseline-builder.s3.amazonaws.com/python-2.7.11.amd64.msi
choco install python --version 2.7.11
chocolatey feature disable -n=allowGlobalConfirmation
