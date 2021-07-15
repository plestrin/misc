#!/bin/bash

# Execute as root to install TEX from DEV

hostnamectl set-hostname tex-deb10-64

apt-get update
apt-get dist-upgrade -y
apt-get install -y evince apt-transport-https gpg texlive texlive-lang-french texlive-latex-extra texlive-fonts-extra git hunspell-en-us hunspell-fr

if [ ! -e /etc/apt/sources.list.d/vscode.list ]; then
    if [ ! -e /etc/apt/trusted.gpg.d/packages.microsoft.gpg ]; then
        wget -q -O - https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/packages.microsoft.gpg
        install -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/trusted.gpg.d/
    fi
    echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list
    apt-get update
fi

apt-get install -y code

echo -e '\n********************\n*** TEX DEB10-64 ***\n********************\n' > /etc/motd
