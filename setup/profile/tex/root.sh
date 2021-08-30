#!/bin/bash

# Execute as root to install TEX from REF

source ../../shared_root.sh

hostnamectl set-hostname tex-deb10-64

apt-get update
apt-get dist-upgrade -y
apt-get install -y evince apt-transport-https gpg texlive texlive-lang-french texlive-latex-extra texlive-fonts-extra git hunspell-en-us hunspell-fr

setup_root_vscode

setup_root_motd "TEX DEB10-64"
