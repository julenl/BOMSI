#! /bin/bash
#set -e  #for debuging
#set -x 
export BOMSI_ISO_RELEASE="Liberty"
export BOMSI_ISO_VERSION="0.1"
export BOMSI_ISO_OPSYS="Ubuntu"
## 
## This file is the main driver of BOMSI, the Bash OpenStack Multinode Scripted Installer. 
## It calls the following libraries:
## - get_args.sh: parses command line arguments and returns the corresponding variables
## - lib/bomsi_vars: main variables, such as IPs, passwords, ...
## - lib/iso_kickstart: rebuilds the original ISO file into an automatic installer one
## - lib/start_iso_vm: starts a VM with the newly created ISO
##  the rest of the files on the lib/ directory are scripts for installing OpenStack
## 
##

echo " "
printf "  \033[0;34m### Starting BOMSI ###\n\033[0m"
echo " "

export THISD=${PWD}
echo ">> Loading bomsi variables from $THISD/lib/bomsi_vars"
[ -f $THISD/lib/bomsi_vars ] && . $THISD/lib/bomsi_vars

## Parse command line options
CMDL_VARS="$@"
source get_args.sh



## Ensure that all variables are loaded/defined

export BOOT_TIMEOUT="100"   # time until the iso bootloaders loads the default option (seconds x10)
export OUT_DIR="/tmp/custom_iso" # Dir. where the original ISO file is uncompressed and processed
export OUT_ISO_DIR="$HOME" # Dir. where the new ISO file is generated
export PATH_TO_ISO="$HOME/ISOS/ubuntu-15.10-server-amd64.iso"
#export PATH_TO_ISO="$HOME/ISOS/ubuntu-14.04.3-server-amd64.iso"

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
    PKG_UPDATE="sudo zypper -n update"
    PKGS="curl gettext-runtime mkisofs qemu-kvm libvirt virt-install libvirt-client bridge-utils acpid libvirt-python qemu "
    pkg_check () { rpm -q $1 ; }
    #PKG_CHECK="rpm -q "
    POST_PKGS='sudo systemctl status libvirtd > /dev/null || sudo systemctl enable libvirtd.service && sudo systemctl start libvirtd.service'
    KVM_GROUPS="libvirt kvm"

elif [ "$OP_SYS" == "Debian" ] || [ "$OP_SYS" == "Ubuntu" ]
  then
    PKG_CMD="sudo apt-get -y install "
    PKG_UPDATE="sudo apt-get -y update"
    pkg_installed () { dpkg -l $1 |grep "ii"; }
    #PKG_CHECK="dpkg -l "
    PKGS="curl gettext genisoimage dumpet qemu-kvm libvirt-bin bridge-utils acpid virtinst qemu-system " # virt-manager ubuntu-vm-builder 
    KVM_GROUPS="libvirtd kvm"

elif [ "$OP_SYS" == "CentOS" ] || [ "$OP_SYS" == "Red Hat" ]
  then
    PKG_CMD="sudo yum -y install "
fi

## Make sure all the packages are installed 
sudo -n ls &>/dev/null || \
printf '\033[0;37m>> Root password is required installing the packages\n\033[0m'

$PKG_UPDATE &> /dev/null
for PKG in $PKGS
  do
    if ! pkg_installed $PKG &> /dev/null; then
      echo ">>>> Installing $PKG"
      $PKG_CMD $PKG &> /tmp/bomsi_install.log
    #else
    #  echo "   $PKG is already installed"
    fi
  done

 [ -z "$POST_PKGS" ] || \
echo ">> Starting and enabling libvirtd (if necessary)" && \
echo $POST_PKGS && \
 eval "$POST_PKGS" # This enables libvirtd





## If the original ISO is not present, download it into the $PATH_TO_ISO directory
if [ ! -f $PATH_TO_ISO ]; then
  echo ">> Downloading ISO to: $PATH_TO_ISO"
  mkdir -p ${PATH_TO_ISO%/*} > /dev/null 
  curl -o $PATH_TO_ISO http://de.releases.ubuntu.com/15.10/ubuntu-15.10-server-amd64.iso
  #curl -o $PATH_TO_ISO http://de.releases.ubuntu.com/14.04.4/ubuntu-14.04.3-server-amd64.iso
fi

run_or_exit "[ -f $PATH_TO_ISO ]"


## Load and execute the function that downloads and rebuilds the custom ISO file
echo ">> Customizing the ISO file"
. lib/iso_kickstart
iso_kickstart

echo ">> The ISO file has been generated"


## The ISO is already created. Now, if $USB_DEV was defined it will install the ISO on that device
## if the $INSTALL_VM variable was defined at some point, it will load and run the start_iso_vm,
## which installs the ISO file into a Virtual Machine with virsh


## Copy (install) the newly created ISO into a pendrive

if [ ! -z ${USB_DEV+x} ]; then
  ## check if device is present
  run_or_exit "sudo fdisk -l |grep $USB_DEV"
  echo ">> clean the content of the pendrive"
  sudo dd if=/dev/zero of=$USB_DEV bs=512 count=1
  #echo -e "o\nn\np\n1\n\n\na\n1\nw" | sudo fdisk $USB_DEV
  echo " "
  echo ">> COPY THE ISO FILE TO THE PENDRIVE IN $USB_DEV "
  echo " "
  ## check if ISO file is present
  run_or_exit "[ -f $PATH_TO_ISO/$OUT_ISO_NAME ]"
  sudo dd if=$OUT_ISO_DIR/$OUT_ISO_NAME of=$USB_DEV bs=512 
  echo ">> Testing USB device"
  sudo qemu-system-x86_64 -enable-kvm -m 1024 -hda $USB_DEV
  unset INSTALL_VM
fi




## Load the ISO into a Virtual Machine with qemu

if [ -z ${INSTALL_VM+x} ]; then 
  echo ">> Not starting VM."; 
else
  run_or_exit "[ -f  $OUT_ISO_DIR/$OUT_ISO_NAME ]"
  echo ">> Starting VM with the ISO" 
  . $THISD/lib/start_iso_vm 
  start_iso_vm 
fi

run_or_exit "virsh list | grep $VM_NAME"
echo "BOMSI finished successfully"



