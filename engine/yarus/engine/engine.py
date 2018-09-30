
"""
    YARUS Engine is the API RESTful
"""

import sys
import requests
import hashlib
import smtplib
from email.mime.text import MIMEText
from flask import Flask, json, jsonify, request
from yarus.engine.crontab import Crontab
from yarus.common.app import App
from yarus.common.repository import Repository
from yarus.common.channel import Channel
from yarus.common.client import Client
from yarus.common.group import Group
from yarus.common.task import Task
from yarus.common.scheduled import Scheduled
from yarus.common.bind import Bind
from yarus.common.link import Link
from yarus.common.grouped import Grouped
from yarus.common.linkrcs import Linkrcs
from yarus.common.exceptions import InvalidValueException, DatabaseError
from yarus.common.functions import *
from yarus.common.user import User

# ========== flasks context ==========

APP = Flask("Yarus Engine")
APP_ENGINE = App(debug=True)

if not APP_ENGINE.start():
    APP_ENGINE.log.error("Error while starting Yarus Engine.")
    sys.exit(1)

# ========== functions ==========

def extract_data():
    """ return json data from the request """
    try:
        data = json.loads(request.data)
    except ValueError as error:
        APP_ENGINE.log.debug(str(error))
        return None
    return data

def getconnecteduser():
    """ get information about the user who's doing the request """
    try:
        data = extract_data()

        if not data:
            return False

        username = None
        password = None
        token = None

        # getting information about the user
        if 'user' in data:
            if 'username' in data['user'] and 'password' in data['user']:
                username = data['user']['username']
                password = data['user']['password']
            elif 'token' in data['user']:
                token = data['user']['token']
            else:
                return False
        else:
            return False

        # the user
        tmp_user = User()
        try:
            if username and password:
                tmp_user.setName(username)
                tmp_user.setPassword(password)
            elif token:
                tmp_user.setToken(token)
        except InvalidValueException as error:
            return False

        # checkout user
        user = connectuser(APP_ENGINE, tmp_user)
        if not user:
            return False
        return user

    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return False

# ========== messages ==========

message_database_error = "Database error. If this error persist please contact the administrator."
message_session_error = "You're not connected."
message_json_error = "Can't read the data because it is not proper JSON fomart."

# ========== executed before and after the creation of the response ==========

@APP.before_request
def before_request():
    try:
        APP_ENGINE.database.connect()
    except:
        APP_ENGINE.log.log(error)

@APP.after_request
def after_request(response):
    try:
        APP_ENGINE.database.close()
    except:
        APP_ENGINE.log.log(error)
    return response

# ========== routes ==========

@APP.route('/api/login', methods=['GET'])
def login():
    """ login """
    try:
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "Error user."})
        # user is valid so generate a new token for the session
        user.setToken(getnewid())
        user.update(APP_ENGINE.database)
        user.password = ""
        data = user.todata()
        return jsonify({"status": 0, "message": "", "data": data})
    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/login/check/<string:token>', methods=['GET'])
def checklogin(token):
    """ check login """
    try:        
        tmp_user = User()
        tmp_user.setToken(token)
        # checkout user
        user = connectuser(APP_ENGINE, tmp_user)
        if not user:
            return jsonify({"status": 1, "message": "Token expired."})
        return jsonify({"info_user": "", "status": 0, "message": "Token is valid."})
    
    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/list/<string:object_name>', methods=['GET'])
def list_object(object_name):
    """ return the list of all the object of the given type """
    try:
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # get the list of the object and return it
        if object_name == 'repository':
            if user.role_id == 1:
                data = APP_ENGINE.database.get_all_object('yarus_repository')
            elif user.role_id == 2:
                data = APP_ENGINE.database.get_all_object_own('yarus_repository', user)
            else:
                return jsonify({"status": -1, "message": "You do not have the right to see " + object_name + " list."})
        elif object_name == 'user':
            if user.role_id == 1:
                data = APP_ENGINE.database.get_all_object('yarus_user')
            else:
                return jsonify({"status": -1, "message": "You do not have the right to see " + object_name + " list."})
        elif object_name == 'channel':
            if user.role_id == 1:
                data = APP_ENGINE.database.get_all_object('yarus_channel')
            elif user.role_id == 2:
                data = APP_ENGINE.database.get_all_object_own('yarus_channel', user)
            else:
                return jsonify({"status": -1, "message": "You do not have the right to see " + object_name + " list."})
        elif object_name == 'client':
            if user.role_id == 1:
                data = APP_ENGINE.database.get_all_object('yarus_client')
            elif user.role_id == 3:
                data = APP_ENGINE.database.get_all_object_own('yarus_client', user)
            else:
                return jsonify({"status": -1, "message": "You do not have the right to see " + object_name + " list."})
        elif object_name == 'group':
            if user.role_id == 1:
                data = APP_ENGINE.database.get_all_object('yarus_group')
            elif user.role_id == 3:
                data = APP_ENGINE.database.get_all_object_own('yarus_group', user)
            else:
                return jsonify({"status": -1, "message": "You do not have the right to see " + object_name + " list."})            
        elif object_name == 'task':
            if user.role_id == 1:
                data = APP_ENGINE.database.get_all_object('yarus_task')
            else:
                 data = APP_ENGINE.database.get_all_object_own('yarus_task', user)             
        elif object_name == 'scheduled':
            if user.role_id == 1:
                data = APP_ENGINE.database.get_all_object('yarus_scheduled')
            else:
                data = APP_ENGINE.database.get_all_object_own('yarus_scheduled', user)              
        elif object_name == 'linkrcs':            
            if user.role_id == 1:
                data = APP_ENGINE.database.get_all_object('yarus_linkrcs')
            else:
                return jsonify({"status": -1, "message": "You do not have the right to see configuration list."})
        elif object_name == 'update':
            data = APP_ENGINE.database.get_all_updates()

        if data:
            return jsonify({"status": 0, "message": "", 'data': data})
        return jsonify({"status": -1, "message": "No " + object_name + " found.", 'data': data})

    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/see/<string:object_name>/<string:object_id>', methods=['GET'])
