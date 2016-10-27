
# BOMSI for Ubuntu 16.04 and OpenStack Newton
## Short introduction
BOMSI installs OpenStack following the official install guides step by step. It generates custom ISO images containing BASH scripts for each node, which will take care of installing and setting up all the core services.

> Note: This installer is neither production-ready nor enterprise-grade. It is just a personal "hobby" project without any guarantee, which I write for myself. If you use it and it helps you, I'll be happy to hear something back. If it doesn't work for you, please let me know and I'll try to fix it.


Watch a short video of me talking about this release of BOMSI at the OpenStack Summit in Barcelona (26.10.2016)
[![Video about BOMSI at the Summit in Barcelona](https://i.ytimg.com/vi/NC9owNXhQO0/hqdefault.jpg?custom=true&w=196&h=110&stc=true&jpg444=true&jpgq=90&sp=68&sigh=G5R0Q2bEC_8iEejWSQtsIF9p3bc)](https://www.youtube.com/watch?v=NC9owNXhQO0)

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




