#!/bin/bash

# Execute as user to install TEX from REF after root.sh

if [ "$(id -u)" -eq 0 ]; then
    echo "[-] this script must be run as simple user"
    exit 1
fi

if [ -e ~/.config/Code ]; then
    ln -s /usr/share/myspell/dicts/* ~/.config/Code/Dictionaries || exit 1
fi