def see_object(object_name, object_id):
    """ return the information of the object of the given type with the given id """
    try:
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # get the object and return its information
        object_data = getobject(APP_ENGINE, object_name, object_id)
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_name + " found with the given ID (" + object_id + ")."})

        if user.role_id != 1:
            if hasattr(object_data, 'manager_id'):
                if user.ID != object_data.manager_id:
                    return jsonify({"status": 103, "message": "You do not have the permission to see this " + object_name})

        # if it's a user we don't send the password hash
        if object_name == "user":
            object_data.password = ""

        data = object_data.todata()

        return jsonify({"status": 0, "message": "", 'data': data})

    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/create/<string:object_name>', methods=['POST'])
def create_object(object_name):
    """ create an object of the given type """
    try:
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": message_json_error})

        # validate information and create the new object
        try:
            if object_name == 'repository':
                new_object = Repository()
                new_object.setID(getnewid())
                new_object.setName(data['repository']['name'])
                new_object.setDescription(data['repository']['description'])
                new_object.setURL(data['repository']['URL'])
                new_object.setType(data['repository']['type'])
                new_object.setDistribution(data['repository']['distribution'].lower())
                new_object.setRelease(data['repository']['release'].lower())
                new_object.setArchitectures(data['repository']['architectures'])
                if new_object.type == 'APT':
                    new_object.setPath(data['repository']['path'])
                    new_object.setComponents(data['repository']['components'])
                new_object.setManagerID(user.ID)
                new_object.setCreationDate()
                new_object.last_sync = 0

                # check if the repository already exist in the database
                if getrepobyname(APP_ENGINE, new_object.name):
                    return jsonify({"status": 102, "message": "Repository with the name " + new_object.name + " already exists in the database."})

                # check if we can reach the remote url
                try:
                    if APP_ENGINE.config.px_host != None and APP_ENGINE.config.px_port != None:
                        proxies = {
                            "http"  : str(APP_ENGINE.config.px_host) + ":" + str(APP_ENGINE.config.px_port)
                        }
                        if requests.get(new_object.URL, proxies=proxies).status_code != 200:
                            return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + new_object.URL + "."})
                    else:
                        if requests.get(new_object.URL).status_code != 200:
                            return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + new_object.URL + "."})                    

                except requests.ConnectionError as error:
                    return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + new_object.URL + ". " + str(error)})
            elif object_name == 'channel':
                new_object = Channel()
                new_object.setID(getnewid())
                new_object.setName(data['channel']['name'])
                new_object.setDescription(data['channel']['description'])
                new_object.setDistribution(data['channel']['distribution'].lower())
                new_object.setRelease(data['channel']['release'].lower())
                new_object.setManagerID(user.ID)
                new_object.setCreationDate()

                 # check if the channel already exist in the database
                if getchannelbyname(APP_ENGINE, new_object.name):
                    return jsonify({"status": 102, "message": "Channel with the name " + new_object.name + " already exists in the database."})
            elif object_name == 'user':
                new_object = User()
                new_object.setID(getnewid())
                password = getnewpassword()
                sha256_hash = hashlib.sha256()
                sha256_hash.update(password.encode('utf-8'))
                hashed_password = sha256_hash.hexdigest()
                new_object.password = hashed_password
                new_object.setName(data['nuser']['name'])
                new_object.setMail(data['nuser']['mail'])
                new_object.setRoleID(data['nuser']['role_id'])
                new_object.token = ""
                new_object.token_expire = 0
                new_object.setCreationDate()

                if APP_ENGINE.database.check_unique_mail(new_object.mail):
                     return jsonify({"status": 1, "message": "This mail address is already taken."})
                if APP_ENGINE.database.check_unique_username(new_object.name):
                     return jsonify({"status": 1, "message": "This user name is already taken."})
                
                # check if the channel already exist in the database
                if getchannelbyname(APP_ENGINE, new_object.name):
                    return jsonify({"status": 102, "message": "Channel with the name " + new_object.name + " already exists in the database."})
            elif object_name == 'client':
                new_object = Client()
                new_object.setID(getnewid())
                new_object.setIP(data['client']['IP'])
                new_object.setName(data['client']['name'])
                new_object.setDescription(data['client']['description'])
                new_object.setVersion(data['client']['version'])
                new_object.setType(data['client']['type'])
                new_object.setDistribution(data['client']['distribution'])
                new_object.setArchitecture(data['client']['architecture'])
                new_object.setManagerID(user.ID)
                new_object.setCreationDate()
                
                # check if the client already exist in the database
                if getclientbyip(APP_ENGINE, new_object.IP):
                    return jsonify({"status": 102, "message": "Client with the IP " + new_object.IP + " already exists in the database."})
            elif object_name == 'group':
                new_object = Group()
                new_object.setID(getnewid())
                new_object.setName(data['group']['name'])
                new_object.setDescription(data['group']['description'])
                new_object.setManagerID(user.ID)
                new_object.setCreationDate()
                # check if the repository already exist in the database
                if getgroupbyname(APP_ENGINE, new_object.name):
                    return jsonify({"status": 102, "message": "Group with the name " + new_object.name + " already exists in the database."})
            elif object_name == 'task':
                new_object = Task()
                new_object.setID(getnewid())
                new_object.setStatus('pending')
                new_object.setCreationDate()
                new_object.setAction(data['task']['action'])
                new_object.setObjectID(data['task']['object_id'])
                new_object.setObjectType(data['task']['object_type'])
                # check if the object exist
                object_data = getobject(APP_ENGINE, new_object.object_type, new_object.object_id)
                if not object_data:
                    return jsonify({"status": 100, "message": "No " + new_object.object_type + " found with the given ID (" + new_object.object_id + ")."})
                new_object.setObjectName(object_data.name)
                new_object.setManagerID(user.ID)
            elif object_name == 'scheduled':
                new_object = Scheduled()
                new_object.setID(getnewid())
                new_object.setCreationDate()
                new_object.last_date = 0
                new_object.setName(data['scheduledtask']['name'])
                new_object.setDescription(data['scheduledtask']['description'])
                new_object.setHour(data['scheduledtask']['hour'])
                new_object.setMinute(data['scheduledtask']['minute'])
                new_object.setDayofmonth(data['scheduledtask']['day_of_month'])
                new_object.setMonth(data['scheduledtask']['month'])
                new_object.setAction(data['scheduledtask']['action'])
                new_object.setObjectID(data['scheduledtask']['object_id'])
                new_object.setDayofweek(data['scheduledtask']['day_of_week'])
                new_object.setDayofplace(data['scheduledtask']['day_place'])
                new_object.setObjectType(data['scheduledtask']['object_type'])
                # check if the object exist
                object_data = getobject(APP_ENGINE, new_object.object_type, new_object.object_id)
                if not object_data:
                    return jsonify({"status": 100, "message": "No " + new_object.object_type + " found with the given ID (" + new_object.object_id + ")."})
                new_object.setObjectName(object_data.name)
                new_object.setManagerID(user.ID)
            elif object_name == 'linkrcs':
                new_object = Linkrcs()
                new_object.setID(getnewid())
                new_object.setDistribution(data['linkrcs']['distribution'])
                new_object.setRelease(data['linkrcs']['release'])
                new_object.setChannels(data['linkrcs']['channels'])
                new_object.setArchitecture(data['linkrcs']['architecture'])
                new_object.setManagerID(user.ID)
                new_object.setCreationDate()

                 # check if the linkrcs already exist in the database
                if getlinkrcsbyinfo(APP_ENGINE, new_object.distribution, new_object.release, new_object.architecture):
                    return jsonify({"status": 102, "message": "Configuration for the system " + new_object.distribution + " " + new_object.release + " already exists in the database."})

        except InvalidValueException as error:
            APP_ENGINE.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})

        except KeyError as error:
            APP_ENGINE.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})

        # push the new object to the database
        new_object.insert(APP_ENGINE.database)

        # if scheduled we need to add the cronjob to the cron file
        if object_name == "scheduled":
            crontab = Crontab()
            if not crontab.generate_cron_file(APP_ENGINE.database):
                return jsonify({"status": 1, "message": "The scheduled task " + new_object.name + " has been added but YARUS can't add the cronjob to the cron file."})
            if not crontab.set_cron_file():
                return jsonify({"status": 1, "message": "The scheduled task " + new_object.name + " has been added but YARUS can't add the cronjob to the cron file."})
        
        # auto configuration client
        elif object_name == "client":
            # check if there is a corresponding configuration
            linkrcs = getlinkrcsbyinfo(APP_ENGINE, new_object.distribution, new_object.version, new_object.architecture)
            
            if not linkrcs:
                return jsonify({"status": 0, "message": "The " + object_name + " was successfully created but wasn't link with any channel (no configuration find)."})            

            channels = getlinkrcschannels(APP_ENGINE, linkrcs.channels.split(';'))
            
            if not channels:
                return jsonify({"status": 0, "message": "The " + object_name + " was successfully created but wasn't link with any channel (no channel in the configuration)."})

            linked_channels = ""
            for channel_info in channels:
                # create the bind
                new_bind = Bind(new_object.ID, channel_id=channel_info['ID'])
                # push the bind to the database
                new_bind.insert(APP_ENGINE.database)
                linked_channels += channel_info['name'] + ", "

            if not linked_channels:
                return jsonify({"status": 0, "message": "The " + object_name + " was successfully created but wasn't link with any channel."})
            return jsonify({"status": 0, "message": "The " + object_name + " was successfully created and is linked to the following channel: " + linked_channels})

        # new user
        elif object_name == 'user':
            msg = MIMEText("An administrator created an account on YARUS for you. You login information are the following: \n Username: " + new_object.name + "\n Password: " + password + "\n You can connect to YARUS from this address: https://" + request.remote_addr + "/")
            msg['Subject'] = "Your YARUS account information"
            adrs = "yarus@yarus.net"
            msg['From'] = adrs
            msg['To'] = new_object.mail

            s = smtplib.SMTP('localhost')
            s.sendmail(adrs, new_object.mail, msg.as_string())
            s.quit()
            
            return jsonify({"status": 0, "message": "The new user was successfully created. Password: " + password})

        return jsonify({"status": 0, "message": "The " + object_name + " was successfully created."})

    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/update/<string:object_name>/<string:object_id>', methods=['PUT'])
