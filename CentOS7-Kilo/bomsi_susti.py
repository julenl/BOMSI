#! /usr/bin/python

# susti
# Substitute a value within a given section in OpenStack config files
#
# Usage: susti config_file section "keyword = value"
# Example: susti /etc/nova/nova.conf keystone_authtoken "username = nova"
import re,sys
parse=0 #parse yes/no
match=0 #match found

if len(sys.argv)<4:
  print ' ## Error: susti takes 3 arguments: susti(.py) file FIELD "keyword=value" ##'
  sys.exit()

config_file=sys.argv[1]
section=sys.argv[2]
sec_re=r"^\["+section+r"\][ -]*"
psearch=sys.argv[3].split("=")[0].rstrip()
preplace=sys.argv[3]


print sys.argv[0], " is setting '"+psearch+"' as '"+preplace+"' in ", config_file
tmpout=open("/tmp/sustilog","a")
print>>tmpout, sys.argv[0], " is setting '", preplace,"' in ", config_file

#out=open('/tmp/susti_tmp','w')
if match == 0: #psearch in section and not commented
  bulk=[]
  for line in open(config_file):
    if re.match(sec_re,line) and parse == 0:
      bulk.append(line.rstrip('\n'))
      parse=1
    elif re.search(r"^[ -]*"+psearch,line) and parse == 1:
      bulk.append(preplace)
      parse,match=0,1
    elif line.startswith(psearch) and match ==1:
      bulk.append("###"+line.rstrip('\n'))
    elif re.search(r"^\[(\w+)\]",line) and parse == 1:
      bulk.append(line.rstrip('\n'))
      parse=0
    else: 
      bulk.append(line.rstrip('\n'))
parse=0


if match == 0: #psearch match exists but line is commented
  bulk=[]
  for line in open(config_file):
    if re.match(sec_re,line) and parse == 0:
      bulk.append(line.rstrip('\n'))
      parse=1
    elif re.search(r"^\#[ -]*"+psearch,line) and parse == 1:
      bulk.append(preplace)
      parse,match=0,1
    elif re.search(r"^\[(\w+)\]",line) and parse == 1:
      bulk.append(line.rstrip('\n'))
      parse=0
    else: 
      bulk.append(line.rstrip('\n'))

if match == 0: #psearch not found in section, appeding to section label
  print "3", match
  bulk=[]
  for line in open(config_file):
    #if re.search(sec_re,line):
    if line.startswith("["+section+"]"):
      bulk.append(line.rstrip('\n'))
      bulk.append(preplace)
      match=1
    else: 
      bulk.append(line.rstrip('\n'))

if match == 0: #section not found, appending section and preplace at the bottom
  print "4", match
  bulk=[]
  for line in open(config_file):
    bulk.append(line.rstrip('\n'))
  bulk.append(" ")
  bulk.append("["+section+"]")
  bulk.append(preplace)

out=open(config_file,'w')
for i in bulk:
 print>>out, i

  
