#! /bin/bash 

## gather_packages (Liberty)
# This script collects all the packages needed to install a full OpenStack Liberty environment
# which are not included on the "CentOS-7-Minimal" package.
# It connects to a (virtual/physical) machine which contains a clean CentOS 7 installation
# without any additionally installed packages and downloads all required packages together with
# their dependencies, and other useful config files and the cirros image, for testing.
# Tip: it is usefull to have clean installed (non updated) CentOS 7 VM, one can clone
# and execute this script on to.


## IP of the "temporal" clean installed machine, where packages will be downloaded
IPTMP=10.0.0.254

## If root password (for ssh loging) was not set, put some value here.
[ ! -z ${ROOT_PASSWORD+x} ] || ROOT_PASSWORD="1234"

echo 'Downloading updated packages for the basic Operative System'
sshpass -p $ROOT_PASSWORD ssh root@$IPTMP yum -y update --downloadonly --downloaddir /tmp/tmp-pkg/ $PKG &> /dev/null

echo "Check if sshpass is installed, if not install it."
which sshpass &> /dev/null || sudo apt-get install sshpass

OSTACK_PACKAGES="""
http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
centos-release-openstack-liberty
deltarpm ntp yum-plugin-priorities
yum-utils htop vim net-tools wget which sshpass telnet nmap-ncat bind-utils
openstack-selinux selinux-policy
policycoreutils-python
mariadb mariadb-server MySQL-python
rabbitmq-server librabbitmq-tools
openstack-keystone httpd mod_wsgi python-openstackclient memcached python-memcached
openstack-glance python-glance python-glanceclient
openstack-nova-api openstack-nova-cert openstack-nova-conductor
openstack-nova-console openstack-nova-novncproxy openstack-nova-scheduler
python-novaclient 
openstack-nova-compute sysfsutils
openstack-neutron openstack-neutron-linuxbridge ebtables ipset
openstack-neutron openstack-neutron-ml2 openstack-neutron-linuxbridge python-neutronclient ebtables ipset
openstack-neutron  openstack-neutron-ml2 python-neutronclient openstack-neutron
openstack-neutron-ml2 openstack-neutron-openvswitch
openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch
openstack-dashboard
openstack-cinder python-cinderclient python-oslo-db
lvm2
openstack-cinder targetcli python-oslo-db python-oslo-log MySQL-python
openstack-cinder targetcli python-oslo-db MySQL-python
openstack-swift-proxy python-swiftclient python-keystone-auth-token python-keystonemiddleware memcached 
xfsprogs rsync
openstack-swift-account openstack-swift-container openstack-swift-object
openstack-heat-api openstack-heat-api-cfn openstack-heat-engine python-heatclient
openstack-ceilometer-api openstack-ceilometer-collector 
openstack-ceilometer-notification openstack-ceilometer-central openstack-ceilometer-alarm 
python-ceilometerclient
openstack-ceilometer-compute python-ceilometerclient python-pecan
 
"""

echo 'Clear the temporal IP and generate the remote temporal package dir'
ssh-keygen -f "~/.ssh/known_hosts" -R $IPTMP
sshpass -p $ROOT_PASSWORD ssh -o "StrictHostKeyChecking no" root@$IPTMP mkdir -p /tmp/tmp-pkg/

echo 'Adding repositories to the remote machine'
sshpass -p $ROOT_PASSWORD ssh root@$IPTMP yum -y install --downloaddir /tmp/tmp-pkg/ http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm 
sshpass -p $ROOT_PASSWORD ssh root@$IPTMP curl -o /tmp/tmp-pkg/epel-release-7-5.noarch.rpm http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
sshpass -p $ROOT_PASSWORD ssh root@$IPTMP yum -y install --downloaddir /tmp/tmp-pkg/ centos-release-openstack-liberty
#sshpass -p $ROOT_PASSWORD ssh root@$IPTMP curl -o /tmp/tmp-pkg/rdo-release-kilo.rpm  https://repos.fedorapeople.org/repos/openstack/openstack-kilo/rdo-release-kilo-1.noarch.rpm


for PKG in $OSTACK_PACKAGES
  do
   sshpass -p $ROOT_PASSWORD ssh root@$IPTMP yum -y install --downloadonly --downloaddir /tmp/tmp-pkg/ $PKG &> /dev/null
   #sshpass -p 1234 ssh root@10.0.0.45 yum -y remove $PKG
   echo "$PKG downloaded"
  done

# Download all the updates
sshpass -p $ROOT_PASSWORD ssh root@$IPTMP yum -y update --downloadonly --downloaddir /tmp/tmp-pkg/
sshpass -p $ROOT_PASSWORD ssh root@$IPTMP yum -y upgrade --downloadonly --downloaddir /tmp/tmp-pkg/
sshpass -p $ROOT_PASSWORD ssh root@$IPTMP yum -y update --downloaddir /tmp/tmp-pkg/

# Download also these convenient configuration sample files
#OTHER_PACKAGES="""
#http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img
#http://git.openstack.org/cgit/openstack/keystone/plain/httpd/keystone.py?h=stable/kilo
#https://git.openstack.org/cgit/openstack/swift/plain/etc/proxy-server.conf-sample?h=stable/kilo
#https://git.openstack.org/cgit/openstack/swift/plain/etc/account-server.conf-sample?h=stable/kilo
#https://git.openstack.org/cgit/openstack/swift/plain/etc/container-server.conf-sample?h=stable/kilo
#https://git.openstack.org/cgit/openstack/swift/plain/etc/object-server.conf-sample?h=stable/kilo
#https://git.openstack.org/cgit/openstack/swift/plain/etc/container-reconciler.conf-sample?h=stable/kilo
#https://git.openstack.org/cgit/openstack/swift/plain/etc/object-expirer.conf-sample?h=stable/kilo
#https://git.openstack.org/cgit/openstack/swift/plain/etc/swift.conf-sample?h=stable/kilo
#"""
#for PKG in $OTHER_PACKAGES;
# do
#  FILENAME=$(echo "$PKG" | awk -F? '{print $1}' | awk -F"/" '{print $NF}')
#  sshpass -p $ROOT_PASSWORD ssh root@$IPTMP curl -o /tmp/tmp-pkg/$FILENAME $PKG
# done


# Create a folder in the home directory of the local machine and download everything
mkdir -p ~/centos_packages
sshpass -p $ROOT_PASSWORD scp -r root@$IPTMP:/tmp/tmp-pkg/* ~/centos_packages/ 



