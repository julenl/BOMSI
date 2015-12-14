
gen_ks (){
  ## Generate specific kickstart files for each machine

[ -f ./bomsi_vars ] && . ./bomsi_vars

## By default, only the core system will be installed.
## Additional services including cinder, swift, heat or ceilometer can be added as a space separated string
## in the SERVICES_LIST to enable their installation in the controller
## The options include any permutation with: cinder swift heat and ceilometer (some might not work 100% )
SERVICES_LIST="heat"




## Edit the boot menu

TMPF=$OUT_DIR/files/isolinux/isolinux.cfg
# Make first menu timeout to $BOOT_TIMEOUT seconds
sed -i "s/timeout 600/timeout $BOOT_TIMEOUT/" $TMPF
sed -i 's/menu title CentOS 7/menu title BOMSI installer for OpenStack Kilo on CentOS 7/' $TMPF
sed -i "s/menu rows 18/menu rows 25/" $TMPF  # Make menu a little bigger vertically

# Remove the default flag from the "test this media" option
tac $TMPF | sed '0,/menu default/{/ menu default/d}' | tac > /tmp/tmpf
mv /tmp/tmpf $TMPF


## Try to set boot menu to auto select the right option
for NODE in controller compute1 compute2 compute3 network block object;
  do
    #echo "NODE" $NODE
    if [[ $VM_NAME == *"$NODE"* ]]; then
      declare "KS_$NODE"=' menu default \n'
      echo ">> The \'$NODE\' node will be set as default on the installer menu" 
      KS_SET="YES"
    fi
  done

## If the default option was not set at all ("KS_SET=YES") set clean machine as default
[ -z ${KS_SET+x} ] && KS_clean=' menu default \n'

## If clean install performed, do not run the install scripts after first reboot
[ ! -z ${KS_clean+x} ] && export NO_FIRSTRUN=""


## Add options to kickstart each machine
sed -i "s/label linux/\
label KS Controller \n\
 menu label ^Kickstart controller \n\
$KS_controller\
 kernel vmlinuz \n\
 append initrd=initrd.img inst.stage2=hd:LABEL=CentOS7 inst.ks=hd:LABEL=CentOS7:\/ks\/ks-cont.cfg \n\n\
label KS compute1 \n\
 menu label Kickstart ^1st Compute node\n\
$KS_compute1\
 kernel vmlinuz\n\
 append initrd=initrd.img inst.stage2=hd:LABEL=CentOS7 inst.ks=hd:LABEL=CentOS7:\/ks\/ks-comp1.cfg \n\n\
label KS compute2\n\
 menu label Kickstart ^2nd Compute node\n\
$KS_compute2\
 kernel vmlinuz\n\
 append initrd=initrd.img inst.stage2=hd:LABEL=CentOS7 inst.ks=hd:LABEL=CentOS7:\/ks\/ks-comp2.cfg \n\n\
label KS compute3\n\
 menu label Kickstart ^3rd Compute node\n\
$KS_compute3\
 kernel vmlinuz\n\
 append initrd=initrd.img inst.stage2=hd:LABEL=CentOS7 inst.ks=hd:LABEL=CentOS7:\/ks\/ks-comp3.cfg \n\n\
label KS network\n\
 menu label Kickstart ^Network node\n\
$KS_network\
 kernel vmlinuz\n\
 append initrd=initrd.img inst.stage2=hd:LABEL=CentOS7 inst.ks=hd:LABEL=CentOS7:\/ks\/ks-net.cfg \n\n\
label KS block\n\
 menu label Kickstart ^Block Storage node\n\
$KS_block\
 kernel vmlinuz\n\
 append initrd=initrd.img inst.stage2=hd:LABEL=CentOS7 inst.ks=hd:LABEL=CentOS7:\/ks\/ks-block.cfg \n\n\
label KS object\n\
 menu label Kickstart ^Object Storage node\n\
$KS_object\
 kernel vmlinuz\n\
 append initrd=initrd.img inst.stage2=hd:LABEL=CentOS7 inst.ks=hd:LABEL=CentOS7:\/ks\/ks-object.cfg \n\n\
label KS Clean Node\n\
 menu label Kickstart Clean Node (i.e. for package downloading)\n\
$KS_clean\
 kernel vmlinuz\n\
 append initrd=initrd.img inst.stage2=hd:LABEL=CentOS7 inst.ks=hd:LABEL=CentOS7:\/ks\/ks-clean.cfg \n\n\
label linux/
" $TMPF

## Modify the label of the non-kickstarted option
sed -i 's/LABEL=CentOS\\x207\\x20x86_64/LABEL=CENTOS7/' $TMPF



OUT_PREF_KS=$OUT_DIR/files/ks    # Output prefix (PATH) for kickstart files
OUT_PREF_PI=$OUT_DIR/files/postinstall  # Output prefix (PATH) for postinstall scripts
mkdir -p $OUT_PREF_PI/node_scripts



if [[ "$SERVICES_LIST" == *"cinder"* ]]; then
   CINDER_CONT_STR="install_cinder_controller"

elif [[ "$SERVICES_LIST" == *"swift"* ]]; then
   SWIFT_CONT_STR="""
   while ! nmap -p 873 object |grep rsync |grep open; do sleep 2 && echo 'waiting for rsync on object' ; done && \
   install_swift_controller && \
   while ! ls /etc/swift/account.ring.gz ; do sleep 2 && echo 'waiting for SWIFT RINGS' ; done && \
   finalize_swift_installation && \
   sshpass -p $ROOT_PASSWORD ssh -o \"StrictHostKeyChecking no\" object touch /tmp/GREEN_LIGHT_TO_START_NODE"""

elif [[ "$SERVICES_LIST" == *"heat"* ]]; then
   HEAT_CONT_STR="install_heat &> /tmp/A13.install_heat_cont && heat_template "

fi

FULL_SERVER_LIST="controller compute1 compute2 compute3 network block object clean"
for HOST in $FULL_SERVER_LIST
 do 
  ## Set content of post-install
  NAME_HOST=${HOST}
  if [[ "$NAME_HOST" = "controller" ]]; then
     IP=$IPPR_A$CONT_LN
     OUT_FILE_KS=$OUT_PREF_KS/ks-cont.cfg
     POST_SCRIPT="""

      controller_bund

      $CINDER_CONT_STR &> /tmp/A10.install_cinder_cont

      #while ! nmap -p 873 object |grep rsync |grep open; do sleep 2 && echo 'waiting for rsync on object' ; done && \
      $SWIFT_CONT_STR &

         #install_swift_controller &>/tmp/A11.install_swift_cont && \
         #finalize_swift_installation &>/tmp/A12.install_cinder_cont && \
         #sshpass -p $ROOT_PASSWORD ssh -o \"StrictHostKeyChecking no\" object touch /tmp/GREEN_LIGHT_TO_START_NODE &

      $HEAT_CONT_STR
         #install_heat &> /tmp/A13.install_heat_cont
         #heat_template
     """
  elif [[ "$NAME_HOST" = "compute1" ]]; then
     IP=$IPPR_A"31"
     OUT_FILE_KS=$OUT_PREF_KS/ks-comp1.cfg
     POST_SCRIPT="""
     basic_net_tunnel  \${IPPR_T}31 $IFACE1
     basic_net_storage \${IPPR_S}31 $IFACE2
     while ! nmap -p 3306 controller |grep mysql |grep open; do sleep 2 && echo 'waiting for Rabbitmq in controller' ; done
     install_nova_node
     install_nova_node_neutron
     """
  elif [[ "$NAME_HOST" = "compute2" ]]; then
     IP=$IPPR_A"32"
     OUT_FILE_KS=$OUT_PREF_KS/ks-comp2.cfg
     POST_SCRIPT="""
     basic_net_tunnel  \${IPPR_T}32 $IFACE1
     basic_net_storage \${IPPR_S}32 $IFACE2
     install_nova_node
     install_nova_node_neutron
     """
  elif [[ "$NAME_HOST" = "compute3" ]]; then
     IP=$IPPR_A"33"

     POST_SCRIPT="""
     basic_net_tunnel  \${IPPR_T}33 $IFACE1
     basic_net_storage \${IPPR_S}33 $IFACE2
     install_nova_node
     install_nova_node_neutron
     """
  elif [[ "$NAME_HOST" = "network" ]]; then
     IP=$IPPR_A$NEUTRON_LN
     OUT_FILE_KS=$OUT_PREF_KS/ks-net.cfg
     POST_SCRIPT="""
     basic_net_tunnel  \${IPPR_T}21 $IFACE1
     #yum -y install net-tools
     basic_net_ext $IFACE_EXT
     install_neutron_node
     configure_openvswitch
     """
  elif [[ "$NAME_HOST" = "block" ]]; then
     IP=$IPPR_A"41"
     OUT_FILE_KS=$OUT_PREF_KS/ks-block.cfg
     POST_SCRIPT="""
     basic_net_storage  \${IPPR_S}41 $IFACE1
     install_cinder_node
     """
  elif [[ "$NAME_HOST" = "object" ]]; then
     IP=$IPPR_A"51"
     OUT_FILE_KS=$OUT_PREF_KS/ks-object.cfg
     POST_SCRIPT="""
     basic_net_storage  \${IPPR_S}51 $IFACE1
     install_swift_node
     create_swift_rings  &>/tmp/O2.create_swift_rings
     while ! ls /tmp/GREEN_LIGHT_TO_START_NODE ; do sleep 2 && echo 'waiting to start swift node' ; done
     start_swift_node
     """
  #elif [[ "$NAME_HOST" = "clean" ]]; then
  else
     IP=$IPPR_A"254"
     OUT_FILE_KS=$OUT_PREF_KS/ks-clean.cfg
     POST_SCRIPT=" "
     ## If the $PKG_DIR does not exist or does not contain more than 500 packages
     ## kickstart a VM for downloading the packages as default in boot menu
     if ! ls -l $PKG_DIR > /dev/null; then
      INSTALL_FROM_INTERNET="YES"
      PKGS_IN_DIR=$(ls -l $PKG_DIR |wc -l) &> /dev/null 
       if [ "${PKGS_IN_DIR:-0}" -lt 500 ]; then
         for i in "${!VAR*}"; do unset $i; done #Unset previous "defaults"
         KS_clean=' menu default \n' 
         export NO_FIRSTRUN=""   # Do not execute anything (installer) after reboot.
       fi
     fi 
  fi

  echo "#! /bin/bash" > $OUT_PREF_PI/node_scripts/setup-$NAME_HOST
  echo ". /tmp/bomsi_vars" >> $OUT_PREF_PI/node_scripts/setup-$NAME_HOST
  echo ". /tmp/bomsi_lib_conf" >> $OUT_PREF_PI/node_scripts/setup-$NAME_HOST
  echo ". /tmp/bomsi_lib_vm" >> $OUT_PREF_PI/node_scripts/setup-$NAME_HOST
  echo "$POST_SCRIPT"  >> $OUT_PREF_PI/node_scripts/setup-$NAME_HOST
  chmod +x $OUT_PREF_PI/node_scripts/setup-$NAME_HOST

  ## Script to run only on first boot, containing the different installers
  if [[ "$NAME_HOST" != "clean" ]]; then
  cat > $OUT_PREF_PI/firstrun_$NAME_HOST << EOF
#!/bin/bash
#
# Calling BOMSI for $NAME_HOST node
# 
# chkconfig: 345 90 10
# description: Calling BOMSI for $NAME_HOST 

case "\$1" in
  start)
    echo "\$\$" > /root/$NAME_HOST-init.d.pid  #PID of this init.d script
    
    . /tmp/bomsi_vars
    . /tmp/bomsi_lib_conf
    . /tmp/bomsi_lib_vm
    N=1
    while ! ping -c1 centos.org; do sleep 1 && N=[$N+1] && echo $N `date` > ~/wait.log ; done
    yum -y install http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
    yum -y install http://rdo.fedorapeople.org/openstack-kilo/rdo-release-kilo.rpm    
    yum -y update
    yum -y upgrade
    yum -y install openstack-selinux selinux-policy deltarpm yum-utils python-chardet python-kitchen ntp yum-plugin-priorities audit-libs-python checkpolicy libcgroup libsemanage-python policycoreutils-python python-IPy setools-libs net-tools nmap sshpass
    #yum -y install epel-release rdo-relase-kilo

    [[ \$FULL_SERVER_LIST =~ \$HOSTNAME ]] && echo 'yes' 
    /root/postinstall/node_scripts/setup-\$HOSTNAME |tee /root/node_script.log    
    touch ~/HOST_COMPLETED-$NAME_HOST
    chmod -x /etc/init.d/firstrun_$NAME_HOST
    chkconfig firstrun_$NAME_HOST off
  ;;
  stop|status|restart|reload|force-reload)
    # do nothing
  ;;
