#!/usr/bin/env python
# coding: utf8

import argparse
import sys
import os
import subprocess
import urllib

if os.geteuid() != 0:
    print("Error: need to run as root.")
    sys.exit(1)

parser = argparse.ArgumentParser()
# adresse IP du server yarus
parser.add_argument('--server', action='store')
# pour configurer ce système
parser.add_argument('--config', action='store_true')
# pour ajouter le système au groupe donner (ID DU GROUPE !!!)
parser.add_argument('--group', action='store')
# infor sur le système
parser.add_argument('-d', '--distribution', action='store')
parser.add_argument('-v', '--version', action='store')
parser.add_argument('-a', '--architecture', action='store')
parser.add_argument('--ip', action='store')
args = parser.parse_args()

if not args.server:    
    print("Error: no YARUS server set.")
    sys.exit(1)

if args.config:
    if os.system("useradd -m yarus"):
        print("Error: couldn't create user yarus.")
        sys.exit(0)
    if os.system("mkdir /home/yarus/.ssh"):
        print("Error: couldn't create .ssh directory in /home/yarus.")
        sys.exit(0)
    if not urllib.urlretrieve ("http://" + args.server + "/keys/authorized_keys", "/home/yarus/.ssh/authorized_keys"):
        print("Error: couldn't retrieve the ssh public key at http://" + args.server + "/keys/authorized_keys.")
        sys.exit(0)
    if os.system("chown -R yarus:yarus /home/yarus/.ssh"):
        print("Error: couldn't change owner of /home/yarus/.ssh.")
        sys.exit(0)
    if os.system("chmod 700 /home/yarus/.ssh"):
        print("Error: couldn't change rights of /home/yarus/.ssh.")
        sys.exit(0)
    if os.system("chmod 600 /home/yarus/.ssh/authorized_keys"):
        print("Error: couldn't change rights of /home/yarus/.ssh/authorized_keys.")
        sys.exit(0)
    if os.system("sudo -V"):
        # rhel and centos come with sudo
        # debian and ubuntu doesn't install it all the time
        if os.system("apt install -y sudo"):
            print("Error: couldn't install sudo.")
            sys.exit(0)
    if os.system("echo \"yarus ALL=(ALL:ALL)   NOPASSWD:ALL\" >> /etc/sudoers"):
        print("Error: couldn't add yarus to the sudoers file.")
        sys.exit(0)

if args.group:
    
    # aller chercher les infos automatiquement n'est pas fiable
    # pour centos et rhel on ne peut pas récupérer la version précise
    # on peut avoir 7 mais pas 7.5.1804
    # pour debian et ubuntu possible

    """
    dist = ""
    version = ""
    arch = ""
    ctype = "YUM"
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

    print(name, dist, version, arch, ctype)
    params = ""
    result = urllib.open("http://" + args.server + ":6821/api/register/" + params).read()
    print(result)
    """

    # donner les informations en params du script
    # avec les options :
    # -d --distribution distribution
    # -v --version version
    # -a --architecture architecture

    name = subprocess.check_output(['hostname']).strip('\n')

    if args.distribution:

        if args.distribution == "centos" or args.distribution == "rhel":
            ctype = "YUM" 
        elif args.distribution == "debian" or args.distribution == "ubuntu":
            ctype = "APT" 
        else:
            print("Error: distribution is not supported.")
            sys.exit(0)

        if args.version:
            if args.architecture:
                params = args.group + "/" + name + "/" + args.ip + "/" + args.distribution + "/" + args.version + "/" + args.architecture + "/" + ctype
                result = urllib.urlopen("http://" + args.server + ":6821/api/register/" + params).read()
                print(result)
            else:
                print("Missing architecture")
        else:
            print("Missing version")
    else:
        print("Missing distribution")