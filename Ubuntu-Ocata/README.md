
# BOMSI for Ubuntu 16.04 and OpenStack Ocata
## Short introduction
BOMSI installs OpenStack following the official install guides step by step. It generates custom ISO images containing BASH scripts for each node, which will take care of installing and setting up all the core services.

## Main updates since Mitaka
- It works properly (out of the box) with extra compute nodes (compute2, compute3)
- It has an "allinone" option to install all OpenStack components on a single machine
- Better support when running behind a http-proxy
- It should work best on Ubuntu, but now it should also work on Debian and RHEL based distros (CentOS, Fedora)

## What you need
1. For just building the ISOs you just need a basic computer running one of the supported GNU/Linux distributions.

2. For building a virtualized environment you will need a GNU/Linux computer (laptop, desktop or server) with at least some 8 GB of RAM and a CPU with at least some 4 cores. Ideally the processors should support hardware virtualization. The "allinone" option might run with even less resources, but working with slow computers is quite painful anyway, so it is up to you.

3. For installing the ISOs from point `1` on baremetal, you will need a computer at least as powerfull as the one in point `2`. For multinode, the machine used for the controller should ideally have 2 network interfaces (connected to the Management and External networks).

> Note: This installer is neither production-ready nor enterprise-grade. It is just a personal "hobby" project without any guarantee, which I write for myself. If you use it and it helps you, I'll be happy to hear something back. If it doesn't work for you, please let me know and I'll try to fix it.


Watch a short video of me talking about this release of BOMSI at the OpenStack Summit in Barcelona (26.10.2016)
[![Video about BOMSI at the Summit in Barcelona](https://i.ytimg.com/vi/NC9owNXhQO0/hqdefault.jpg?custom=true&w=196&h=110&stc=true&jpg444=true&jpgq=90&sp=68&sigh=G5R0Q2bEC_8iEejWSQtsIF9p3bc)](https://www.youtube.com/watch?v=NC9owNXhQO0)

## Install your computer manually
BOMSI checks if the local environment (your computer) is ready to build the ISO and the virtual machine(s).
The file `l_opsys` guesses the operating system and tryes to set up everything properly, but if you rather do it by hand, here are the instructions:

- You need sudo. Debian does not set it up by default. 

- Install the dependencies for building the ISO:

    curl gettext rsync fuseiso xorriso

  Installing fuseiso in Debian requires downloading the package and installing manually (check the `l_opsys` file). The package `xorriso` for CentOS is on the _rpmforge_ repository.

- Install dependencies for KVM:

    qemu-kvm libvirt-bin bridge-utils acpid virtinst qemu-system virt-manager

  To make sure you can create VMs as a user, ensure that your user has write access to `/var/lib/libvirt/images` directory (the script sets `777` permissions to make things easier).

  Make sure the user is member of the KVM groups (i.e. libvirt, kvm  and libvirt-qemu in Debian). You might need to log out and log in again (or restart) to make it work.


## How to build your OpenStack virtual environmnent:
1. Make sure you have git installed:
`sudo apt-get -y install git`

or in RHEL based distros

`sudo yum -y install git`

2. Get the code:
`git clone http://github.com/julenl/BOMSI/`

3. Move to the directory containing the script:
`cd BOMSI/Ubunbu-Ocata/`

4. Optionally you can customize the IPs and passwords
`vim lib/t_vars`

5. Run BOMSI
    1. Just generate an ISO file which you can use to install all the machines:
    `./bomsi`

    your image is now on the `$OUT_ISO_DIR` (default: /var/lib/libvirt/images) defined with the other local variables in `l_vars`.


    2. Install OpenStack:

    > Info: the first time the script is run, it will download the Ubuntu ISO into $HOME/ISOS/. Then it will as your permission to install the dependencies curl, gettext, rsync, fuseiso and xorriso. If you build a virtual environment it will also set it up or you, if it is not already, and will install (asking first for your permission) qemu-kvm libvirt bridge-utils virtinstall qemu-system and virt-manager.

    > Security info: If you are concerned about your own machine, you just need to check the files starting with *l_*, they are the ones doing stuff on the local computer. One of the few issues you might find, is that in order to be able to create VMs as a regular user it will set `777` permissions into `/var/lib/libvirt/images`. If you do not like this, check the file `l_opsys` and find a workaround that works in Ubuntu and CentOS.

    All in one server:

    `./bomsi -n=allinone`

    or in 2 separate nodes:
    `./bomsi -n=controller`
    `./bomsi -n=compute1`

    ... and, if you have a powerful computer, you can add more nodes too, if you want:
    `./bomsi -n=compute2`
    `./bomsi -n=compute3`


## Launching an instance
- From command line:
    - Source the local variables
     `. lib/t_vars`
     `. lib/l_vars`
    - connect to the controller with ssh (to use this command, make sure you have `sshpass` installed)
     `controller`

     Now you are loged into the controller machine

    - Load the bomsi variables in the controller node
     `. bomsi/lib/t_vars`
    - Load the bomsi functions
     `load_bomsi_functions`
    - Launch the instance
     `launch_instance`
      This last command will launch an instance called `bomsi-test-instance` in the provider network

- From the web browser:
    - Open a web browser (i.e. Firefox) and go to the address of the controller
      This address is by default `10.1.0.11` instead of the standard `10.0.0.11`
      to avoid conflicts with the competition installer _osbash_ from _training-labs_.
      And it can be redefined in `t_vars` in the variable `IP_controller`.

      `firefox http://10.1.0.11/horizon`

    - The login credentials are:
        - Domain: default
        - User name: admin
        - Password: Password

    - Go to **Project > Compute > Instances** and click in _Launch Intance_ on the right
        - On the Details tab, write some name in _Instance Name_, for example _test-instance_
        - On the Source tab, select _cirros_ from the _available_ section by clicking the arrow upwards
        - On the Flavor tab, select _m1.nano_ from the _available_ section by clicking on the arrow upwards
        - Click on **Launch Instance** on the lower right corner

    - You can now see your instance listed in **Project > Compute > Instances**. If you click on its name, you will get to the page with the instnce details. If you click on _Console_, you will get a VNC window where you can interact with your machine. As explained in the login prompt of that machine, you can log in with the user `cirros` and the password `cubswin:)`