def update_object(object_name, object_id):
    """ update the object of the given type and given id """
    try:
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # check if the object exists
        object_inst = getobject(APP_ENGINE, object_name, object_id)
        if not object_inst:
            return jsonify({"status": 103, "message": "No " + object_name + " found."})

        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": message_json_error})

        # validate information and create the new object
        try:
            if object_name == 'repository':
                object_inst.setName(data['repository']['name'])
                object_inst.setDescription(data['repository']['description'])
                object_inst.setURL(data['repository']['URL'])
                object_inst.setType(data['repository']['type'])
                object_inst.setDistribution(data['repository']['distribution'].lower())
                object_inst.setRelease(data['repository']['release'].lower())
                object_inst.setArchitectures(data['repository']['architectures'])
                if object_inst.type == 'APT':
                    object_inst.setPath(data['repository']['path'])
                    object_inst.setComponents(data['repository']['components'])

                # check if we can reach the remote url
                try:
                    if APP_ENGINE.config.px_host != None and APP_ENGINE.config.px_port != None:
                        proxies = {
                            "http"  : str(APP_ENGINE.config.px_host) + ":" + str(APP_ENGINE.config.px_port)
                        }
                        if requests.get(new_object.URL, proxies=proxies).status_code != 200:
                            return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + new_object.URL + "."})
                    else:
                        if requests.get(new_object.URL).status_code != 200:
                            return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + new_object.URL + "."})

                except requests.ConnectionError as error:
                    return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + object_inst.URL + ". " + str(error)})
            elif object_name == 'channel':
                object_inst.setName(data['channel']['name'])
                object_inst.setDescription(data['channel']['description'])
                object_inst.setDistribution(data['channel']['distribution'].lower())
                object_inst.setRelease(data['channel']['release'].lower())
            elif object_name == 'client':
                object_inst.setIP(data['client']['IP'])
                object_inst.setName(data['client']['name'])
                object_inst.setDescription(data['client']['description'])
                object_inst.setVersion(data['client']['version'])
                object_inst.setDistribution(data['client']['distribution'])
                object_inst.setType(data['client']['type'])
            elif object_name == 'group':
                object_inst.setName(data['group']['name'])
                object_inst.setDescription(data['group']['description'])
            elif object_name == 'scheduled':
                object_inst.setName(data['scheduledtask']['name'])
                object_inst.setDescription(data['scheduledtask']['description'])
                object_inst.setHour(data['scheduledtask']['hour'])
                object_inst.setMinute(data['scheduledtask']['minute'])
                object_inst.setDayofmonth(data['scheduledtask']['day_of_month'])
                object_inst.setMonth(data['scheduledtask']['month'])
                object_inst.setDayofweek(data['scheduledtask']['day_of_week'])
                object_inst.setDayofplace(data['scheduledtask']['day_place'])
            elif object_name == 'user':
                object_inst.setName(data['nuser']['name'])
                object_inst.setMail(data['nuser']['mail'])
                object_inst.setRoleID(data['nuser']['role_id'])     

        except InvalidValueException as error:
            APP_ENGINE.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})

        except KeyError as error:
            APP_ENGINE.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})

        # update the new object to the database
        object_inst.update(APP_ENGINE.database)

        # if scheduled we need to add the cronjob to the cron file
        if object_name == 'scheduled':
            crontab = Crontab()
            if not crontab.generate_cron_file(APP_ENGINE.database):
                return jsonify({"status": 1, "message": "The scheduled task " + object_inst.name + " has been added but YARUS can't add the cronjob to the cron file."})
            if not crontab.set_cron_file():
                return jsonify({"status": 1, "message": "The scheduled task " + object_inst.name + " has been added but YARUS can't add the cronjob to the cron file."})

        return jsonify({"status": 0, "message": "The " + object_name + " " + object_inst.name + " was successfully updated."})

    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/delete/<string:object_name>', methods=['DELETE'])
