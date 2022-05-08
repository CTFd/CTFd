# Get Kali Up and Running

## Category: Basics

Kali Linux is an Operating System that has security tools preinstalled on it, we will be using it to get everyone up and running and not worry about downloading tools etc.

1. Download [VirtualBox](https://www.virtualbox.org/wiki/Downloads) on your computer.
2. Download the [kali.ova](https://drive.google.com/file/d/1STLzVHKL2EXC1MBgDC_VC0JYrjkZ51vk/view?usp=sharing) file.
3. Import the VM into VirtualBox and boot it up.
4. Log in
   **Username:** kali
    **Password:** supersecure
5. Install Guest Additions
   1. In the menu bar go to `Devices > Insert Guest Additions CD image...`
   2. Then in the VM run the following command `$ sudo bash /media/cdrom/VBoxLinuxAdditions.run`
      - Replace `cdrom` in the command with the location of where the additions CD is inserted, it could be `cdrom0`
6. Reboot the VM
7. There should be a `~/Desktop/flag.txt` file, read it for the flag


**Additional:**
In VBox in the VM settings you may want to do the following:
1. Under `General > Advanced` select `Shared Clipboard` and `Drag'n'Drop` to be Bidirectional, this will allow you to move files and copy and paste to/from the VM seamlessly.
2. Under `System > Motherboard` you may want to increase your RAM by setting `Base Memory` to 4GB (4096 MB).