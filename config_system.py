#!/usr/bin/env python

import argparse
import sys
import os
import subprocess
import urllib

if os.geteuid() != 0:
    print("Error: need to run as root.")
    sys.exit(1)

parser = argparse.ArgumentParser()

parser.add_argument('--server', action='store')

args = parser.parse_args()

name = ""
dist = ""
version = ""
arch = ""
ctype = "APT"

if args.server:
    """
    osrelease = open('/etc/os-release', 'r')
    lines = osrelease.readlines()
    for line in lines:
        tmp = line.split('=')
        if tmp[0] == 'ID':
            dist = tmp[1].strip('\n')
        elif tmp[0] == 'VERSION':
            version = tmp[1].split('(')[1].split(')')[0]

    arch = subprocess.check_output(['uname', '-r']).split('-')[-1].strip('\n')
    name = subprocess.check_output(['hostname']).strip('\n')
    """
    if os.system("useradd -m yarus"):
        print("Error: couldn't create user yarus.")
        sys.exit(0)
    else:
        print("yarus user created")

    if os.system("mkdir /home/yarus/.ssh"):
        print("Error: couldn't create .ssh directory in /home/yarus.")
        sys.exit(0)
    else:
        print("/home/yarus/.ssh directory created")    

    if not urllib.urlretrieve ("http://" + args.server + "/keys/authorized_keys", "/home/yarus/.ssh/authorized_keys"):
        print("Error: couldn't retrieve the ssh public key at http://" + args.server + "/keys/authorized_keys.")
        sys.exit(0)
    else:
        print("ssh key downloaded")

    if os.system("chown -R yarus:yarus /home/yarus/.ssh"):
        print("Error: couldn't change owner of /home/yarus/.ssh.")
        sys.exit(0)
    else:
        print("changed owner of /home/yarus/.ssh")

    if os.system("chmod 700 /home/yarus/.ssh"):
        print("Error: couldn't change rights of /home/yarus/.ssh.")
        sys.exit(0)
    else:
        print("changed rights of /home/yarus/.ssh")

    if os.system("chmod 600 /home/yarus/.ssh/authorized_keys"):
        print("Error: couldn't change rights of /home/yarus/.ssh/authorized_keys.")
        sys.exit(0)
    else:
        print("changed rights of /home/yarus/.ssh/authorized_keys")

    if os.system("echo \"yarus ALL=(ALL:ALL)   NOPASSWD:ALL\" >> /etc/sudoers"):
        print("Error: couldn't add yarus to the sudoers file.")
        sys.exit(0)
    else:
        print("added yarus to sudoers file")
    
    """
    print(name, dist, version, arch, ctype)
    params = ""
    result = urllib.open("http://" + args.server + ":6821/api/register/" + params).read()
    print(result)
    """

else:
    print("Error: no YARUS server set.")
    sys.exit(1)