def delete_object(object_name):
    """ delete the object of the given type and given id """
    try:
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": message_json_error})

        # check if exist in the database then delete
        try:
            for object_id in data['data']:
                object_inst = getobject(APP_ENGINE, object_name, object_id)
                if not object_inst:
                    continue
                if object_name == 'group' and object_id == '1':
                    continue
                elif object_name == 'user' and object_id == '1':
                    continue
                # delete the object
                object_inst.delete(APP_ENGINE.database)
                continue

            # if scheduled we need to add the cronjob to the cron file
            if object_name == 'scheduled':
                crontab = Crontab()
                crontab.generate_cron_file(APP_ENGINE.database)
                crontab.set_cron_file()

            return jsonify({"status": 0, "message": "Successfully deleted from the database."})

        except InvalidValueException as error:
            APP_ENGINE.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})

        except KeyError as error:
            APP_ENGINE.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})

    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/<string:object_name>/<string:object_id>/list/<string:info_list>', methods=['GET'])
def object_list(object_name, object_id, info_list):
    """ list all the object of a given type linked to the object """
    try:
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # get the list of the object and return it
        object_data = getobject(APP_ENGINE, object_name, object_id)
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_name + " found with the given ID (" + object_id + ")."})

        # get the list and return it
        if object_name == 'client':
            if info_list == 'tasks':
                data = APP_ENGINE.database.get_object_what('task', object_data.ID, object_name)
            elif info_list == 'rc':
                data = getbinds(APP_ENGINE, object_data.ID)
            elif info_list == 'upgradables':
                data = APP_ENGINE.database.get_upgradables(object_data.ID, object_name)
            elif info_list == 'scheduled':
                data =  APP_ENGINE.database.get_object_what('scheduled', object_data.ID, object_name)
            elif info_list == 'update':
                data = APP_ENGINE.database.get_object_what('update', object_data.ID, object_name)
            elif info_list == 'group':
                data = APP_ENGINE.database.get_client_group(object_data.ID)
                APP_ENGINE.log.log(data)
        elif object_name == 'update':
            if info_list == 'upgraded':
                data = APP_ENGINE.database.get_upgraded(object_id)
        elif object_name == 'group':
            if info_list == 'clients':
                data = APP_ENGINE.database.get_groupeds(object_data.ID)
            elif info_list == 'tasks':
                data = APP_ENGINE.database.get_object_what('task', object_data.ID, object_name)
            elif info_list == 'scheduled':
                data =  APP_ENGINE.database.get_object_what('scheduled', object_data.ID, object_name)
            elif info_list == 'upgradables':
                data = APP_ENGINE.database.get_upgradables(object_data.ID, object_name)
            elif info_list == 'update':
                data = APP_ENGINE.database.get_object_what('update', object_data.ID, object_name)
        elif object_name == 'channel':
            if info_list == 'repositories':
                data = APP_ENGINE.database.get_links(object_data.ID)
            elif info_list == 'tasks':
                data = APP_ENGINE.database.get_object_what('task', object_data.ID, object_name)
            elif info_list == 'scheduled':
                data =  APP_ENGINE.database.get_object_what('scheduled', object_data.ID, object_name)
        elif object_name == 'repository':
            if info_list == 'tasks':
                data = APP_ENGINE.database.get_object_what('task', object_data.ID, object_name)
            elif info_list == 'scheduled':
                data =  APP_ENGINE.database.get_object_what('scheduled', object_data.ID, object_name)
        elif object_name == 'linkrcs':
            if info_list == 'channels':
                linkrcs = getobject(APP_ENGINE, 'linkrcs', object_id)
                channels_id = []
                for chan_id in linkrcs.channels.split(";"):
                    if chan_id != "":
                        channels_id.append(chan_id)
                data = getlinkrcschannels(APP_ENGINE, channels_id)

        if data:
            return jsonify({"status": 0, "message": "", 'data': data})
        return jsonify({"status": -1, "message": "No " + info_list + " found for " + object_name + ".", 'data': data})

    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/link/<string:object_name>/<string:object_id>', methods=['POST'])
