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




## READ t_vars and l_vars line by line, parse variables and add them to BOMSI_VARS

def read_bomsi_vars(FILE,OUTPUT_FORMAT,PATH_TO_BOMSI):
   # FILE can be lib/t_vars or lib/l_vars
   # OUTPUT_FORMAT can be STRING, RAW or LINE (returns full line in file)
   # Returns a dictionary with key:value for all l_/t_vars variables
   BOMSI_VARS={}
   PARSE = False

   for line in open(PATH_TO_BOMSI+'/lib/'+FILE,"r"):
       #if FILE == "l_vars":
       #   print line
       li=line.strip()
       var,val='',''
       #Parse normal variables (line starts with "export")
       if li.startswith("export ") and "=" in li:
           var_val=li.split()[1]
           var=var_val.split("=")[0]
           val=var_val.split("=")[1]
       elif li.startswith("set_if_unset ") and len(li.split()) > 2:
           var=li.split()[1]
           val=li.split()[2]

       if val:
           if OUTPUT_FORMAT == "LINE":
               val=li.rstrip()

           # Trim first and last " quote marks from value
           if val.startswith('"') and val.endswith('"'):
               val = val[1:-1]

           if OUTPUT_FORMAT == "RAW":
               val = val
           if OUTPUT_FORMAT == "STRING":
               # If variables contain variables, expand them
               if len(val)>0 and "$" in val:
                   val=os.popen('. '+PATH_TO_BOMSI+'/lib/'+FILE+' && echo '+val+'""')
                   val=val.readlines()[0].strip()

           BOMSI_VARS.update({ var : val })
   return BOMSI_VARS





# EDIT variables as and were they were originally defined

def edit_bomsi_var(button, FILE, PATH_TO_BOMSI, VARIABLE, VALUE):
    #print VALUE.get_text()
    try:
      VALUE = VALUE.get_text()
    except:
      VALUE = VALUE.get_active_text()

    VARS_FILE=PATH_TO_BOMSI+"/lib/"+FILE
    BULK=[]

    #Did the variable change?
    #Compare new variable with the one defined on the l_/t_vars
    #Is the variable alredy in the file
    try:
        raw_line=read_bomsi_vars(FILE,'LINE',PATH_TO_BOMSI)[VARIABLE]
        new_var=False
    except:  
        new_var=True

    if not new_var:
        if raw_line.startswith("set_if_unset") and len(raw_line.split()) > 2:
           var=raw_line.split()[1]
           val=raw_line.split()[2]
        elif raw_line.startswith("export") and "=" in raw_line:
           var_val=raw_line.split()[1]
           var=var_val.split("=")[0]
           val=var_val.split("=")[1]

        if val == VALUE or val == '"'+VALUE+'"' or val == "'"+VALUE+"'":
            # Variables didn't change (maybe qoutes, but it's the same). Do nothing
            pass
        else:
            # Try expanding the variables
            expval=os.popen('. '+PATH_TO_BOMSI+'/lib/'+FILE+' && echo $'+var+'""')
            expval=expval.readlines()[0].strip()
            if expval == VALUE or expval == '"'+VALUE+'"' or expval == "'"+VALUE+"'":
                # Expanding the old value as variable returns the same as the new value
                print "Values are the same"
                pass
            else:
                # Here is where we SUBSTITUTE the value
                for line in open(VARS_FILE, "r"):
                    if len(line.split()) > 1:
                      if line.split()[1].startswith(var):
                          #first_arg is export OR set_if_unset
                          sep,firstarg=" ",""
                          first_arg=raw_line.split()[0]
                          if "export" in raw_line:
                              sep="="
                          BULK.append(first_arg + " " + var + sep + VALUE)
                          var_found=True
                      else:
                          BULK.append(line.rstrip())
                    else:
                      BULK.append(line.rstrip())

    else:
        # If variable not defined in file
        print "Appending 'export "+VARIABLE+" "+VALUE+"' to "+ VARS_FILE
        for line in open(VARS_FILE, "r"):
            BULK.append(line.rstrip())
        BULK.append("export " + VARIABLE + "=" + VALUE)

    if len(BULK) > 10:
      output=open(PATH_TO_BOMSI+'/lib/'+FILE,"w")
      #print len(BULK)
      for line in BULK:
         output.write("%s\n" % (line))

      output.close()
      print VARIABLE + ' saved as ' + VALUE + ' in lib/' + FILE +' file'
       

    


def get_pendrives():
     BULK=os.popen("ls -l /dev/disk/by-id/usb* 2> /dev/null |awk -F/ '{print $NF}'")
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
      edit_bomsi_var("nothing","l_vars",PATH_TO_BOMSI,'USB_DISK_DEV',combo)
      print "USB_DISK was set to:",combo.get_active_text()


