#!/usr/bin/env python
# coding: utf8

import argparse
import sys
import os
import subprocess

if sys.version_info >= (3,0):
    import urllib.request as urllib
else:
    import urllib

if os.geteuid() != 0:
    print("Error: need to run as root.")
    sys.exit(1)

parser = argparse.ArgumentParser()
# adresse IP du server yarus    
parser.add_argument('--server', action='store')
# pour configurer ce systÃ¨me
parser.add_argument('--config', action='store_true')
# pour ajouter le systÃ¨me au groupe donner (ID DU GROUPE !!!)
parser.add_argument('--group', action='store')
# infor sur le systÃ¨me
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
        # debian and ubuntu don't install it all the time
        if os.system("apt install -y sudo"):
            print("Error: couldn't install sudo.")
            sys.exit(0)
    if os.system("echo \"yarus ALL=(ALL:ALL)   NOPASSWD:ALL\" >> /etc/sudoers"):
        print("Error: couldn't add yarus to the sudoers file.")
        sys.exit(0)

    if not os.path.isfile("/usr/bin/python"):
        pythonpath = subprocess.check_output(['whereis', 'python']).decode('utf-8').strip('\n')
        if os.system("ln -s " + pythonpath.split()[1] + " /usr/bin/python"):
            print("Error: /usr/bin/python")
            sys.exit(0)

if args.group:

    dist = ""
    version = ""
    arch = ""
    ctype = ""

    osrelease = open('/etc/os-release', 'r')
    lines = osrelease.readlines()
    for line in lines:
        tmp = line.split('=')
        if tmp[0] == 'ID':
            dist = tmp[1].strip('\n').replace("\"", "")
        elif tmp[0] == 'VERSION':
            version = tmp[1].split('(')[1].split(')')[0]

    arch = subprocess.check_output(['uname', '-r']).split(b'-')[-1].strip(b'\n')
    name = subprocess.check_output(['hostname']).strip(b'\n')

    # donner les informations en params du script
    # avec les options :
    # -d --distribution distribution
    # -v --version version
    # -a --architecture architecture

    if args.distribution:
        dist = args.distribution

    if dist == "centos" or dist == "rhel":
        ctype = "YUM" 
    elif dist == "debian" or dist == "ubuntu":
        ctype = "APT" 
    else:
        print("Error: distribution is not supported (centos, rhel, debian, ubuntu are supported).")
        sys.exit(0)

    if args.version:
        version = args.version

    if args.architecture:
        arch = args.architecture

    print(name, dist, version, arch, ctype)

    params = str(args.group) + "/" + name.decode('utf-8') + "/" + str(args.ip) + "/" + str(dist) + "/" + str(version) + "/" + str(arch) + "/" + str(ctype)
    print("http://" + str(args.server) + ":6821/api/register/" + str(params))
    result = urllib.urlopen("http://" + str(args.server) + ":6821/api/register/" + str(params)).read()
    print(result.decode('utf-8'))

    if "successfully" in result.decode('utf-8'):
        print("ALL OK !")
    else:
        print("Error see previous message.")