def link(object_name, object_id):
    """ link an object with an other """
    try:
        APP_ENGINE.database.connect()

        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": message_json_error})

        object_data = getobject(APP_ENGINE, object_name, object_id)
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_name + " found with the given ID (" + object_id + ")."})

        if object_name == 'client':
            message = ""
            for repochan in data['data']:
                otype, rc_id = repochan.split(':')

                if otype == 'r':

                    # check if the repository exist
                    repository = getobject(APP_ENGINE, 'repository', rc_id)
                    if not repository:
                        message += "No repository found with the given ID (" + rc_id + "). "
                        continue

                    # check if they are already linked
                    if getbind(APP_ENGINE, object_data.ID, repository.ID, ""):
                        message += "The repository " + repository.name + " is already linked to the client " + object_data.name + ". "
                        continue

                    # create the bind
                    new_bind = Bind(object_data.ID, repo_id=repository.ID)

                    # push the bind to the database
                    new_bind.insert(APP_ENGINE.database)

                    message += "The repository " + repository.name + " has been linked to the client " + object_data.name + ". "
                    continue

                elif otype == 'c':

                    # check if the channel exist
                    channel = getobject(APP_ENGINE, 'channel', rc_id)
                    if not channel:
                        message += "No channel found with the given ID (" + rc_id + "). "
                        continue

                    # check if they are already linked
                    if getbind(APP_ENGINE, object_data.ID, "", channel.ID):
                        message += "The channel " + channel.name + " is already linked to the client " + object_data.name + ". "
                        continue

                    # create the bind
                    new_bind = Bind(object_data.ID, channel_id=channel.ID)

                    # push the bind to the database
                    new_bind.insert(APP_ENGINE.database)

                    message += "The channel " + channel.name + " has been linked to the client " + object_data.name + ". "
                    continue

        elif object_name == 'group':
            for client_id in data['data']:
                # check if client exists
                client = getobject(APP_ENGINE, 'client', client_id)
                if not client:
                    continue

                # check if they are already binded
                if getgrouped(APP_ENGINE, object_data.ID, client.ID):
                    continue

                # create the bind
                new_grouped = Grouped(client.ID, object_data.ID)
                # push the bind to the database
                new_grouped.insert(APP_ENGINE.database)
                continue
            message = "Systems have been added to the group."

        elif object_name == 'channel':
            message = ""
            for channel_id in data['data']:
                # check if the repository exist
                repository = getobject(APP_ENGINE, 'repository', channel_id)
                if not repository:
                    message += "No repository found with the given ID (" + channel_id + "). "
                    continue                    # check if they are already linked
                if getlink(APP_ENGINE, object_data.ID, repository.ID):
                    message += "Repository " + repository.name + " is already in the channel " + object_data.name + ". "
                    continue

                # create the link
                new_link = Link(repository.ID, object_data.ID)

                # push the link to the database
                new_link.insert(APP_ENGINE.database)

                message += "The repository " + repository.name + " was successfully added to the channel " + object_data.name + ". "

        elif object_name == 'linkrcs':
            linked_channels = object_data.channels.split(";")
            for channel_id in data['data']:
                # check if channel exists
                channel = getobject(APP_ENGINE, 'channel', channel_id)
                if not channel:
                    continue

                 # check if they are already linked
                if channel.ID in linked_channels:
                    continue

                # create the link
                linked_channels.append(channel.ID)
                continue

            new_channels = ""
            for chan_id in linked_channels:
                new_channels += chan_id + ";"
            new_channels = new_channels[:-1]
            object_data.channels = new_channels
            object_data.update(APP_ENGINE.database)
            message = "Channels have been added to this configuration."

        return jsonify({"status": 0, "message": message})

    except DatabaseError as error:
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

    finally:
        APP_ENGINE.database.close()

