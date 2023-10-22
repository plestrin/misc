#!/bin/bash

# Execute as root to install NET from REF

SCRIPT_PATH=$(cd -- "$(dirname "$0")" > /dev/null 2>&1; pwd -P)
ROOT_PATH=${SCRIPT_PATH}/../../

source "${ROOT_PATH}/shared_root.sh" || exit 1

setup_root_apt_update
hostnamectl set-hostname "net-deb${VERSION}-64" || exit 1
setup_root_basic_graphic || exit 1
setup_root_apt_install firefox-esr || exit 1
setup_root_lightdm_auto "$(id -un 1000)" || exit 1
setup_root_motd "NET DEB${VERSION}-64" || exit 1
