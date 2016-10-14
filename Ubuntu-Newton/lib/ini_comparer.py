#! /usr/bin/env python

## ini_comparer
## Compare 2 "ini" configuration files, one local and the other one remote
## Usage: ./ini_comparer.py PATH_TO_FILE  USER@HOST
## Example: ./ini_comparer.py /etc/nova/nova.conf  root@openstack2

import os,sys,sets
import subprocess

if len(sys.argv) < 3:
  print "ERROR: ini_comparer takes 2 arguments"
  print "Usage: ./ini_comparer.py PATH_TO_FILE  USER@HOST"
  sys.exit()


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


terminal_width=int(os.popen('stty size', 'r').read().split()[1])



## This function checks the command line arguments, and tries to guess
## whether the argument contains an "@"(=>remote) or ":"(=>path) and if 
## not, assumes the argument is directly a file name or full path
## ... and returns a tuple with 2 elements: a list with each line of the 
## file and the file name of the first file
file1=""
def get_file(arg,file1):
  if "@" in arg:
    print  "The argument "+arg+" refers to a remote file."
    host=arg.split(':')[0]
    if ":" in arg:
      #print "phf 0:", arg
      cfile=arg.split(':')[1]
      file1=cfile
      #print "phf 0.1:", host, cfile
    else:
      #File not set, if file1 was set, this is the 2nd file, so use the same as in the 1st one
      if file1 != "": 
        cfile=file1
      else:
        print "you must provide at lest one file name"
        sys.exit()
  else:
    print "The argument "+arg+" is a file."
    cfile=arg
    file1=cfile
  #print "phf 1:", cfile

  try:
    host
    #print "phf 2:", host
    # If the ssh keys were not set
    try:
      output=subprocess.check_output('ssh -oBatchMode=yes ' + host + ' echo "Y" ', shell=True)
    # Set ssh keys
    except:
      print "Adding ssh-key for ", host
      subprocess.check_output('ssh-copy-id ' + host)    
    # Load remote file into confraw list, line by line
    confraw = subprocess.check_output('ssh -oBatchMode=yes ' + host + ' cat '+ cfile, shell=True).split('\n')
    #ssh = subprocess.Popen(['ssh', host, 'cat', cfile], stdout=subprocess.PIPE)
    #print "phf 3:", ssh.readlines()
    #confraw=ssh.stdout.readlines()

    if len(confraw) < 1:
      print "ERROR: The config seems wrong, it has only ", len(confraw), "lines"
      sys.exit()
  except:
    confraw=open(cfile,"r").readlines()
    #print "phf 4:", confraw
   
  conf_lst=[]
  for line in confraw:
    # If lines are not "empty" or commented
    if len(line)>3 and not line.startswith('#') and not line.startswith(';'): 
      conf_lst.append(line.strip(' \t\n\r'))
    
  #print "phf 5:", file1, "AA"
  return list(conf_lst), file1





## This function takes a list with each line of the conf file and returns
## another list of lists. Each sublist contains the section name and a dictionary
## with "key = value" for each section
def conf_lst_dict(conf_lst):
  tmp_dict=dict()  # temporal dictionary, to be appended to each element of conf_lst_dict_out
  conf_lst_dict_out=[]

  for line in conf_lst:
    #print "##Line in conf_list", line
    ## If line contains a section title
    if line[0] == "[" and "]" in line:
      #print "yes",tmp_dict, len(tmp_dict)
      ## Avoid stuff before the first section
      if len(conf_lst_dict_out) > 0:
        tmp_dict_copy=tmp_dict.copy()
        conf_lst_dict_out[-1].append(tmp_dict_copy)  



#       ## The dictionary of keywords is alredy collected
#       if len(tmp_dict) > 0:
#         #print "AAAA",conf1_sections[-1]
#         tmp_dict_copy=tmp_dict.copy()
#         conf_lst_dict_out[-1].append(tmp_dict_copy)
#         print "DDDDD", tmp_dict_copy
#       else:
#         print "#########", conf_lst_dict_out
#         print "#########A", conf_lst_dict_out[-1]
#         emty=dict()
#         conf_lst_dict_out[-1].append(empty)
        

      conf_lst_dict_out.append([line.strip('[]')])
      tmp_dict.clear()
    else:
      # Parse also keys without value
      if "=" in line:
        key=line.split("=")[0].strip()
        value=line.split("=")[1].strip()
        tmp_dict[key]=value
      else:
        key=line
        tmp_dict[key]="NOVALUE"

  conf_lst_dict_out[-1].append(tmp_dict)
      
  return conf_lst_dict_out
      