@APP.route('/api/unlink/<string:object_name>/<string:object_id>', methods=['DELETE'])
def unlink(object_name, object_id):
    """ unlink an object with an other """
    try:
        APP_ENGINE.database.connect()

        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": message_json_error})

        object_data = getobject(APP_ENGINE, object_name, object_id)
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_name + " found with the given ID (" + object_id + ")."})

        if object_name == 'client':
            message = ""
            for repochan in data['data']:
                otype, rc_id = repochan.split(':')

                if otype == 'r':

                     # check if the repository exist
                    repository = getobject(APP_ENGINE, 'repository', rc_id)
                    if not repository:
                        message += "No repository found with the given ID (" + rc_id + "). "
                        continue

                    # check if they are already linked
                    olink = getbind(APP_ENGINE, object_data.ID, repository.ID, "")
                    if not olink:
                        message += "The repository " + repository.name + " isn't linked to the client " + object_data.name + ". "
                        continue

                    olink.delete_bind(APP_ENGINE.database)
                    message += "The repository " + repository.name + " has been removed from the client " + object_data.name + ". "
                    continue

                elif otype == 'c':

                   # check if the channel exist
                    channel = getobject(APP_ENGINE, 'channel', rc_id)
                    if not channel:
                        message += "No channel found with the given ID (" + rc_id + "). "
                        continue

                    # check if they are already linked
                    olink = getbind(APP_ENGINE, object_data.ID, "", channel.ID)
                    if not olink:
                        message += "The channel " + channel.name + " isn't linked to the client " + object_data.name + ". "
                        continue

                    olink.delete_bind(APP_ENGINE.database)
                    message += "The channel " + channel.name + " has been removed from the client " + object_data.name + ". "
                    continue

        elif object_name == 'group':
            message = ""
            for client_id in data['data']:

                # check if client exists
                client = getobject(APP_ENGINE, 'client', client_id)
                if not client:
                    message += "No client found with the given ID (" + client_id + "). "
                    continue

                # check if they are already linked
                olink = getgrouped(APP_ENGINE, object_data.ID, client.ID)
                if not olink:
                    message += "The client " + client.name + " isn't in the group " + object_data.name + "."
                    continue

                # delete the link
                olink.delete_grouped(APP_ENGINE.database)
                message += "The client " + client.name + " has been removed from the group " + object_data.name + "."
                continue

        elif object_name == 'channel':
            message = ""
            for repo_id in data['data']:

                # check if repo exists
                repository = getobject(APP_ENGINE, 'repository', repo_id)
                if not repository:
                    message += "No repository found with the given ID (" + repo_id + "). "
                    continue

                # check if the link exists
                olink = getlink(APP_ENGINE, object_data.ID, repository.ID)
                if not olink:
                    message += "Repository " + repository.name + " is already in the channel " + object_data.name + ". "
                    continue

                # delete the link
                olink.delete_link(APP_ENGINE.database)
                message += "The repository " + repository.name + " has been removed from the channel " + object_data.name + ". "
                continue

        elif object_name == 'linkrcs':
            linked_channels = object_data.channels.split(";")
            for channel_id in data['data']:

                # check if channel exists
                channel = getobject(APP_ENGINE, 'channel', channel_id)
                if not channel:
                    continue

                # check if they are already linked
                if channel.ID not in linked_channels:
                    continue

                # delete the link
                linked_channels.remove(channel.ID)
                continue
            
            new_channels = ""
            for chan_id in linked_channels:
                new_channels += chan_id + ";"
            new_channels = new_channels[:-1]
            object_data.channels = new_channels
            object_data.update(APP_ENGINE.database)
            message = "Channels have been removed from this configuration."

        return jsonify({"status": 0, "message": message})

    except DatabaseError as error:
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

    finally:
        APP_ENGINE.database.close()

