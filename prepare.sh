#!/bin/sh

PS3='Please select your OS: '
options=("Debian" "ArchLinux" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "Debian")
            sudo apt-get install build-essential python-dev python-pip libffi-dev -y
	    pip install -r requirements.txt
	    break
            ;;
        "ArchLinux")
            sudo pacman -S --needed --noconfirm base-devel python-pip libffi
            pip2 install --user -r requirements.txt
	    break
            ;;
        "Quit")
            break
            ;;
        *) echo invalid option;;
    esac
done
