# BOMSI _lib/_ folder

This is the "lib" folder inside the bomsi root dir.
It contains all the functions and scripts used by BOMSI.

The files have different prefixes, indicating the target machine for their execution.

- The files starting with `l_` are supposed to be executed in the local machine,
while building the ISO images or virtual environment.

- The files starting with `t_` are meant to be executed on the target machines,
or the ones that are going to be running the actual OpenStack installation.

- `ks_template` is a kickstart/preseed file template for installing the operative system
  of the OpenStack servers. Carefull! It is not meant to be used as it is. It is a template
  and contains variables which are parsed by `l_gen_iso` to generate the real files.

- `ini_comparer.py` is a usefull script to compare two local or remote .ini configuration
  files

- susti is a python script for editing .ini config files.
  Usage: `susti CONFIG_FILE SECTION "KEYWORD = VALUE"`

- `os_test_ubuntu` is a library of functions to check if everything is working properly
  without having to type in all the "`service XXX status`" and "`openstack XXX list`"
  commands.

- The `modified_files` script retriebes all the configuration files modified by the installation. This is useful to run on a brocken system and on a working one, and then compare the configuration files with `ini_comparer.py`. 

