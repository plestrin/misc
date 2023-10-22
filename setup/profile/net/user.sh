#!/bin/bash

# Execute as user to install NET from REF after root.sh

SCRIPT_PATH=$(cd -- "$(dirname "$0")" > /dev/null 2>&1; pwd -P)
ROOT_PATH=${SCRIPT_PATH}/../../

source "${ROOT_PATH}/shared_user.sh" || exit 1

setup_user_basic_graphic || exit 1
setup_user_export_alias || exit 1
