#! /bin/bash

# This script lists and retrieves all the files modified during the
# OpenStack installation following the install-guides.

controller_ip="10.0.0.11"
compute1_ip="10.0.0.31"

list_files_controller="
/etc/chrony/chrony.conf
/etc/mysql/mariadb.conf.d/99-mysqld_openstack.cnf
/etc/memcached.conf
/etc/apache2/apache2.conf
/etc/keystone/keystone.conf
/etc/glance/glance-api.conf
/etc/glance/glance-registry.conf
/etc/nova/nova.conf
/etc/neutron/neutron.conf
/etc/neutron/plugins/ml2/ml2_conf.ini
/etc/neutron/plugins/ml2/linuxbridge_agent.ini
/etc/neutron/l3_agent.ini
/etc/neutron/dhcp_agent.ini
/etc/neutron/dnsmasq-neutron.conf
/etc/neutron/metadata_agent.ini
/etc/openstack-dashboard/local_settings.py
"


list_files_compute="
/etc/nova/nova.conf
/etc/nova/nova-compute.conf
/etc/neutron/neutron.conf
/etc/neutron/plugins/ml2/linuxbridge_agent.ini
/etc/neutron/plugins/ml2/linuxbridge_agent.ini

"

mkdir -p bomsi_sample_conf/{controller,compute1}

for conf in `echo "$list_files_controller"`;
  do
    echo $conf
    rsync -av root@${controller_ip}:${conf} bomsi_sample_conf/controller
  done

for conf in `echo "$list_files_compute"`;
  do
    echo $conf
    rsync -av root@${compute1_ip}:${conf} bomsi_sample_conf/compute1
  done

tar cvjf bomsi_sample_conf.bz2 bomsi_sample_conf