#print " "
#print " "
#print " "
#print " "


##
##  Load the config files and give them format 
##

conf_list1=get_file(sys.argv[1],file1)
file1=conf_list1[1]

#print "BBBBBBBBB", conf_list1[0]
conf_lst_dict1 = conf_lst_dict(conf_list1[0])


conf_list2=get_file(sys.argv[2],file1)
conf_lst_dict2=conf_lst_dict(conf_list2[0])


## Lists of sections on each file
sections1=[conf_lst_dict1[i][0] for i in range(len(conf_lst_dict1))]
sections2=[conf_lst_dict2[i][0] for i in range(len(conf_lst_dict2))]

## Sum of unique elements
## Can be done shorter with 'Set', but it doesn't keep the order
all_sections= sections1 + list(set(sections2) - set(sections1))
#ddall_sections= list(sets.Set(sections1+sections2)) #sections1 + list(set(sections2) - set(sections1))
#print all_sections

## Find sections of section_i missing in all_sections
def miss_sec(sec_i,all_sections):
  sec_diff=list(sets.Set(all_sections).difference(sets.Set(sec_i)))
  secstr=""
  for s in sec_diff:
    if secstr == "":
      secstr=s
    else:
      secstr=secstr+", "+s
  return secstr

#print miss_sec(sections1,all_sections)
#print miss_sec(sections2,all_sections)
   



sec_collect=[] # this collects the data for printing everything at once
equal_sections=[] # this collects the sections without differences

#def diff_keys(conf_file,section):
if 1:
  for section in all_sections:

    ## Find the index of "section" element in conf_sec_dict list
    if section in sections1:
      #print "PPPP",section, sections1
      idx1 = sections1.index(section)
      #print "MMMM",conf_lst_dict1[idx1]
      conf_sec_dict1=conf_lst_dict1[idx1][1]
      all_keys1=conf_lst_dict1[idx1][1].keys()
      #print all_keys1
    else:
      all_keys1=[]

    if section in sections2:
      idx2 = sections2.index(section)
      conf_sec_dict2=conf_lst_dict2[idx2][1]
      all_keys2=conf_lst_dict2[idx2][1].keys()
      #print all_keys2
    else:
      all_keys2=[]
    
    all_keys=sets.Set(all_keys1+all_keys2)
    #print all_keys
    #print "Keyword(s) "+ miss_sec(all_keys2,all_keys)+" is missing in section "+section 
    
    #str_sec=str("  "+section+ "  ")
    #sec_title=str_sec.center(terminal_width, '-')
#
#    print sec_title

    
    keys_equal=True
    sec_collect.append([section])

    for key in all_keys:
      if conf_sec_dict1.get(key):
         val1=conf_sec_dict1.get(key)
      else:
         val1=""
      if conf_sec_dict2.get(key):
         val2=conf_sec_dict2.get(key)
      else:
         val2=""

      if val1 != val2: 
        sec_collect[-1].append([key, val1, val2])
        #print '{:>35} = {}{:>35}{} {}{:>35}{} '.format(key,bcolors.OKBLUE, val1, bcolors.ENDC, bcolors.OKGREEN, val2,bcolors.ENDC) 
        keys_equal=False
      #else:
      #  print "OK",key,val1

    if keys_equal == True:
      equal_sections.append(section)


##
##  From here on comes the final printing
##


titlestr = " Comparing configuration files with ini_comparer " 
print " "
print bcolors.RED + titlestr.center(terminal_width, '=') + bcolors.ENDC
print " "


eq_str="" # equal sections in string format, separated by comma
if len(equal_sections) > 0:
  for sec in equal_sections:
    if eq_str == "":
      eq_str=sec
    else:
      eq_str=eq_str+", "+sec

  print '{}  {}{}{}'.format("These sections are identic: ",bcolors.BOLD, eq_str, bcolors.ENDC) 



print " "
 
str_title=str(" "+bcolors.BLUE+sys.argv[1]+bcolors.ENDC+" ============================== "+bcolors.GREEN+sys.argv[2]+bcolors.ENDC+ " ")
print '----------------'+str_title.center(terminal_width, '-')+'--'
print " "
 
