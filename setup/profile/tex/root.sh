#!/bin/bash

# Execute as root to install TEX from REF

SCRIPT_PATH=$(cd -- "$(dirname "$0")" > /dev/null 2>&1; pwd -P)
ROOT_PATH=${SCRIPT_PATH}/../../

source "${ROOT_PATH}/shared_root.sh" || exit 1

setup_root_apt_update
hostnamectl set-hostname "tex-deb${VERSION}-64" || exit 1
setup_root_basic_graphic || exit 1
setup_root_apt_install  \
    evince              \
    apt-transport-https \
    gpg                 \
    texlive             \
    texlive-lang-french \
    texlive-latex-extra \
    texlive-fonts-extra \
    git                 \
    hunspell-en-us      \
    hunspell-fr || exit 1
setup_root_lightdm_auto "$(id -un 1000)" || exit 1
setup_root_vscode || exit 1
setup_root_motd "TEX DEB${VERSION}-64" || exit 1
