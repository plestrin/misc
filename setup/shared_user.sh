#!/bin/bash

if [ "$(id -u)" -eq 0 ]; then
    echo "[-] this script must be run as simple user"
    exit 1
fi

setup_user_basic_graphic() {
    cp "${ROOT_PATH}/data/Xresources" ~/.Xresources || return 1
    mkdir -p ~/.config/i3 || return 1
    cp "${ROOT_PATH}/data/i3config" ~/.config/i3/config || return 1
    echo -e '[Desktop]\nSession=i3\n' > ~/.dmrc || return 1
}

setup_user_vscode() {
    if dpkg-query -W hunspell > /dev/null 2>&1 && [ -e ~/.config/Code/Dictionaries ]; then
        ln -s /usr/share/myspell/dicts/* ~/.config/Code/Dictionaries || return 1
    fi
}

setup_user_export_alias() {
    alias > ~/.bash_aliases || return 1
}