@APP.route('/api/<string:object_type>/<string:object_id>/approve', methods=['PUT'])
def approveupgradable(object_type, object_id):
    """ approve packages to upgrade for the given client """
    try:
        APP_ENGINE.database.connect()

        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # get the object
        object_data = getobject(APP_ENGINE, object_type, object_id)
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_type + " found with the given ID (" + object_id + ")."})

        # extract the information about the approved packages
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": message_json_error})

        for upgradable_id in data['data']:
            upgradable = getupgradable(APP_ENGINE, upgradable_id)
            if not upgradable:
                continue
            upgradable.approved = 1
            upgradable.update(APP_ENGINE.database)
            continue

        return jsonify({"status": 0, "message": "Packages have been approved."})

    except DatabaseError as error:
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

    finally:
        APP_ENGINE.database.close()

@APP.route('/api/<string:object_type>/<string:object_id>/disapprove', methods=['PUT'])
def disapproveupgradable(object_type, object_id):
    """ disapprove packages to upgrade for the given client """
    try:
        APP_ENGINE.database.connect()

        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # get the object
        object_data = getobject(APP_ENGINE, object_type, object_id)
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_type + " found with the given ID (" + object_id + ")."})

        #extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": message_json_error})

        for upgradable_id in data['data']:
            upgradable = getupgradable(APP_ENGINE, upgradable_id)
            if not upgradable:
                continue
            upgradable.approved = 0
            upgradable.update(APP_ENGINE.database)
            continue

        return jsonify({"status": 0, "message": "Packages have been disapproved."})

    except DatabaseError as error:
        return jsonify({"status": 1, "message": message_database_error, "data": ""})
    finally:
        APP_ENGINE.database.close()

