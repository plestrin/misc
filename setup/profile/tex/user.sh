#!/bin/bash

# Execute as user to install TEX from REF after root.sh

if [ "$(id -u)" -eq 0 ]; then
    echo "[-] this script must be run as simple user"
    exit 1
fi

ln -s /usr/share/myspell/dicts/* /home/user/.config/Code/Dictionaries