esac
EOF
fi


## If NO_FIRSTRUN is set, do not activate firstrun script
if [ ! -z ${NO_FIRSTRUN+x} ]; then
 #echo "Not executing /etc/init.d/firstrun_$NAME_HOST on next boot"
 FIRSTRUN_EXE_STR=''
else
 #echo "Executing firstrun script as /etc/init.d/firstrun_$NAME_HOST"
 FIRSTRUN_EXE_STR="chkconfig --add firstrun_$NAME_HOST on
 chkconfig --level 345 firstrun_$NAME_HOST on"
fi


if [ ! -z ${USE_INTERNET+x} ]; then # if var is unset
 INSTALL_FROM_INTERNET="YES"
fi

## If INSTALL_FROM_INTERNET was set, "use network installation
if [ ! -z ${INSTALL_FROM_INTERNET} ]; then
  USE_NETWORK_INSTALLATION="""# Use network installation
 url --url=\"http://mirror.centos.org/centos/7/os/x86_64/\" """
fi




PASSWORD=$(openssl passwd -1 "$ROOT_PASSWORD")
cat > $OUT_FILE_KS << EOF
#version=RHEL7
# System authorization information
auth --enableshadow --passalgo=sha512

# Use CDROM installation media
cdrom
$USE_NETWORK_INSTALLATION

