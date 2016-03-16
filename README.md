# BOMSI
Bash OpenStack Multinode Scripted Installer

BOMSI can be seen as an scripted version of the official documentation at http://docs.openstack.org.
It generates an ISO file for CentOS(7) or Ubuntu(15.10) including the installation scripts, which will execute once after first reboot.

The bomsi-iso.sh script (the one that creates the ISOs and VMs) is supposed to run under GNU/Linux and currently it is tested on Ubuntu and SUSE.

The directories are named after:
(Operative_System)-(OpenStack_Release)
Where Operative_System is the operative system for the server running OpenStack. 


