#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "[-] this script must be run as root"
    exit 1
fi

setup_root_apt_update() {
    apt-get update || return 1
    apt-get dist-upgrade || return 1
    apt-get autoremove -y || return 1
}

setup_root_apt_install() {
    apt-get update || return 1
    apt-get install -y "$@" || return 1
}

setup_root_basic_graphic() {
    setup_root_apt_install  \
        i3                  \
        j4-dmenu-desktop    \
        lightdm             \
        rxvt-unicode || return 1
}

setup_root_lightdm_auto() {
    sed -i "s/#autologin-user=$/autologin-user=$1/" /etc/lightdm/lightdm.conf
}

setup_root_vscode() {
    setup_root_apt_install wget || return 1
    if [ ! -e /etc/apt/sources.list.d/vscode.list ]; then
        if [ ! -e /etc/apt/trusted.gpg.d/packages.microsoft.gpg ]; then
            wget -q -O - https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/packages.microsoft.gpg
            install -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/trusted.gpg.d/
        fi
        echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list || return 1
    fi
    setup_root_apt_install code || return 1
}

setup_root_motd() {
    echo -e "\\n********************\\n*** $1 ***\\n********************\\n" > /etc/motd
}

VERSION=$(cut -d . -f 1 < /etc/debian_version)
