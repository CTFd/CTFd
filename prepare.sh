#!/usr/bin/bash

# package manager variable
var_pm='none'

# package manager detection
apt-get --version &> /dev/null
if [ $? -eq 0 ]; then
    echo "[*] apt-get detected"
    var_pm='aptget'
fi
pacman --version &> /dev/null
if [ $? -eq 0 ]; then
    echo "[*] pacman detected"
    var_pm='pacman'
fi
zypper --version &> /dev/null
if [ $? -eq 0 ]; then
    echo "[*] zypper detected"
    var_pm='zypper'
fi
yum --version &> /dev/null
if [ $? -eq 0 ]; then
    echo "[*] yum detected"
    var_pm='yum'
fi
dnf --version &> /dev/null
if [ $? -eq 0 ]; then
    echo "[*] dnf detected"
    var_pm='dnf'
fi
emerge --version &> /dev/null
if [ $? -eq 0 ]; then
    echo "[*] emerge detected"
    var_pm='emerge'
fi

# Installation
echo "[*] Installation running"
case "$var_pm" in
    "aptget")
        sudo apt-get install build-essential python-dev python-pip libffi-dev -y
        pip install -r requirements.txt
        ;;
    "pacman")
        sudo pacman -S --needed --noconfirm base-devel python-pip libffi
        pip2 install --user -r requirements.txt
        ;;
    "zypper")
        echo "[*] zypper not supported yet"
        ;;
    "yum")
        echo "[*] yum not supported yet"
        ;;
    "dnf")
        echo "[*] dnf not supported yet"
        ;;
    "emerge")
        echo "[*] emerge not supported yet"
        ;;
    *)
        echo "invalid option"
        exit 1
esac
echo "[*] Installation done"
