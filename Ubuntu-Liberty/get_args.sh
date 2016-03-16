#! /bin/bash

HELP_TEXT="""
bomsi-iso version $BOMSI_ISO_VERSION for OpenStack release $BOMSI_ISO_RELEASE.
-i, --install_vm              Install a virtual machine with the created iso image
-n, --name=VM_NAME            Name for the quemu virtual machine being created.
-r, --root_password=Password  Root password for the kickstarted machine
-u, --create_usb=/dev/sdb     Create a bootable pendrive on the give device with the new ISO. disables VM
-g, --gatewayln               Last number of Gateway IP in management network (10.0.0.1 --> 1)
-d, --dnsln                   Last number of DNS IP in management network (10.0.0.1 --> 1)
-m, --netmask                 Netmask (def. 255.255.255.0)
--use_internet                Allow downloading packages from internet (def. NO)
--no_firstrun                 Do not execute the init.d script after reboot
--virt_nic_man=\"network=management\"
                              The name of the management network (or bridge) for VMs (i.e. \"bridge=br0\")
-v, --version                 Print version and exit
-V, --verbose                 Toggle verbose mode
-Q, --quiet                   Toggle quiet mode (no output)
-h, --help                    Print this help and exit

Default configurations are provided for any name (-n) containing controller, compute1, compute2, compute3, network, block, object or clean. Clean kickstarts a clean CentOS machine, i.e. for dowloading the packages with gather_packages for a full off-line installation.

Examples:
Create an ISO image with a boot menu which allows to select which machine is going to be installed:
./bomsi-iso.sh

Create the previous ISO image and test it on a virtual machine called \"1.controller\":
./bomsi-iso.sh -n=1.controller

Create an ISO for installing the first compute node and burn it onto a bootable pendrive:
(assuming the pendrive is inserted on the system and that it is on /dev/sdb)
(this also starts a (diskless) qemu test machine, to test that the pendrive works fine)
./bomsi-iso.sh -n=compute1 -u=/dev/sdb

"""


for i in "$@"
do
  case $i in
      -i|--install_vm)
        export INSTALL_VM=' '
        shift # next value in @
      ;;
      -n=*|--vm_name=*)
        export VM_NAME="${i#*=}"
        export INSTALL_VM=' '
        shift # past argument=value
      ;;
      -r=*|--root_password=*)
        #export ROOT_PASSWORD="${i#*=}"
        sustivar "ROOT_PASSWORD=${i#*=}"
        shift 
      ;;
      -o=*|--output_iso_name=*)
        export OUT_ISO_NAME="${i#*=}"
        shift 
      ;;
      --no_firstrun)
        export NO_FIRSTRUN=""
        shift 
      ;;
      --use_internet)
        export INSTALL_FROM_INTERNET="YES"
        shift 
      ;;
      --virt_nic_man=*)
        export VIRT_NIC_MAN="${i#*=}"
        shift 
      ;;
      -u=*|--create_usb=*)
        export USB_DEV="${i#*=}"
        shift 
      ;;
      -g=*|--gatewayln=*)
        sustivar "GATEWAY_LN=${i#*=}"
        shift 
      ;;
      -d=*|--dnsln=*)
        sustivar "DNS_LN=${i#*=}"
        shift 
      ;;
      -v|--version)
        echo "$BASH_ARGV version $VERSION"
        exit
      ;;
      -V|--verbose)
        export SILENCER=''
        shift # next value in @
      ;;
      -Q|--quiet)
        export MUTE=' '
        export SILENCER=' &> /dev/null '
        shift # next value in @
      ;;
      -h|--help|*)
        echo "$HELP_TEXT"
        exit
      ;;
      *)
              # unkonwn options 
      ;;
  esac
done

