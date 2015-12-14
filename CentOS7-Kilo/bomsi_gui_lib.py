#! /usr/bin/env python

import os
from gi.repository import Gtk

def sys_info(PWD, PATH_TO_BOMSI):
    import os,platform,subprocess

    #print platform.system()
    #print platform.release()
    #print os.uname()
    OP_SYS=platform.linux_distribution()
    OP_SYS=' '.join(OP_SYS)

    def file_exists(fname):
        try:
            os.stat(fname)
            return True
        except OSError:
            return False

    
    if file_exists('/usr/bin/zypper'):
        #print "Suse based"
        PACK_CMD="zypper -y install "
    elif file_exists('/usr/bin/apt-get'):
        #print "Debian based"
        PACK_CMD="apt-get -y install "
    elif file_exists('/usr/bin/yum'):
        #print "Red Hat based"
        PACK_CMD="yum -y install "
    else:
        raise OSError, "cannot find a usable package manager"


    from psutil import virtual_memory

    mem = virtual_memory()
    TOT_MEM=mem.total/(1024 * 1024) 
    USED_MEM=mem.used/(1024 * 1024)
    FREE_MEM=mem.free/(1024 * 1024)
    PERC_MEM=(100*USED_MEM)/TOT_MEM


    #print "Guest Operative system information:"
    #print "Operative system: ", OP_SYS
    #print "Package install command: ", PACK_CMD 
    #print "Total RAM memoy: ", TOT_MEM, "MB, ", PERC_MEM, "% used"
    #print "Used RAM memoy: ", USED_MEM, "MB"
    #print "Free RAM memoy: ", FREE_MEM, "MB"


    def cmd_exists(cmd):
        return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

    def cmd_check(cmd):
        if not cmd_exists(cmd):
           OUT= "<span foreground='red'><big>" + u'\u24e7'.encode('utf-8') +"</big>   " + cmd + " </span> <b>NOT</b> installed. \n   You can install it by running:\n   <i>" +  PACK_CMD + cmd + "</i>"
        else:
           OUT= "<span foreground='green'><big>" + u'\u2713'.encode('utf8') + "</big> "+ cmd+ " installed </span>"
        return OUT

    #print "qemu exists: ", cmd_exists("virsh")
    #print "qemu check: ", cmd_check("qemu")
    #print "virsh check: ", cmd_check("virsh")


    sys_str="  <big>Localhost information:</big> \n"
    sys_str+="Operative System: \n     " + str(OP_SYS)+"\n"
    sys_str+="Package Command: \n     "+ str(PACK_CMD)+"\n"
    sys_str+="Total RAM: \n     "+ str(TOT_MEM)+"MB"+"\n"
    sys_str+="Used RAM: \n     "+ str(USED_MEM) +"  ("+ str(PERC_MEM) +"% used)"+"\n"
    sys_str+="\nCurrent working directory: \n     "+ str(PWD)+" "+"\n"
    sys_str+="Path to BOMSI files: \n     "+ str(PATH_TO_BOMSI)+" "+"\n"

    soft_str="  <big>Installed Packages:</big> \n"
    soft_str+=cmd_check("curl")+"\n"
    soft_str+=cmd_check("virsh")+"\n"
    soft_str+=cmd_check("virtualbox")+"\n"
    soft_str+=cmd_check("createrepo")+"\n"
    soft_str+=cmd_check("genisoimage")+"\n"
    soft_str+=cmd_check("syslinux")+"\n"
    soft_str+=cmd_check("syslinux-utils")+"\n"
    

    sys_dict = { "SYS_STR": sys_str, "SOFT_STR": soft_str, "OP_SYS":OP_SYS, "PACK_CMD":PACK_CMD, "TOT_MEM":TOT_MEM, "PERC_MEM":PERC_MEM }


    return sys_dict







def read_bomsi_vars(PATH_TO_BOMSI):
   BOMSI_VARS={}
   #Read the bomsi_vars file line by line and parse the variables
   for var in open(PATH_TO_BOMSI+"/bomsi_vars","r"):
       li=var.strip()
       if not li.startswith("#") and "=" in li and "$PATH" not in li and "awk " not in li and "sed " not in li:
           #Remove comments in line
           if '#' in var:
             var=var.split('#')[0]
           var=var.rstrip().split()[1]
           var_val_tmp=""
           var_var=var.split("=")[0] #variable
           var_val_bulk=var.split("=")[1] #value
           if "'" in var_val_bulk or '"' in var_val_bulk:
             var_val_bulk="=".join(var.split("=")[1:])
           else: 
             var_val_bulk=var.split("=")[1] 

           #If the BASH variable is defined using (an)other variable(s)
           if '$' in var_val_bulk:
             var_val_bulk = var_val_bulk.replace('{','').replace('}','').strip()
             for N in range(var_val_bulk.count('$')):
               var_val_tmp_i=var_val_bulk.split("$")[N+1]
               #If the variable contains a string IPPR_T"1"
               if '"' in var_val_tmp_i:
                 var_val_tmp0=var_val_tmp_i.split('"')[0]
                 var_val_tmp1=var_val_tmp_i.split('"')[1]
                 var_val_tmp += BOMSI_VARS[var_val_tmp0]+var_val_tmp1
               else:
                 #Using a try, in case variables were not properly defined
                 try:
                   BOMSI_VARS[var_val_tmp_i]
                   var_val_tmp += BOMSI_VARS[var_val_tmp_i]  
                 except:
                   print var_var, var_val_tmp_i,"variable not defined"
                   var_val_tmp
           else:
             var_val_bulk = var_val_bulk.replace('"','')
             var_val_tmp = var_val_bulk      
       
           var_val = var_val_tmp 
           BOMSI_VARS.update({ var_var : var_val })

   return BOMSI_VARS




