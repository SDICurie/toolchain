#!/bin/bash
#
# Copyright (C) 2015, Intel Corporation. All rights reserved.
#
# The source code, information and material ("Material") contained herein is owned by Intel Corporation
# or its suppliers or licensors, and title to such Material remains with Intel Corporation or its suppliers
# or licensors. The Material contains proprietary information of Intel or its suppliers and licensors.
# The Material is protected by worldwide copyright laws and treaty provisions. No part of the Material may be
# used, copied, reproduced, modified, published, uploaded, posted, transmitted, distributed or disclosed in
# any way without Intel's prior express written permission. No license under any patent, copyright or other
# intellectual property rights in the Material is granted to or conferred upon you, either expressly, by implication,
# inducement, estoppel or otherwise. Any license under such intellectual property rights must be express and approved
# by Intel in writing.
#
# Unless otherwise agreed by Intel in writing, you may not remove or alter this notice or any other notice embedded
# in Materials by Intel or Intel's suppliers or licensors in any way.
#

SCRIPT_PATH=$(readlink -f $0)
TARGET_DIR="/etc/udev/rules.d"

#     0 - success
# not 0 - fail
install_rules() {
    local rc=1
    local filepath="$(find $(dirname $0)/../debugger -type f -iname 99-openocd.rules | head -1)"
    if [ -f "$filepath" ]; then
        cp  -r "$filepath" "$TARGET_DIR" 1>/dev/null 2>&1
        rc=$?
    fi
    return $rc
}

if [ -w "$TARGET_DIR" ]; then
    if install_rules; then
        echo "Rules file was installed successfully."
    else
        echo "Rules file installation was failed."
    fi
    exit 0
fi

### handle non-root call ###
LOOP=1
while [ "1" = "$LOOP" ]; do
    echo "
Please make your selection by entering an option.
Root privileges are required to install OpenOCD udev rules.

1. Run as a root
2. Run using sudo privileges

q. Quit"

    read -p "Please type a selection: " usr_choice
    [ -z "$usr_choice" ] && usr_choice=1
    case $usr_choice in
        1 )
            sh -c "(exec su - -c \"sh $SCRIPT_PATH\")"
            if [ $? -ne 0 ]; then
                read -p "Login as root failed. Would you like to try again? [y] " usr_choice
                if [ -n "$usr_choice" ] && [ "y" != "$usr_choice" ]; then
                    echo "Exiting..."
                    exit 1
                fi
            else
                LOOP=0
            fi
            ;;
        2 )
            sh -c "(sudo su - -c \"sh $SCRIPT_PATH\")"
            if [ $? -ne 0 ]; then
                read -p "Login as sudo failed. Would you like to try again? [y] " usr_choice
                if [ -n "$usr_choice" ] && [ "y" != "$usr_choice" ]; then
                    echo "Exiting..."
                    exit 1
                fi
            else
                LOOP=0
            fi
            ;;
        q )
            exit 0   
            ;;
        * ) 
            read -p "Invalid choice. Press <Enter> and try again."
            ;;
    esac
done