# Use graphical/text/cmdline install
graphical

# SELinux configuration
#selinux disabled

# Installation logging level info/debug
#logging level=debug


# Run the Setup Agent on first boot
firstboot --enable
ignoredisk --only-use=$HD
# Keyboard layouts
keyboard --vckeymap=us --xlayouts='us'
# System language
lang en_US.UTF-8 --addsupport=de_DE.UTF-8

# Network information
#network --bootproto=static --device=$IFACE0 --ip=$IP --netmask=$NETMASK --gateway=$GATEWAY --nameserver=$NAMESERVER --activate --hostname=$NAME_HOST
# Set the given parameters on the first device with active link found
network --bootproto=static --device=link  --ip=$IP --netmask=$NETMASK --gateway=$GATEWAY --nameserver=$NAMESERVER --activate --hostname=$NAME_HOST
# Root password
rootpw --iscrypted $PASSWORD
# System timezone
timezone Europe/Berlin --isUtc 
# System bootloader configuration
bootloader --append=" crashkernel=auto" --location=mbr --boot-drive=$HD
autopart --type=lvm
# Partition clearing information
clearpart --all --initlabel --drives=$HD


#repo --name=<repoid> [--baseline=<url>| --mirrorlist=<url>]

#Reboot after installation?
reboot

