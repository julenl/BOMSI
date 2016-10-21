#!/usr/bin/python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os
import sys

#sys.path.append("./lib")
import l_bomsi_gui_lib #library for functions on this GUI

global PWD
global PATH_TO_ISO
PWD=os.getcwd()
PATH_TO_BOMSI=PWD

#print PWD, PATH_TO_BOMSI

BOMSI_GUI_OPSYS="Ubuntu"
BOMSI_GUI_RELEASE="Newton"
BOMSI_GUI_VERSION="0.2"

# Modal window showing local system information
class LocalSysInfoModal(Gtk.Dialog):
    def __init__(self, parent, PWD, PATH_TO_BOMSI):
        Gtk.Dialog.__init__(self, "Local system information", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(400, 300)

        #Labels containing system information (operative system/software)
        row_sysinfo = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        label_sysinfo_syst = Gtk.Label()
        label_sysinfo_syst.set_markup(l_bomsi_gui_lib.sys_info(PWD, PATH_TO_BOMSI)['SYS_STR'])
        label_sysinfo_soft = Gtk.Label()
        label_sysinfo_soft.set_markup(l_bomsi_gui_lib.sys_info(PWD, PATH_TO_BOMSI)['SOFT_STR'])
        row_sysinfo.pack_start(label_sysinfo_syst, False, True, 0)
        row_sysinfo.pack_start(label_sysinfo_soft, False, True, 0)

        label_sysinfo_version = Gtk.Label('BOMSI GUI for '+BOMSI_GUI_RELEASE+' version: '+BOMSI_GUI_VERSION + ' on ' + BOMSI_GUI_OPSYS)

        box = self.get_content_area()
        box.add(row_sysinfo)
        box.add(label_sysinfo_version)
        self.show_all()








class Main(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title='BOMSI GUI ('+BOMSI_GUI_OPSYS+'/'+BOMSI_GUI_RELEASE+')')
        self.set_border_width(10)

      #This is the vertical container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30,halign=Gtk.Align.START, valign=Gtk.Align.START)
        self.add(vbox)




      #First row with logo, system info and basic checks
        topbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        logo_img = Gtk.Image.new_from_file(PWD+'/lib/gui_img/BOMSI_logo_gui.png')
        topbox.pack_start(logo_img, False, False, 0) #(child,expand=True,fill=True,padding=0) 



        #Box with two rows: sysinfo button/files check and hide/show vars editor
        vbox_top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        #Little box for the sysinfo button and the files checker
        hbox_sys_files = Gtk.Box()

        button_showinfo = Gtk.Button(label="System Info",halign=Gtk.Align.END)
        button_showinfo.connect("clicked",self.on_button_clicked_info)
        hbox_sys_files.pack_start(button_showinfo, False, False, 0) 


        #Check if all the needed BOMSI files are in the PATH_TO_BOMSI directory
        BOMSI_FILES=['lib/l_iso2vm','lib/l_vars','lib/t_vars','bomsi']

        for bfile in BOMSI_FILES:
          if not os.path.isfile(PATH_TO_BOMSI+'/'+bfile):
             text_label_conffile = "<span foreground='red'><big>" + u'\u24e7'.encode('utf8') + "</big> "+ bfile +" file not found at:</span> \n    "+PATH_TO_BOMSI
             
        try:
             not text_label_conffile
        except:
             text_label_conffile = "<span foreground='green'><big>" + u'\u2713'.encode('utf8') + "</big> all BOMSI files detected</span>"
             BFILES_EXIST=" "
               
        label_checkconff = Gtk.Label(halign=Gtk.Align.END)
        label_checkconff.set_markup(text_label_conffile)
        
        hbox_sys_files.pack_start(label_checkconff, False, True, 0 )
        vbox_top.pack_start(hbox_sys_files, False, True, 0 )


   

      #Notebook with the install variables
        notebook_vars = Gtk.Notebook()

        switch_box = Gtk.Box()
        switch_label = Gtk.Label('Hide BOMSI variables editor:  ',halign=Gtk.Align.END)
        switch_box.pack_start(switch_label, False, False, 0)
        switch_sysinfo = Gtk.Switch()
        switch_sysinfo.connect("notify::active", self.notebook_vars_show, notebook_vars)
        switch_sysinfo.props.valign = Gtk.Align.END
        switch_box.pack_start(switch_sysinfo, False, False, 0)

        ## These three lines come from the previus section
        vbox_top.pack_start(switch_box, True, True, 0 )
        topbox.pack_start(vbox_top, True, True, 0)
        vbox.pack_start(topbox, True, True, 0)





 

        #Function for creating elements on the variables dialog 
        def vars_entry_unit(LABEL,FILE,VARIABLE,TTTEXT):
          # Display label, file containing the variable (t/l_vars), variable name and tootip text
          grid_li = Gtk.Grid(valign=Gtk.Align.START)
                   
 
          vars_li = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, valign=Gtk.Align.START)
          vars_li.set_tooltip_text(TTTEXT)
          label = Gtk.Label(LABEL,halign=Gtk.Align.START)
          label.set_width_chars(14)
          label.set_line_wrap(True)
          vars_li.pack_start(label, False, False, 0)

          vars_entry = Gtk.Entry()
          vars_entry.set_width_chars(14)

          try:
             VALUE=l_bomsi_gui_lib.read_bomsi_vars(FILE,'STRING',PATH_TO_BOMSI)[VARIABLE]
          except:
             VALUE='' # If variable not defined in l/t_vars


          vars_entry.set_text(VALUE)
          vars_entry.set_halign(Gtk.Align.END)
          vars_li.pack_start(vars_entry, False, False, 0)

          button_save = Gtk.Button(label="<Save",halign=Gtk.Align.END)
          button_save.connect("clicked",l_bomsi_gui_lib.edit_bomsi_var,FILE,PATH_TO_BOMSI,VARIABLE,vars_entry)
          vars_li.pack_start(button_save, False, False, 0)

          #grid_li.attach(label,0,2,0,1) 
          #grid_li.attach(vars_entry,2,4,0,1 )
          #grid_li.attach(button_save,4,5,0,1)

          return vars_li
       



        ### HERE GOES THE CONTENT OF THE TABS AND VARIABLES ###

        # Main variables

        table_mainvars = Gtk.Table(5, 2, True, valign=Gtk.Align.START) #(rows,columns,homogenous, ...)
        table_mainvars.set_row_spacings(10)
        table_mainvars.set_col_spacings(10)

        tooltip='Name of the ISO file which will be created\n(in the home directory)\ni.e.:controller.iso'
        item=vars_entry_unit('ISO name', 'l_vars','OUT_ISO_NAME', tooltip)
        table_mainvars.attach(item,0,2,0,1)

        tooltip='Disk device in which \nUbuntu is going to\nget installed.\n i.e.: sda (for physical HDs)\nor vda (for virtual HDs'
        item=vars_entry_unit('Disk name', 'l_vars', 'HD', tooltip)
        table_mainvars.attach(item,0,2,1,2)

        tooltip='Number of Virtual CPUs\n(for virtual environments).\n i.e.: 2'
        item=vars_entry_unit('# of VCPUs', 'l_vars', 'VCPUS', tooltip)
        table_mainvars.attach(item,0,2,2,3)

        tooltip='Amount of RAM memory (in Mb)\n(for virtual environments).\n i.e.: 4092'
        item=vars_entry_unit('Virt. RAM', 'l_vars', 'VRAM', tooltip)
        table_mainvars.attach(item,0,2,3,4)

        tooltip='The name of the management\nnetwork (or bridge) for VMs\n (i.e. "network=management" or "bridge=br0")'
        item=vars_entry_unit('Virt mgm net', 'l_vars', 'VIRT_NIC_MAN', tooltip)
        table_mainvars.attach(item,0,2,4,5)


        tooltip='Network interface associated to the admin network.\ni.e.: eth0'
        item=vars_entry_unit('iface admin',  't_vars','IFACE0',tooltip)
        table_mainvars.attach(item,2,4,0,1)

        #tooltip='Network interface associated to the tunnel network\ni.e.:eth1 or eth0.1'
        #item=vars_entry_unit('iface tunnel', 'IFACE1',tooltip)
        #table_mainvars.attach(item,2,4,1,2)

        #tooltip='Network interface associated to the storage network\ni.e.:eth2 or eth0.2'
        #item=vars_entry_unit('iface storage', 'IFACE2',tooltip)
        #table_mainvars.attach(item,2,4,2,3)

        tooltip='Network interface associated to the external network'
        item=vars_entry_unit('iface extern',  't_vars','IFACE_EXT',tooltip)
        table_mainvars.attach(item,2,4,3,5)