@APP.route('/api/register/<string:group_id>/<string:name>/<string:ip>/<string:distribution>/<string:release>/<string:architecture>/<string:ctype>', methods=['GET'])
def register(group_id, name, ip, distribution, release, architecture, ctype):
    try:
        # get the group
        group = getobject(APP_ENGINE, "group", group_id)
        if not group:
            return jsonify({"status": 103, "message": "No group found with the given ID (" + group_id + ")."})
        
        new_object = Client()
        new_object.setID(getnewid())
        new_object.setIP(ip)
        new_object.setName(name)
        new_object.setDescription("Name: " + name + ", distribution: " + distribution + ", version: " + release + ", architecture: " + architecture + ".")
        new_object.setVersion(release)
        new_object.setType(ctype)
        new_object.setDistribution(distribution)
        new_object.setArchitecture(architecture)
        new_object.setManagerID(group.manager_id)
        new_object.setCreationDate()

        # check if the client already exist in the database
        old_client = getclientbyip(APP_ENGINE, new_object.IP)
        if old_client:
            old_client.delete(APP_ENGINE.database)

        # push the new object to the database
        new_object.insert(APP_ENGINE.database)

        # add the client to the group
        # create the bind
        new_grouped = Grouped(new_object.ID, group.ID)
        # push the bind to the database
        new_grouped.insert(APP_ENGINE.database)

        # autolink
        # check if there is a corresponding configuration
        linkrcs = getlinkrcsbyinfo(APP_ENGINE, new_object.distribution, new_object.version, new_object.architecture)
        
        if not linkrcs:
            return jsonify({"status": 0, "message": "The " + name + " was successfully created but wasn't link with any channel (no configuration find)."})            

        channels = getlinkrcschannels(APP_ENGINE, linkrcs.channels.split(';'))
        
        if not channels:
            return jsonify({"status": 0, "message": "The " + name + " was successfully created but wasn't link with any channel (no channel in the configuration)."})

        linked_channels = ""
        for channel_info in channels:
            # create the bind
            new_bind = Bind(new_object.ID, channel_id=channel_info['ID'])
            # push the bind to the database
            new_bind.insert(APP_ENGINE.database)
            linked_channels += channel_info['name'] + ", "

        if not linked_channels:
            return jsonify({"status": 0, "message": "The " + name + " was successfully created but wasn't link with any channel."})
        return jsonify({"status": 0, "message": "The " + name + " was successfully created and is linked to the following channel: " + linked_channels})

    except InvalidValueException as error:
        APP_ENGINE.log.debug(str(error))
        return jsonify({"status": 100, "message": str(error)})
    
    except KeyError as error:
        APP_ENGINE.log.debug("Missing key: " + str(error))
        return jsonify({"status": 100, "message": "Missing key: " + str(error)})
    
    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/import/<string:object_type>/<string:object_id>/<string:update_id>', methods=['GET'])
def import_upgradable(object_type, object_id, update_id):    
    try:
        # get the object
        cg = getobject(APP_ENGINE, object_type, object_id)
        if not cg:
            return jsonify({"status": 103, "message": "No " + object_type + " found with the given ID (" + object_id + ")."})

        # get the update
        update = getobject(APP_ENGINE, 'update', update_id)
        if not update:
            return jsonify({"status": 103, "message": "No update with ID " + update_id + "."})

        updated_packages = APP_ENGINE.database.get_updated_package(update_id)

        for pkg in updated_packages:
            APP_ENGINE.database.approve_upgradable(cg.ID, object_type, pkg['package_id'])
            print(pkg['package_id'] + " approved")

        return jsonify({"status": 0, "message": "Approved packages have been imported."})

    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

@APP.route('/api/reset/<string:user_id>', methods=['GET'])
def reset_password(user_id):
    try:
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": message_session_error, "data": ""})

        # get the object and return its information
        object_user = getobject(APP_ENGINE, 'user', user_id)
        if not object_user:
            return jsonify({"status": 103, "message": "No user found with the given ID (" + user_id + ")."})

        password = getnewpassword()
        sha256_hash = hashlib.sha256()
        sha256_hash.update(password.encode('utf-8'))
        hashed_password = sha256_hash.hexdigest()
        object_user.password = hashed_password
        object_user.update(APP_ENGINE.database)

        return jsonify({"status": 0, "message": "The new password is: " + password})

    except DatabaseError as error:
        APP_ENGINE.log.log(error)
        return jsonify({"status": 1, "message": message_database_error, "data": ""})

# for development only
if __name__ == "__main__":
    APP.run(debug=True, host='0.0.0.0', port=6821)