## Print only the sections with differences
for diff_sec in sec_collect:
  if len(diff_sec) > 1:
    ## Set header of each different section
    str_sec=str("  "+diff_sec[0]+ "  -------")
    sec_title=str_sec.center(terminal_width, '-')
    print sec_title

    for diff in diff_sec[1:]:
      key,val1,val2=diff[0],diff[1],diff[2]
      if val1 != "NOVALUE" and val2 != "NOVALUE":
        print '{:>30} = {}{:>45}{} {}{:>45}{} '.format(key,bcolors.BLUE, val1, bcolors.ENDC, bcolors.GREEN, val2,bcolors.ENDC) 
      else:
        print '{:>40}     {} xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx {} '.format(key,bcolors.YELOW,bcolors.ENDC) 
 

print ''.center(terminal_width, '-')

## Print everything
#for section in all_sections:
#
  












sys.exit()


matching_sections=[]
print "### Differences in configuration files"

for section in all_sections:
   if section:
     print "sec",section
     try:
       idx1 = sections1.index(section)
       conf1_sec_dict = conf1_list[idx1][1]
       print "here", conf1_sec_dict
     except:
       conf1_sec_dict={}
   
     try:
       print "OOOOOOOOOOOOOOOOOOOOOOO"
       idx2 = sections2.index(section)
       print "HHHH", idx2
       conf2_sec_dict = conf2_list[idx2][1]
       print "there", conf2_sec_dict
     except:
       conf2_sec_dict={}

     keys1 = sets.Set(conf1_sec_dict.keys())
     keys2 = sets.Set(conf2_sec_dict.keys())

     all_keys= sets.Set(conf1_sec_dict.keys()+conf2_sec_dict.keys())
     #print all_keys


     keys21=keys2.difference(keys1)
     keys12=keys1.difference(keys2)
     if len(keys21) > 0:
       #print "### keys missing on list 1"
       #print keys21
       keys21_missing=keys21

     if len(keys12) > 0:
       #print "### keys missing on list 2"
       #print keys12
       keys12_missing=keys12

     #if len(keys21) > 0 or len(keys12) > 0:
     #  print ' missing on localhost                 missing on remote'
     #  print '  {:<50}   {:<50}'.format(list(keys21), list(keys12))
     #  print ' '

     diffvars=[]
     for key in list(all_keys):
       val1,val2="",""
       try:
         conf1_sec_dict[key]
         val1=conf1_sec_dict[key]
         #print key+ " = " + conf1_sec_dict[key] 
       except:
         1
         #print "## Config file 1 missing key ", key

       try:
         conf2_sec_dict[key]
         val2=conf2_sec_dict[key]
         #print key+ " = " + conf2_sec_dict[key] 
       except:
         1
         #print "## Config file 1 missing key ", key


       if val1 != val2:
         diffvars.append([key,val1,val2])
     
     if len(diffvars) > 1:
       print " " 
       print "> On section "+section
       
       for line in diffvars:
         key,val1,val2=line[0],line[1],line[2]
         if len(key) < 20:
           print '{:>20} = {}{:>35}{} {}{:>35}{} '.format(key,bcolors.OKBLUE, val1, bcolors.ENDC, bcolors.OKGREEN, val2,bcolors.ENDC) 
         else:
           print '{:<35} = {}{:>27}{} {}{:>27}{} '.format(key,bcolors.OKBLUE, val1, bcolors.ENDC, bcolors.OKGREEN, val2,bcolors.ENDC) 

     else:
       matching_sections.append(section)





























## Sections Missing in conf1
sec21=list(sets.Set(sections2).difference(sets.Set(sections1)))
sec21str=""
for sec in sec21:
  print sec
  if sec21str != "":
    sec21str=sec21str+", "+sec.strip('[]')
  else:
    sec21str=sec.strip('[]')
    
#print "sec21",sec21
#print sec21str

## Sections Missing in conf2
sec12=list(sets.Set(sections1).difference(sets.Set(sections2)))
sec12str=""
for sec in sec12:
  if sec12str != "":
    sec12str=sec12str+", "+sec.strip('[]')
  else:
    sec12str=sec.strip('[]')





##
##  First file
##

