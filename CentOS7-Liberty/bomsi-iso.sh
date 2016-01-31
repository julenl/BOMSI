#! /bin/bash 
#set -e  #for debuging
#set -x 
export BOMSI_ISO_RELEASE="Liberty"
export BOMSI_ISO_VERSION="0.1"
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

[ -f $THISD/bomsi_vars ] && . $THISD/bomsi_vars

## Parse command line options
CMDL_VARS="$@"
source get_args.sh

## VARIABLES (if the are not set, they'll get default values)
[ -z ${ROOT_PASSWORD+x} ] || ROOT_PASSWORD="1234" #Root/User password for CentOS

export BOOT_TIMEOUT="100"   # time until the iso bootloaders loads the default option (seconds x10)
export OUT_DIR="/tmp/custom_iso"
export OUT_ISO_DIR="$HOME"  
export PKG_DIR="$HOME/centos_packages"
export PATH_TO_ISO="$HOME/ISOS/CentOS-7-x86_64-Minimal-1503-01.iso"
[ -z ${OUT_ISO_NAME+x} ] && OUT_ISO_NAME="BOMSI-${VM_NAME}.iso"
[ ! -z ${HD+x} ] || export HD="vda" # name of the disk where the system will be installed

[ ! -z ${VCPUS+x} ] || export VCPUS=2 # No. of virtual CPUs for each test VM
[ ! -z ${VRAM+x} ]  || export VRAM=4092 # Mb of RAM for test VMs i.e. 8192


export NETMASK="255.255.255.0"

export DS=5 # root virtual HD Size of 5 Gb. Minimum 4 Gb, recommended 8
export DS_B=2 # virtual HD Size of 4 Gb for block storage
export DS_O=2 # virtual HD Size of 2 Gb for object storage


## Make sure isos are umounted and remove the files from previous runs
df -h |grep /dev/loop0 > /dev/null && sudo umount /dev/loop0
df -h |grep /dev/loop1 > /dev/null && sudo umount /dev/loop1
sudo rm -rf $OUT_DIR/files
sudo rm -rf $OUT_DIR/*comps*



mkdir -p $OUT_DIR/files/{ks,postinstall}

## If original ISO file does not exist, get one:
#wget ftp://mirror.fraunhofer.de/centos.org/7/isos/x86_64/CentOS-7-x86_64-Minimal-1503-01.iso ~/ISOS
## Otherwise use some other mirror closer to your location
which curl > /dev/null || sudo apt-get -y install curl >> /tmp/installed_by_bomsi.log
if [ ! -f $PATH_TO_ISO ]; then
  mkdir -p ${PATH_TO_ISO%/*} > /dev/null 
  curl -o $PATH_TO_ISO  ftp://mirror.fraunhofer.de/centos.org/7/isos/x86_64/CentOS-7-x86_64-Minimal-1503-01.iso
fi
 
    


mkdir -p /tmp/mountiso/
echo '>> Root password is required for mounting the iso image.'
sudo mount -o loop $PATH_TO_ISO /tmp/mountiso/ &> /dev/null

echo ">> Copying the contents of the iso file in /tmp/mountiso/ into $OUT_DIR/custom_iso/files/"
rsync -a /tmp/mountiso/ $OUT_DIR/files/

COMPS=$(ls -l /tmp/mountiso/repodata/ | grep -i comps.xml.gz |awk '{print $9}')
rm -rf $OUT_DIR/files/repodata/*comps*
cp /tmp/mountiso/repodata/$COMPS $OUT_DIR/
cd $OUT_DIR/files/
gunzip  $OUT_DIR/*-comps.xml.gz
#unalias mv
mv -f $OUT_DIR/*comps.xml $OUT_DIR/comps.xml



## Script that downloads all OpenStack packages to another CentOS 7 machine
## and copies them to the local $PKG_DIR (def. ~/centos_packages) directory

chmod +x $THISD/gather_packages_os.sh
#$THISD/gather_packages_os.sh 



echo ">> Copying packages from $PKG_DIR/ to $OUT_DIR/files/Packages/ "
rsync -a $PKG_DIR/ $OUT_DIR/files/Packages/ &> /tmp/rsync.log ||echo "WARNING: Probably $PKG_DIR/ does not exist. Packages will be downloaded fully from the internet" #&& exit


## Generate Kickstart files
echo ">> Generating kickstart files"
chmod +x $THISD/gen_ks.sh 
. $THISD/gen_ks.sh
gen_ks

# Uncomment the "priority" line if the local pkgs are really updated
cat > $OUT_DIR/files/postinstall/localrepo.repo << EOF
[localrepo]
name=Local Repository
baseurl=file:///root/LocalRepo
gpgcheck=0
enabled=1
#priority=1
EOF

cat > $OUT_DIR/files/postinstall/hosts << EOF
${IPPR_A}$CONT_LN controller
${IPPR_A}$NEUTRON_LN network   
${IPPR_A}31 compute1  
${IPPR_A}32 compute2  
${IPPR_A}33 compute3  
${IPPR_A}$CINDER_LN block     
${IPPR_A}$SWIFT_LN object    
EOF


cp -r $THISD/bomsi* $OUT_DIR/files/postinstall/



which createrepo > /dev/null || sudo apt-get -y install createrepo genisoimage >> /tmp/installed_by_bomsi.log

echo ">> Creating repository index in $OUT_DIR/comps.xml... "
cd $OUT_DIR/files
createrepo -g $OUT_DIR/comps.xml . &> /dev/null

cd $OUT_DIR
chmod 664 $OUT_DIR/files/isolinux/isolinux.bin


rm -rf $OUT_DIR/$OUT_ISO_NAME

echo ">> Generating ISO image in $OUT_DIR/$OUT_ISO_NAME ... " 
sudo /usr/bin/genisoimage -untranslated-filenames -volid 'CentOS7' \
         -J -joliet-long -rational-rock -translation-table -input-charset utf-8 \
         -x ./lost+found -b isolinux/isolinux.bin -c isolinux/boot.cat \
         -no-emul-boot -boot-load-size 4 -boot-info-table \
         -eltorito-alt-boot -e images/efiboot.img -no-emul-boot \
         -o $OUT_ISO_DIR/$OUT_ISO_NAME \
         -T $OUT_DIR/files/  &> /dev/null

which isohybrid > /dev/null|| sudo apt-get -y install syslinux >> /tmp/installed_by_bomsi.log || sudo apt-get -y install syslinux-utils >> /tmp/installed_by_bomsi.log
sudo isohybrid --uefi $OUT_ISO_DIR/$OUT_ISO_NAME #&> /dev/null


[ $? == 0 ] && echo "The ISO \"$OUT_ISO_NAME\" was generated succesfully in $OUT_ISO_DIR."


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
  . $THISD/bomsi_lib_vm 
  start_iso_vm 
fi