def edit_bomsi_var(button, PATH_TO_BOMSI, VARIABLE, VALUE):
    #print VALUE.get_text()
    try:
      VALUE = VALUE.get_text()
    except:
      VALUE = VALUE.get_active_text()

    VARS_FILE=PATH_TO_BOMSI+"/bomsi_vars"
    BULK=[]
    VAR_CHANGED = False
    for line in open(VARS_FILE, "r"):
      if line.strip() != '':
        line=line.strip()
        if " "+VARIABLE+"=" in line:
          line="export " + VARIABLE + "=" + VALUE
          BULK.append(line)
          VAR_CHANGED = True
        else:
          BULK.append(line)

    if not VAR_CHANGED :
      line="export " + VARIABLE + "=" + VALUE
      BULK.append(line)
       
    out=open(PATH_TO_BOMSI+"/bomsi_vars","w")
    for line in BULK:
      print>>out, line
    out.close()
    print VARIABLE + " saved as " + VALUE + " in bomsi_vars file"
    


def get_pendrives():
     BULK=os.popen("ls -l /dev/disk/by-id/usb* |awk -F/ '{print $NF}'")
     DISKS=[]
     for line in BULK.readlines():
         DISKS.append(line.strip().rstrip('1234567890'))

     DISKS=list(set(DISKS))
     LABEL_STR=""
     for DISK in DISKS:
       LABEL_STR += "<b>"+DISK+ ":</b>  \n"

     return DISKS
        

def set_selected_disk(nothing,combo,PATH_TO_BOMSI):
    #disk = combo.get_active_text()
    if combo.get_active_text() != None:
      edit_bomsi_var("nothing",PATH_TO_BOMSI,'USB_DISK_DEV',combo)
      print "USB_DISK was set to:",combo.get_active_text()




def opt_only_iso(widget,PATH_TO_BOMSI,ISO_LABEL):
    #name=entry.get_text()
    print 'Creating iso file: ~/'+ISO_LABEL+''
    #os.system('sudo PYTHONPATH=$PYTHONPATH:'+PATH_TO_BOMSI+' '+PATH_TO_BOMSI+'/bomsi-iso.sh ')
    os.system('sudo '+PATH_TO_BOMSI+'/bomsi-iso.sh ')
    import getpass
    if name != 'BOMSI-multiboot.iso':
      os.system('sudo mv ~/BOMSI-multiboot.iso ~/'+name+'')
    os.system('sudo chown '+getpass.getuser()+' ~/'+name+'')



def create_pendrive(widget, PATH_TO_BOMSI):
   try:
     read_bomsi_vars(PATH_TO_BOMSI)
     BOMSI_VARS = read_bomsi_vars(PATH_TO_BOMSI)
     USB_DISK_DEV=BOMSI_VARS['USB_DISK_DEV']
     print 'Generating a BOMSI ISO file at: ~/'
     print 'Installing ISO on device /dev/'+USB_DISK_DEV
     #This just executes bomsi-iso.sh -n=controller -u=/dev/sdb
     os.system('sudo '+PATH_TO_BOMSI+'/bomsi-iso.sh -n=controller -u=/dev/'+USB_DISK_DEV + ' |tee /tmp/bomsi.log')
   except:
     print "ERROR: no pendrive detected"
   


def create_local_virt_env(widget, PATH_TO_BOMSI, entry):
   read_bomsi_vars(PATH_TO_BOMSI)
   machine=entry.get_active_text()
   BOMSI_VARS = read_bomsi_vars(PATH_TO_BOMSI)
   try:
     INSTALL_TYPE = BOMSI_VARS['INSTALL_TYPE']
   except:
     INSTALL_TYPE = '3_nodes'   

   try:
    OUT_ISO_NAME=BOMSI_VARS['OUT_ISO_NAME'].split('.iso')[0]
   except:
    OUT_ISO_NAME='BOMSI-multiboot'

   print INSTALL_TYPE,machine, OUT_ISO_NAME

   if INSTALL_TYPE == '3_nodes':
      print '##### Generating and installing the controller node ####'
      os.system('sudo ./bomsi-iso.sh -n=1.controller')
      print '##### Generating and installing the first compute node ####'
      os.system('sudo ./bomsi-iso.sh -n=1.compute1')
      print '##### Generating and installing the network node ####'
      os.system('sudo ./bomsi-iso.sh -n=1.network')
     
   elif INSTALL_TYPE == 'controller':
      print '##### Generating and installing the controller node ####'
      os.system('sudo ./bomsi-iso.sh -n=1.controller')
   elif INSTALL_TYPE == 'compute1':
      print '##### Generating and installing only the first compute node ####'
      os.system('sudo ./bomsi-iso.sh -n=1.compute1')
   elif INSTALL_TYPE == 'compute2':
      print '##### Generating and installing only the second compute node ####'
      os.system('sudo ./bomsi-iso.sh -n=1.compute2')
   elif INSTALL_TYPE == 'compute3':
      print '##### Generating and installing only the third compute node ####'
      os.system('sudo ./bomsi-iso.sh -n=1.compute3')
   elif INSTALL_TYPE == 'network':
      print '##### Generating and installing only the network node ####'
      os.system('sudo ./bomsi-iso.sh -n=1.network')









def diag_no_usb_selected(self, widget):
    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, "This is an INFO MessageDialog")
    dialog.format_secondary_text(
        "And this is the secondary text that explains things.")
    dialog.run()
    print("INFO dialog closed")