if "@" in sys.argv[1]:
  print sys.argv[1]
  if ":" in sys.argv[1]:
    host1=sys.argv[1].split(':')[0]
    file1=sys.argv[1].split(':')[1]
  else:
    print "you must provide at lest one file name"
    sys.exit()
else:
  file1=sys.argv[1]



## If 1st arg is remote or a local file
try:
  host1
  try:
    output=subprocess.check_output('ssh -oBatchMode=yes ' + host1 + ' echo "Y" ', shell=True)
    #os.system('ssh -oBatchMode=yes ' + host1 + ' echo "" ')
    #print "IIII YES", output
  except:
    print "Adding ssh-key for ", host1    
    os.system('ssh-copy-id ' + host1 + ' 2> /dev/null')
    #print "IIII NO"
  ssh = subprocess.Popen(['ssh', host1, 'cat', file1], stdout=subprocess.PIPE)
  conf1raw=ssh.stdout.readlines()
except:
  conf1raw=open(file1,"r").readlines()
    


conf1_list=[[]]
tmp_dict=dict()

for line in conf1raw:
   line_tmp=line.strip(' \t\n\r')
   if len(line_tmp) > 4:
     if line_tmp[0] == "[" and "]" in line:
       #print "##############''''"
       #print "catch",line_tmp, len(tmp_dict), type(tmp_dict), type(conf1_sections[0]),conf1_sections[-1], tmp_dict
       if len(tmp_dict) >0:
         #print "AAAA",conf1_sections[-1]
         tmp_dict_copy=tmp_dict.copy()
         conf1_list[-1].append(tmp_dict_copy)
       conf1_list.append([line_tmp])
       tmp_dict.clear()
     else:
       key=line_tmp.split("=")[0].strip()
       value=line_tmp.split("=")[1].strip()
       tmp_dict[key]=value
conf1_list[-1].append(tmp_dict)
conf1_list.pop(0)

#for item in conf1_list:
#  print item
#  print " "


##
##  Second file
##



if "@" in sys.argv[2]:
  if ":" in sys.argv[2]:
    host2=sys.argv[2].split(':')[0]
    file2=sys.argv[2].split(':')[1]
  else:
    host2=sys.argv[2].split(':')[0]
    file2=file1 
else:
  file2=sys.argv[2]

print host2, file2

## If 1st arg is remote or a local file
try:
  host2
  try:
    output=subprocess.check_output('ssh -oBatchMode=yes ' + host2 + ' echo "Y" ', shell=True)
    #os.system('ssh ' + host2 + ' echo "" &> /dev/null')
    #print "IIII YES",output
  except:    
    print "Adding ssh-key for ", host2    
    os.system('ssh-copy-id ' + host2 + ' 2> /dev/null')
    #print "IIII NO"
  ssh = subprocess.Popen(['ssh', host2, 'cat', file2], stdout=subprocess.PIPE)
  conf2raw=ssh.stdout.readlines()
except:
  conf12raw=open(file1,"r").readlines()



#conf2raw=ssh.stdout.readlines()

#for line in ssh.stdout:
#    line  # do stuff

#print type(ssh), type(ssh.stdout)
#print ssh.stdout

#conf2raw=open(sys.argv[2],"r").readlines()

conf2_list=[[]]
tmp_dict.clear()
tmp_dict_copy.clear()

for line in conf2raw:
   line_tmp=line.strip(' \t\n\r')
   if len(line_tmp) > 4:
     if line_tmp[0] == "[" and "]" in line:
       if len(tmp_dict) >0:
         tmp_dict_copy=tmp_dict.copy()
         conf2_list[-1].append(tmp_dict_copy)
       conf2_list.append([line_tmp])
       tmp_dict.clear()
     else:
       key=line_tmp.split("=")[0].strip()
       value=line_tmp.split("=")[1].strip()
       tmp_dict[key]=value
conf2_list[-1].append(tmp_dict)
conf2_list.pop(0)


#for item in conf2_list:
#  print item
#  print " "



## Lists of sections on each file
sections1=[conf1_list[i][0] for i in range(len(conf1_list))]
sections2=[conf2_list[i][0] for i in range(len(conf2_list))]

## Sum of unique elements
all_sections= sections1 + list(set(sections2) - set(sections1))

#print all_sections

