
# BOMSI for Ubuntu 16.04 and OpenStack Newton


## How to use it:
1. Make sure you have git installed:
`sudo apt-get -y install git`

2. Get the code:
`git clone http://github.com/julenl/BOMSI/`

3. Move to the directory containing the script:
`cd BOMSI/Ubunbu-Newton/`

4. Optionally you can pre-install the dependencies to avoid problems
``` bash
sudo apt-get -y install qemu-kvm dumpet libvirt-bin acpid virtinst \
                           qemu-system fuseiso virt-manager
```
5. Optionally you can customize the IPs and passwords
`vim lib/t_vars`

6. Install the controller
`./bomsi -n=controller`

7. Install the first compute node
`./bomsi -n=compute1`