#       tooltip=
#       item=
#       table_mainvars.attach(item,0,2,1,2)




        item=vars_entry_unit('ISO name',  'l_vars','OUT_ISO_NAME', 'Name of the ISO file which will be created\n(in the home directory)\ni.e.:controller.iso')


        vars_main_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        #First column of main variables tab
        vars_main_hbox_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,valign=Gtk.Align.START)
        vars_main_hbox_vbox.pack_start(vars_entry_unit('ISO name','l_vars', 'OUT_ISO_NAME', 'Name of the ISO file which will be created\n(in the home directory)\ni.e.:controller.iso'), True, False, 0)
        vars_main_hbox_vbox.pack_start(vars_entry_unit('Disk name','l_vars','HD', 'Disk device in which \nUbuntu is going to\nget installed.\n i.e.: sda'), True, False, 0)
        vars_main_hbox_vbox.pack_start(vars_entry_unit('# of VCPUs','l_vars','VCPUS', 'Number of Virtual CPUs\n(for virtual environments).\n i.e.: 2'), False, False, 0)
        vars_main_hbox_vbox.pack_start(vars_entry_unit('RAM','l_vars','VRAM', 'Amount of RAM memory (in Mb)\n(for virtual environments).\n i.e.: 4092'), False, False, 0)
        vars_main_hbox_vbox.pack_start(vars_entry_unit('Virt mgm net','l_vars', 'VIRT_NIC_MAN', 'The name of the management\nnetwork (or bridge) for VMs\n (i.e. "management" or "br0")'), False, False, 0)
        #vars_main_hbox_vbox.pack_start(vars_entry_unit('', '', ''), True, True, 0)

        vars_main_hbox.pack_start(vars_main_hbox_vbox, False, False, 0)

        #Second column of passwords variables tab
        vars_main_hbox_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,valign=Gtk.Align.START)
        #vars_main_hbox_vbox.pack_start(vars_entry_unit('Glance', 'GLANCE_PASSWORD','Password for Glance'), True, True, 0)
        vars_main_hbox.pack_start(vars_main_hbox_vbox, False, False, 0)

        notebook_vars_main = Gtk.Label(label="Main variables")



 
        # Main Passwords
        vars_pwt_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        #First column of password variables tab
        vars_pwt_hbox_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,valign=Gtk.Align.START)
        vars_pwt_hbox_vbox.pack_start(vars_entry_unit('Ubuntu root','t_vars','ROOT_PASSWORD', 'Root password for login to the machine'), True, True, 0)
        vars_pwt_hbox_vbox.pack_start(vars_entry_unit('MariaDB admin','t_vars','MYSQL_ROOT','Root password for the MySQL/Mariadb database'), True, True, 0)
        vars_pwt_hbox_vbox.pack_start(vars_entry_unit('Rabbit admin','t_vars','RABBIT_PASS','RabbitMQ admin password'), True, True, 0)
        vars_pwt_hbox_vbox.pack_start(vars_entry_unit('admin user','t_vars','ADMIN_PASS','"OpenStack admin user'), True, True, 0)
        vars_pwt_hbox_vbox.pack_start(vars_entry_unit('demo user','t_vars','DEMO_PASS','"OpenStack demo user'), True, True, 0)
        vars_pwt_hbox.pack_start(vars_pwt_hbox_vbox, True, True, 0)

        #Second column of passwords variables tab
        vars_pwt_hbox_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,valign=Gtk.Align.START)
        vars_pwt_hbox_vbox.pack_start(vars_entry_unit('Glance','t_vars','GLANCE_PASSWORD','Password for Glance'), True, True, 0)
        vars_pwt_hbox_vbox.pack_start(vars_entry_unit('Nova','t_vars','NOVA_PASSWORD','Password for Neutron'), True, True, 0)
        vars_pwt_hbox_vbox.pack_start(vars_entry_unit('Neutron','t_vars','NEUTRON_PASSWORD','Password for Nova'), True, True, 0)
        vars_pwt_hbox.pack_start(vars_pwt_hbox_vbox, True, True, 0)

        notebook_vars_pwl = Gtk.Label(label="Passwords")



        vars_ips_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        #First column of the Server IPs tab
        vars_ips_hbox_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,valign=Gtk.Align.START)
        #vars_ips_hbox_vbox.pack_start(vars_entry_unit('iface admin', 'IFACE0','Network interface associated to the admin network'), True, True, 0)
        #vars_ips_hbox_vbox.pack_start(vars_entry_unit('iface tunnel', 'IFACE1','Network interface associated to the tunnel network'), True, True, 0)
        #vars_ips_hbox_vbox.pack_start(vars_entry_unit('iface storage', 'IFACE2','Network interface associated to the storage network'), True, True, 0)
        #vars_ips_hbox_vbox.pack_start(vars_entry_unit('iface external', 'IFACE_EXT','Network interface associated to the external network'), True, True, 0)
        vars_ips_hbox_vbox.pack_start(vars_entry_unit('Controller','t_vars','IP_controller','IP of the controller server'), True, True, 0)
        #vars_ips_hbox_vbox.pack_start(vars_entry_unit('Network', 'NEUTRON_NODE_IP','IP of the network node'), True, True, 0)
        vars_ips_hbox_vbox.pack_start(vars_entry_unit('Compute1','t_vars','IP_compute1','IP of the compute node (1st one)'), True, True, 0)
        vars_ips_hbox.pack_start(vars_ips_hbox_vbox, True, True, 0)
 

        #Second column of the Server IPs tab
        vars_ips_hbox_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,valign=Gtk.Align.START)
        vars_ips_hbox_vbox.pack_start(vars_entry_unit('Pref. admin net','t_vars','IPPR_A','Admin network without the last number'), True, True, 0)
        vars_ips_hbox_vbox.pack_start(vars_entry_unit('Pref. ext. net','t_vars','IPPR_EXT','External network without last number'), True, True, 0)
        #vars_ips_hbox_vbox.pack_start(vars_entry_unit('Prefix stor. net','IPPR_S','Storage network without the last number'), True, True, 0)
        vars_ips_hbox_vbox.pack_start(vars_entry_unit('Gateway','t_vars','GATEWAY','Default gateway for the management network'), True, True, 0)
        vars_ips_hbox_vbox.pack_start(vars_entry_unit('DNS server','t_vars','NAMESERVER','IP of the DNS server'), True, True, 0)
        vars_ips_hbox.pack_start(vars_ips_hbox_vbox, True, True, 0)

        notebook_vars_ipl = Gtk.Label(label="Server IPs")


        #Pack both tabs in the variables notebook
        notebook_vars.append_page(table_mainvars, notebook_vars_main)
        #notebook_vars.append_page(vars_main_hbox, notebook_vars_main)
        notebook_vars.append_page(vars_pwt_hbox, notebook_vars_pwl)
        notebook_vars.append_page(vars_ips_hbox, notebook_vars_ipl)

        #Show the variables notebook in main window
        vbox.pack_start(notebook_vars, False, True, 0)








      #Box containing possible options

        #Download packages
        vbox_packages = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        label_packages = Gtk.Label()
        label_packages.set_markup("Download OS files\n <small>using a VM</small>")
        logo_packages = Gtk.Image.new_from_file(PWD+'/lib/gui_img/download_packages.png')
        button_packages = Gtk.Button()
        button_packages.set_image(logo_packages)
        button_packages.connect("clicked", l_bomsi_gui_lib.opt_packages,PATH_TO_BOMSI)
        vbox_packages.pack_start(label_packages, False, True, 0)
        vbox_packages.pack_start(button_packages, False, True, 0)




        #Just create the ISO
        vbox_iso = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        label_only_iso = Gtk.Label()
        label_only_iso.set_markup("Dry run \n <small>Only generate ISO</small>")
        logo_opt_iso = Gtk.Image.new_from_file(PWD+'/lib/gui_img/cd.png')

        #label_only_iso_name = Gtk.Label()
        #label_only_iso_name.set_markup('File name:')        

        #entry_only_iso = Gtk.Entry()
        try:
          ISO_LABEL_GUI=l_bomsi_gui_lib.read_bomsi_l_vars(PATH_TO_BOMSI)['OUT_ISO_NAME_GUI']
        except:
          ISO_LABEL_GUI='BOMSI-multiboot.iso'
        #entry_only_iso.set_text(ISO_LABEL)

        button_only_iso = Gtk.Button()
        button_only_iso.set_image(logo_opt_iso)
        button_only_iso.connect("clicked", l_bomsi_gui_lib.opt_only_iso,PATH_TO_BOMSI,ISO_LABEL_GUI)


        vbox_iso.pack_start(label_only_iso, False, True, 0)
        vbox_iso.pack_start(button_only_iso, False, True, 0)
        #vbox_iso.pack_start(label_only_iso_name, False, True, 0) 
        #vbox_iso.pack_start(entry_only_iso, False, True, 0) 
    
   
        #Install the ISO on a pendrive
        vbox_pen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        label_iso2pen = Gtk.Label()
        label_iso2pen.set_markup("Create Pendrive \n<small>with auto-installer</small>")
        logo_opt_pen = Gtk.Image.new_from_file(PWD+'/lib/gui_img/pen.png')
        button_iso2pen = Gtk.Button()
        button_iso2pen.set_image(logo_opt_pen)
        ERROR_WIN=self.on_error_clicked
        button_iso2pen.connect("clicked",l_bomsi_gui_lib.create_pendrive, PATH_TO_BOMSI)
        #button_iso2pen.connect("clicked",self.on_error_clicked)

        #If pendrives connected, list them, otherwise raise error
        diskbox = Gtk.Box(spacing=0)
        label_usb = Gtk.Label()

        DISKS=l_bomsi_gui_lib.get_pendrives()
        if len(DISKS) == 0:
          print "Info: no pendrives detected"
          label_usb.set_markup('No pendrives\ndetected!')
          label_usb.set_tooltip_text('Close the window, connect pendrive \n and run this GUI again.')
        else:
          label_usb.set_markup('Use disk:')
          diskbox.pack_start(label_usb, False, False, 0)
          #List of connected pendrives
          disklist=Gtk.ComboBoxText()
          disklist.set_entry_text_column(0)

          for disk in DISKS:
             disklist.append_text(disk)

          disklist.set_entry_text_column(0)
          disklist.connect("changed", l_bomsi_gui_lib.set_selected_disk, disklist, PATH_TO_BOMSI)
          diskbox.pack_start(disklist, False, False, 0)
         
        #currency_combo = Gtk.ComboBoxText()
        #currency_combo.set_entry_text_column(0)
        #for currency in currencies:
        #    currency_combo.append_text(currency)

        #print type(disklist), type(label_usb), DISKS
        vbox_pen.pack_start(label_iso2pen, False, True, 0)
        vbox_pen.pack_start(button_iso2pen, False, True, 0)
        vbox_pen.pack_start(label_usb, False, True, 0)
        vbox_pen.pack_start(diskbox, False, True, 0)




        
        ### Create KVM machines with the ISO(s) ###
        vbox_kvm = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        label_kvm = Gtk.Label()
        label_kvm.set_markup("Local KVM \n<small>use local KVM (virsh)</small>")
        logo_opt_kvm = Gtk.Image.new_from_file(PWD+'/lib/gui_img/kvm.png')

        label_kvm_name = Gtk.Label()
        label_kvm_name.set_markup('Install type:')        

   
        combo_kvm=Gtk.ComboBoxText()
        combo_kvm.set_entry_text_column(0)
        combo_kvm.append_text('2_nodes')
        combo_kvm.append_text('controller')
        #combo_kvm.append_text('network')
        combo_kvm.append_text('compute1')
        combo_kvm.append_text('compute2')
        combo_kvm.append_text('compute3')
        combo_kvm.append_text('clean')
        combo_kvm.append_text('packages')

        combo_kvm.connect("changed", l_bomsi_gui_lib.edit_bomsi_var,'l_vars',PATH_TO_BOMSI,'INSTALL_TYPE',combo_kvm)

        button_kvm = Gtk.Button()
        button_kvm.set_image(logo_opt_kvm)
        button_kvm.connect("clicked", l_bomsi_gui_lib.create_local_virt_env, PATH_TO_BOMSI, combo_kvm)


        vbox_kvm.pack_start(label_kvm, False, False, 0)
        vbox_kvm.pack_start(button_kvm, False, False, 0)
        vbox_kvm.pack_start(label_kvm_name, False, False, 0)
        vbox_kvm.pack_start(combo_kvm, False, False, 0)






        vbox_rkvm = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        label_rkvm = Gtk.Label()
        label_rkvm.set_markup("Remote KVM \n<small>remote KVM server</small>")
        logo_opt_rkvm = Gtk.Image.new_from_file(PWD+'/lib/gui_img/kvm.png')
        button_rkvm = Gtk.Button()
        button_rkvm.set_image(logo_opt_rkvm)
        vbox_rkvm.pack_start(label_rkvm, False, True, 0)
        vbox_rkvm.pack_start(button_rkvm, False, True, 0)
       


        #This is the box with the install options (only iso, pendrive, KVM) 
        row_options = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50,halign=Gtk.Align.CENTER)
        row_options.pack_start(vbox_packages, False, True, 0)
        row_options.pack_start(vbox_iso, False, True, 0)
        row_options.pack_start(vbox_pen, False, True, 0)
        row_options.pack_start(vbox_kvm, False, True, 0)
        #row_options.pack_start(vbox_rkvm, False, True, 0)

        #Add the row with the install options (only iso, pendrive, kvm, ..)
        vbox.pack_start(row_options, False, True, 0)



    def on_button_clicked_info(self, widget):
        dialog = LocalSysInfoModal(self, PWD, PATH_TO_BOMSI)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("The OK button was clicked")
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()



        
    def notebook_vars_show(self, widget, gparam, notebook_vars):
        if widget.get_active():
            state = "on"
            notebook_vars.hide()
        else:
            state = "off"
            notebook_vars.show()
        print("Variables editing dialog visibility turned: ", state)


    def on_button_clicked(self, widget):
        print("Hello World")


    def on_switch_activated(self, switch, gparam):
        if switch.get_active():
            state = "on"
        else:
            state = "off"
        print("Switch was turned", state)


    def on_error_clicked(self, widget):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CANCEL, "No pendrives detected")
        dialog.format_secondary_text(
            "If you want to create a bootable pendrive, close the window, attach a pendrive and try again.")
        dialog.run()
        print("ERROR dialog closed")

        dialog.destroy()



win = Main()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()