## Sections Missing in conf1
sec21=list(sets.Set(sections2).difference(sets.Set(sections1)))
sec21str=""
for sec in sec21:
  print sec
  if sec21str != "":
    sec21str=sec21str+", "+sec.strip('[]')
  else:
    sec21str=sec.strip('[]')
    
#print "sec21",sec21
#print sec21str

## Sections Missing in conf2
sec12=list(sets.Set(sections1).difference(sets.Set(sections2)))
sec12str=""
for sec in sec12:
  if sec12str != "":
    sec12str=sec12str+", "+sec.strip('[]')
  else:
    sec12str=sec.strip('[]')
    


##
##  Differences in configuration files
##

matching_sections=[]
print "### Differences in configuration files"

for section in all_sections:
   if section:
     print "sec",section
     try:
       idx1 = sections1.index(section)
       conf1_sec_dict = conf1_list[idx1][1]
       print "here", conf1_sec_dict
     except:
       conf1_sec_dict={}
   
     try:
       print "OOOOOOOOOOOOOOOOOOOOOOO"
       idx2 = sections2.index(section)
       print "HHHH", idx2
       conf2_sec_dict = conf2_list[idx2][1]
       print "there", conf2_sec_dict
     except:
       conf2_sec_dict={}

     keys1 = sets.Set(conf1_sec_dict.keys())
     keys2 = sets.Set(conf2_sec_dict.keys())

     all_keys= sets.Set(conf1_sec_dict.keys()+conf2_sec_dict.keys())
     #print all_keys


     keys21=keys2.difference(keys1)
     keys12=keys1.difference(keys2)
     if len(keys21) > 0:
       #print "### keys missing on list 1"
       #print keys21
       keys21_missing=keys21

     if len(keys12) > 0:
       #print "### keys missing on list 2"
       #print keys12
       keys12_missing=keys12

     #if len(keys21) > 0 or len(keys12) > 0:
     #  print ' missing on localhost                 missing on remote'
     #  print '  {:<50}   {:<50}'.format(list(keys21), list(keys12))
     #  print ' '

     diffvars=[]
     for key in list(all_keys):
       val1,val2="",""
       try:
         conf1_sec_dict[key]
         val1=conf1_sec_dict[key]
         #print key+ " = " + conf1_sec_dict[key] 
       except:
         1
         #print "## Config file 1 missing key ", key

       try:
         conf2_sec_dict[key]
         val2=conf2_sec_dict[key]
         #print key+ " = " + conf2_sec_dict[key] 
       except:
         1
         #print "## Config file 1 missing key ", key


       if val1 != val2:
         diffvars.append([key,val1,val2])
     
     if len(diffvars) > 1:
       print " " 
       print "> On section "+section
       
       for line in diffvars:
         key,val1,val2=line[0],line[1],line[2]
         if len(key) < 20:
           print '{:>20} = {}{:>35}{} {}{:>35}{} '.format(key,bcolors.OKBLUE, val1, bcolors.ENDC, bcolors.OKGREEN, val2,bcolors.ENDC) 
         else:
           print '{:<35} = {}{:>27}{} {}{:>27}{} '.format(key,bcolors.OKBLUE, val1, bcolors.ENDC, bcolors.OKGREEN, val2,bcolors.ENDC) 

     else:
       matching_sections.append(section)


matchstr=""
for match in matching_sections:
  if matchstr != "":
    matchstr=matchstr+", "+match.strip('[]')
  else:
    matchstr=matchstr+match.strip('[]')

print " "
print "Sections matching 100%: "+ bcolors.BOLD + matchstr +bcolors.ENDC

print " "
print 'Secs in 1 but not in 2                                  Secs in 2 but not in 1   '
print '   {:>27}                     {:>27}'.format(sec21str,sec12str)
print " "


#print all_sections

    # print conf1_sec_dict.keys().difference(conf2_sec_dict.keys())





sys.exit()




for section in conf1_sections:
  section={}
  print "s",section

variables = { section:section for section in conf1_sections}

print variables
sys.exit()

for line in conf1raw:
   line_tmp=line.strip(' \t\n\r')
   if len(line_tmp) > 4:
     if line_tmp[0] == "[" and "]" in line:
       last_section=line_tmp
     else:
       key=line_tmp.split("=")[0]
       value=line_tmp.split("=")[1]
       globals()[last_section[key]]=[value]
       print last_section, key, value, #globals()[last_section]
     

for line in conf1list:
  print line