%packages
@core
kexec-tools
chrony


%end


%post --nochroot
#!/bin/sh

set -x -v
exec 1>/mnt/sysimage/root/kickstart-stage1.log 2>&1

echo "==> copying files from media to install drive..."
cp -r /run/install/repo/postinstall /mnt/sysimage/root
cp -r /run/install/repo/postinstall/hosts /mnt/sysimage/etc/
cp -r /run/install/repo/postinstall/bomsi_* /mnt/sysimage/tmp/
mv /mnt/sysimage/tmp/bomsi_susti.py /mnt/sysimage/tmp/susti
chmod +x /mnt/sysimage/tmp/susti

#cp -r /run/install/repo/postinstall/firstrun_$NAME_HOST /mnt/sysimage/etc/init.d/

## Create and add a local repository located in /root/LocalRepo/
cp -r /mnt/sysimage/root/postinstall/localrepo.repo /mnt/sysimage/etc/yum.repos.d/localrepo.repo
mkdir -p /mnt/sysimage/root/LocalRepo
cp -r /run/install/repo/Packages /mnt/sysimage/root/LocalRepo
createrepo -v /mnt/sysimage/root/LocalRepo

%end



%post
#!/bin/sh
set -x -v
exec 1>/root/kickstart-stage2.log 2>&1

echo "export PATH=\$PATH:/tmp" >> /etc/profile
#systemctl enable sshd
#systemctl start sshd

cp -r /root/postinstall/firstrun_$NAME_HOST /etc/init.d/
chmod +x /etc/init.d/firstrun_$NAME_HOST
chcon system_u:object_r:initrc_exec_t:s0 /etc/init.d/firstrun_$NAME_HOST

$FIRSTRUN_EXE_STR
#chkconfig --add firstrun_$NAME_HOST on 
#chkconfig --level 345 firstrun_$NAME_HOST on

#/etc/init.d/firstrun_$NAME_HOST start

%end
EOF

done

echo ">> gen_ks done"

}


