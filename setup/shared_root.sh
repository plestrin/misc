#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "[-] this script must be run as root"
    exit 1
fi

VERSION=$(cut -d . -f 1 < /etc/debian_version)

setup_root_vscode() {
    if [ ! -e /etc/apt/sources.list.d/vscode.list ]; then
        if [ ! -e /etc/apt/trusted.gpg.d/packages.microsoft.gpg ]; then
            wget -q -O - https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/packages.microsoft.gpg
            install -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/trusted.gpg.d/
        fi
        echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list
        apt-get update
    fi

    apt-get install -y code
}

setup_root_motd() {
    echo -e "\\n********************\\n*** $1 ***\\n********************\\n" > /etc/motd
}
