
import re
from yarus.common.const import TASK_ACTIONS

def check_id(ID):
    if ID:
        if re.match("^[a-zA-z0-9]*$", ID):
            return True
        else:
            return False
    else:
        return False

def check_ip(IP):
    if IP:
        if re.match("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", IP):
            return True
        else:
            return False
    else:
        return False

def check_version(version):
    if version:
        if re.match("^[a-zA-z0-9\-\_\.]*$", version):
            return True
        else:
            return False
    else:
        return False

def check_name(name):
    if name:
        if re.match("^[a-zA-z0-9-_. /]*$", name):
            return True
        else:
            return False
    else:
        return False

def check_description(description):
    if description:        
        return True
    else:
        return False

def check_distribution(distribution):
    if distribution:
        if re.match("^[a-zA-z0-9\-\_\.]*$", distribution):
            return True
        else:
            return False
    else:
        return False

def check_type(rtype):
    if rtype:
        if rtype == 'YUM' or rtype == 'APT':
            return True
        else:
            return False
    else:
        return False

def check_status(status):
    if status:
        if status == 'pending' or status == 'running' or status == 'failed' or status == 'completed':
            return True
        else:
            return False
    else:
        return False

def check_objecttype(object_type):
    if object_type:
        if object_type == 'repository' or object_type == 'task' or object_type == 'client' or object_type == 'group' or object_type == 'scheduled' or object_type == 'channel':
            return True
        else:
            return False
    else:
        return False

def check_action(action):
    if action:
        if action in TASK_ACTIONS:
            return True
        else:
            return False
    else:
        return False

def check_url(url):
    if url:
        if re.match("^https?:\/\/([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$", url):
            return True
        else:
            return False
    else:
        return False

def check_release(release):
    if release:
        if re.match("^[a-zA-z0-9\-\_\.]*$", release):
            return True
        else:
            return False
    else:
        return False
        
def check_components(components):
    if components:
        if re.match("^[a-zA-z0-9\-\_\.,]*$", components):
            return True
        else:
            return False
    else:
        return False

def check_architectures(architectures):
    if architectures:
        if re.match("^[a-zA-z0-9\-\_\.,]*$", architectures):
            return True
        else:
            return False
    else:
        return False

def check_channels(channels):
    if channels:
        if re.match("^[a-zA-z0-9;]*$", channels):
            return True
        else:
            return False
    else:
        return False

        