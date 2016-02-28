#! /bin/bash
#set -e  #for debuging
#set -x 
export BOMSI_ISO_RELEASE="Liberty"
export BOMSI_ISO_VERSION="0.1"
export BOMSI_ISO_OPSYS="Ubuntu"
## 
## This file is the main driver of BOMSI, the Bash OpenStack Multinode Scripted Installer. 
## It calls the following libraries:
## - bomsi_vars: main variables, such as IPs, passwords, ...
## - bomsi_lib_conf: library containing functions to install and configure OpenStack 
## - bomsi_lib_vm: library containing functions to handdle local (test) virtual machines and network settings
## - bomsi_susti.py: python (OK this is not BASH :P) script for handeling the ".ini" configuration files
## - gather_packages_os.sh: function for gathering all needed packages for off-line (or just faster) install
## - get_args.sh: command line argument parser for bomsi-iso.sh (i.e. ./bomsi-iso.sh -h)
## - gen_ks.sh: library for generating the kickstart and installation files for all machines
## - bomsi_os_test: library for testing and troubleshooting each OpenStack machine
## 
##



export THISD=${PWD}

[ -f $THISD/lib/bomsi_vars ] && . $THISD/lib/bomsi_vars

## Parse command line options
CMDL_VARS="$@"
source get_args.sh



## Ensure that all variables are loaded/defined

export BOOT_TIMEOUT="100"   # time until the iso bootloaders loads the default option (seconds x10)
export OUT_DIR="/tmp/custom_iso" # Dir. where the original ISO file is uncompressed and processed
export OUT_ISO_DIR="$HOME" # Dir. where the new ISO file is generated
#export PATH_TO_ISO="$HOME/ISOS/ubuntu-15.10-server-amd64.iso"
export PATH_TO_ISO="$HOME/ISOS/ubuntu-14.04.3-server-amd64.iso"

## If these variables were not set befor, set them now
[ -z ${ROOT_PASSWORD+x} ] && export ROOT_PASSWORD="1234" #Root/User password for the server
[ -z ${OUT_ISO_NAME+x} ] && export OUT_ISO_NAME="BOMSI-$VM_NAME.iso"
[ -z ${HD+x} ] && export HD="vda" # name of the disk where the system will be installed
[ -z ${VCPUS+x} ] && export VCPUS=2 # No. of virtual CPUs for each test VM
[ -z ${VRAM+x} ]  && export VRAM=4092 # Mb of RAM for test VMs i.e. 8192

export NETMASK="255.255.255.0"

export DS=5 # root virtual HD Size of 5 Gb. Minimum 4 Gb, recommended 8
export DS_B=2 # virtual HD Size of 4 Gb for block storage
export DS_O=2 # virtual HD Size of 2 Gb for object storage




##Detect Operative System
OP_SYS=$(awk '{print $1}' /etc/issue |head -1)
if [ "$OP_SYS" == "Welcome" ] # That's (open)SUSE
  then
    PKG_CMD="sudo zypper -n install "
    PKGS="curl gettext-tools mkisofs qemu-kvm libvirt libvirt-client bridge-utils acpid virt-manager kvm libvirt-python qemu "
    PKG_CHECK="rpm -q "
    POST_PKGS="sudo systemctl enable libvirtd.service && sudo systemctl start libvirtd.service"

elif [ "$OP_SYS" == "Debian" ] || [ "$OP_SYS" == "Ubuntu" ]
  then
    PKG_CMD="sudo apt-get -y install "
    PKG_CHECK="dpkg -l "
    PKGS="curl gettext mkisofs dumpet qemu-kvm libvirt-bin bridge-utils acpid virtinst virt-manager qemu-system" # ubuntu-vm-builder 

elif [ "$OP_SYS" == "CentOS" ] || [ "$OP_SYS" == "Red Hat" ]
  then
    PKG_CMD="sudo yum -y install "
fi

## Make sure all the packages are installed 
for PKG in $PKGS
  do
    if ! $PKG_CHECK $PKG > /dev/null; then
      echo ">>> Installing $PKG"
      $PKG_CMD $PKG > /tmp/bomsi_install.log
    fi
    $POST_PKGS # This enables libvirtd
  done





## If the original ISO is not present, download it into the $PATH_TO_ISO directory
#which curl > /dev/null || sudo apt-get -y install curl >> /tmp/installed_by_bomsi.log
if [ ! -f $PATH_TO_ISO ]; then
  mkdir -p ${PATH_TO_ISO%/*} > /dev/null 
  #curl -o $PATH_TO_ISO http://cdimage.ubuntu.com/lubuntu/releases/15.10/release/lubuntu-15.10-desktop-amd64.iso
  #curl -o $PATH_TO_ISO http://de.releases.ubuntu.com/15.10/ubuntu-15.10-server-amd64.iso
  curl -o $PATH_TO_ISO http://de.releases.ubuntu.com/14.04.4/ubuntu-14.04.3-server-amd64.iso
fi




## Load and execute the function that downloads and rebuilds the custom ISO file
. lib/iso_kickstart
iso_kickstart




## The ISO is already created. Now, if $USB_DEV was defined it will install the ISO on that device
## if the $INSTALL_VM variable was defined at some point, it will load and run the start_iso_vm,
## which installs the ISO file into a Virtual Machine with virsh


## Copy (install) the newly created ISO into a pendrive

if [ ! -z ${USB_DEV+x} ]; then
  echo ">> clean the content of the pendrive"
  sudo dd if=/dev/zero of=$USB_DEV bs=512 count=1
  #echo -e "o\nn\np\n1\n\n\na\n1\nw" | sudo fdisk $USB_DEV
  echo " "
  echo ">> COPY THE ISO FILE TO THE PENDRIVE IN $USB_DEV "
  echo " "
  sudo dd if=$OUT_ISO_DIR/$OUT_ISO_NAME of=$USB_DEV bs=512 
  echo ">> Testing USB device"
  sudo qemu-system-x86_64 -enable-kvm -m 1024 -hda $USB_DEV
  unset INSTALL_VM
fi




## Load the ISO into a Virtual Machine with qemu

if [ -z ${INSTALL_VM+x} ]; then 
  echo ">> Not starting VM."; 
else 
  . $THISD/lib/start_iso_vm 
  start_iso_vm 
fi