def opt_packages(widget,PATH_TO_BOMSI):
  import os,subprocess
  os.system(''+PATH_TO_BOMSI+'/bomsi-iso.sh -n=Packages')    
  import time
  IPTMP="10.0.0.254"
  os.system('ssh-keygen -f "$HOME/.ssh/known_hosts" -R '+IPTMP)
  CMD='sshpass -p '+ROOT_PASSWORD+' ssh -o "StrictHostKeyChecking no" root@'+IPTMP+' hostname'
  PKGS_UP=False
  while not PKGS_UP:
    print "####"
    RESPO=subprocess.Popen(CMD,shell=True, stdout=subprocess.PIPE)
    try:
      RESPOSTR=list(RESPO.stdout)[0]
      PKGS_UP=True
    except:
      time.sleep(5)
      print "waiting 5 more seconds for the packages VM"

  print "Packages server is up, downloading..."
  print "... this might take quite long..."
  os.system(PATH_TO_BOMSI+'/gather_packages_os.sh ')
  print "DONE!"
  print "Packages stored in ~/Packages directory"  
  



def opt_only_iso(widget,PATH_TO_BOMSI,ISO_LABEL):
    #name=entry.get_text()
    print 'Creating iso file: ~/'+ISO_LABEL+''
    #os.system('sudo PYTHONPATH=$PYTHONPATH:'+PATH_TO_BOMSI+' '+PATH_TO_BOMSI+'/bomsi-iso.sh ')
    os.system(''+PATH_TO_BOMSI+'/bomsi ')
    import getpass
    if name != 'BOMSI-multiboot.iso':
      os.system('sudo mv ~/BOMSI-multiboot.iso ~/'+name+'')
    os.system('sudo chown '+getpass.getuser()+' ~/'+name+'')



def create_pendrive(widget, PATH_TO_BOMSI):
   try:
     read_bomsi_vars('l_vars','STRING',PATH_TO_BOMSI)
     BOMSI_VARS = read_bomsi_vars('l_vars','STRING',PATH_TO_BOMSI)
     USB_DISK_DEV=BOMSI_VARS['USB_DISK_DEV']
     print 'Generating a BOMSI ISO file at: ~/'
     print 'Installing ISO on device /dev/'+USB_DISK_DEV
     #This just executes bomsi-iso.sh -n=controller -u=/dev/sdb
     os.system('sudo '+PATH_TO_BOMSI+'/bomsi-iso.sh -n=controller -u=/dev/'+USB_DISK_DEV + ' |tee /tmp/bomsi.log')
   except:
     print "ERROR: no pendrive detected"
   


def create_local_virt_env(widget, PATH_TO_BOMSI, entry):
   read_bomsi_vars('l_vars','STRING',PATH_TO_BOMSI)
   machine=entry.get_active_text()
   BOMSI_VARS = read_bomsi_vars('l_vars','STRING',PATH_TO_BOMSI)
   try:
     INSTALL_TYPE = read_bomsi_vars('l_vars','STRING',PATH_TO_BOMSI)['INSTALL_TYPE']
     #BOMSI_VARS['INSTALL_TYPE']
   except:
     INSTALL_TYPE = '2_nodes'   

   try:
    OUT_ISO_NAME=BOMSI_VARS['OUT_ISO_NAME'].split('.iso')[0]
   except:
    OUT_ISO_NAME='BOMSI-multiboot'


   if INSTALL_TYPE == '2_nodes':
      print '##### Generating and installing the controller node ####'
      #os.system('./bomsi -n=1.controller')
      print '##### Generating and installing the first compute node ####'
      #os.system('./bomsi -n=1.compute1')
     
   elif INSTALL_TYPE == 'controller':
      print '##### Generating and installing the controller node ####'
      os.system('./bomsi -n=1.controller')
   elif INSTALL_TYPE == 'compute1':
      print '##### Generating and installing only the first compute node ####'
      os.system('./bomsi -n=1.compute1')
   elif INSTALL_TYPE == 'compute2':
      print '##### Generating and installing only the second compute node ####'
      os.system('./bomsi -n=1.compute2')
   elif INSTALL_TYPE == 'compute3':
      print '##### Generating and installing only the third compute node ####'
      os.system('./bomsi -n=1.compute3')
   elif INSTALL_TYPE == 'clean':
      print '##### Generating and installing a clean machine ####'
      os.system('./bomsi -n=1.clean')
   elif INSTALL_TYPE == 'packages':
      print '##### Generating and installing only a machine to download packages ####'
      os.system('./bomsi -n=1.packages')
   #elif INSTALL_TYPE == 'network':
   #   print '##### Generating and installing only the network node ####'
   #   os.system('sudo ./bomsi-iso.sh -n=1.network')









def diag_no_usb_selected(self, widget):
    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, "This is an INFO MessageDialog")
    dialog.format_secondary_text(
        "And this is the secondary text that explains things.")
    dialog.run()
    print("INFO dialog closed")










