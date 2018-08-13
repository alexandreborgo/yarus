
import requests
from flask import Flask, json, jsonify, request

from yarus.engine.appengine import AppEngine
from yarus.engine.crontab import Crontab

from yarus.common.exceptions import *
from yarus.common.functions import *
from yarus.common.user import User

app = Flask("Yarus Engine")
app_engine = AppEngine(debug=True)

if not app_engine.start():
    print("Error while starting YarusEngine.")

# return json data from the request
def extract_data():
    try:
        data = json.loads(request.data)
    except ValueError as error:
        app_engine.log.debug(str(error))
        return None
    return data

# get information about the user who's doing the request
def getconnecteduser():
    try:
        data = extract_data()

        if not data:
            return False

        username = None
        password = None
        token = None
        # getting information about the user
        if 'user' in data:
            if 'username' in data['user']:
                if 'password' in data['user']:
                    username = data['user']['username']
                    password = data['user']['password']
                else:
                    return False
            elif 'token' in data['user']:
                token = data['user']['token']
            else:
                return False
        else:
            return False

        # creating the user
        tmp_user = User()
        try:
            if username and password:
                tmp_user.setName(username)
                tmp_user.setPassword(password)
            elif token:
                tmp_user.setToken(token)
        except InvalidValueException as error:
           return False
        except MissingValueException as error:
            return False

        # checkout user
        user = connectuser(app_engine, tmp_user)
        if not user:
            return False
        else:
            return user

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error."})

# login
@app.route('/api/login', methods=['GET'])
def login():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # user is valid so generate a new token for the session
        user.setToken(getnewid())
        user.update(app_engine.database)
        data = user.todata()
        return jsonify({"status": 0, "message": "", "data": data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# check login
@app.route('/api/login/check/<string:token>', methods=['GET'])
def checklogin(token):
    try:
        app_engine.database.connect()
        tmp_user = User()
        tmp_user.setToken(token)
        # checkout user
        user = connectuser(app_engine, tmp_user)
        if not user:
            return jsonify({"status": 1, "message": "Token expired."})
        else:
            return jsonify({"status": 0, "message": "Token is valid."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()


# return the list of all the object of the given type
@app.route('/api/list/<string:object_name>', methods=['GET'])
def list_object(object_name):
    try:
        app_engine.database.connect()
        
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})

        # get the list of the object and return it

        if object_name == 'repository':
            data = app_engine.database.get_all_object('yarus_repository')
        elif object_name == 'channel':
            data = app_engine.database.get_all_object('yarus_channel')
        elif object_name == 'client':
            data = app_engine.database.get_all_object('yarus_client')
        elif object_name == 'group':
            data = app_engine.database.get_all_object('yarus_group')
        elif object_name == 'task':
            data = app_engine.database.get_all_object('yarus_task')
        elif object_name == 'scheduled':
            data = app_engine.database.get_all_object('yarus_scheduled')            
        
        if len(data) > 0:
            return jsonify({"status": 0, "message": "", 'data': data})
        else:
            return jsonify({"status": -1, "message": "No " + object_name + " found.", 'data': data})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})

    finally:
        app_engine.database.close()

# return the information of the object of the given type with the given id
@app.route('/api/see/<string:object_name>/<string:object_id>', methods=['GET'])
def see_object(object_name, object_id):
    try:
        app_engine.database.connect()
        
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})

        # get the object and return its information

        object_data = getobject(app_engine, object_name, object_id)        
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_name + " found with the given ID (" + object_id + ")."})

        # if it's a user we don't send the password hash
        if object_name == 'user':
            object_data.password = ""
        
        data = object_data.todata()

        return jsonify({"status": 0, "message": "", 'data': data})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})

    finally:
        app_engine.database.close()

# create an object of the given type
@app.route('/api/create/<string:object_name>', methods=['POST'])
def create_object(object_name):
    try:
        app_engine.database.connect()
        
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})

        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})

        # validate information and create the new object
        try:
            if object_name == 'repository':
                new_object = Repository()
                new_object.setID(getnewid())
                new_object.setName(data['repository']['name'])
                new_object.setURL(data['repository']['URL'])
                new_object.setDescription(data['repository']['description'])
                new_object.setType(data['repository']['type'])
                new_object.setRelease(data['repository']['release'])
                if new_object.type == 'APT':
                    new_object.setPath(data['repository']['path'])
                new_object.setDistribution(data['repository']['distribution'])
                new_object.setComponents(data['repository']['components'])
                new_object.setArchitectures(data['repository']['architectures'])
                new_object.setManagerID(user.ID)
                new_object.setCreationDate()

                # check if the repository already exist in the database
                if getrepobyname(app_engine, new_object.name):
                    return jsonify({"status": 102, "message": "Repository with the name " + new_object.name + " already exists in the database."})

                # check if we can reach the remote url
                try:
                    if app_engine.config.px_host != "":
                        proxies = {
                            "http"  : app_engine.config.px_host + ":" + str(app_engine.config.px_port)
                        }
                    else:
                        proxies = None

                    if requests.get(new_object.URL, proxies=proxies).status_code != 200:
                        return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + new_object.URL + "."})
                        
                except Exception as exception:
                    return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + new_object.URL + "."})

            elif object_name == 'channel':
                new_object = Channel()
                new_object.setID(getnewid())
                new_object.setName(data['channel']['name'])
                new_object.setDescription(data['channel']['description'])
                new_object.setManagerID(user.ID)
                new_object.setCreationDate()

                 # check if the channel already exist in the database
                if getchannelbyname(app_engine, new_object.name):
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
                new_object.setManagerID(user.ID)
                new_object.setCreationDate()
                # check if the client already exist in the database
                if getclientbyip(app_engine, new_object.IP):
                    return jsonify({"status": 102, "message": "Client with the IP " + new_object.IP + " already exists in the database."})

            elif object_name == 'group':
                new_object = Group()
                new_object.setID(getnewid())
                new_object.setName(data['group']['name'])
                new_object.setDescription(data['group']['description'])
                new_object.setManagerID(user.ID)
                new_object.setCreationDate()
                # check if the repository already exist in the database
                if getgroupbyname(app_engine, new_object.name):
                    return jsonify({"status": 102, "message": "Group with the name " + new_object.name + " already exists in the database."})
            
            elif object_name == 'task':
                new_object = Task()
                new_object.setID(getnewid())
                new_object.setStatus('pending')
                new_object.setCreationDate()
                new_object.setAction(data['task']['action'])
                new_object.setObjectID(data['task']['object_id'])
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
                new_object.setAction(data['scheduledtask']['task_action'])
                new_object.setObjectID(data['scheduledtask']['object_id'])
                new_object.setDayofweek(data['scheduledtask']['day_of_week'])
                new_object.setDayofplace(data['scheduledtask']['day_place'])
                new_object.setManagerID(user.ID)

        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})

        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})

        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})

        # push the new object to the database
        new_object.insert(app_engine.database)
        
        # if scheduled we need to add the cronjob to the cron file
        if object_name == 'scheduled':
            crontab = Crontab()
            if not crontab.generate_cron_file(app_engine.database):
                return jsonify({"status": 1, "message": "The scheduled task " + new_object.name + " has been added but YARUS can't add the cronjob to the cron file."})
            if not crontab.set_cron_file():
                return jsonify({"status": 1, "message": "The scheduled task " + new_object.name + " has been added but YARUS can't add the cronjob to the cron file."})

        
        return jsonify({"status": 0, "message": "The " + object_name + " was successfully created."})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})

    finally:
        app_engine.database.close()

# update the object of the given type and given id
@app.route('/api/update/<string:object_name>/<string:object_id>', methods=['PUT'])
def update_object(object_name, object_id):
    try:
        app_engine.database.connect()
        
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})

        # check if the object exists
        object_inst = getobject(app_engine, object_name, object_id)
        if not object_inst:
            return jsonify({"status": 103, "message": "No " + object_name + " found."})
        
        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})

        # validate information and create the new object
        try:
            if object_name == 'repository':
                
                object_inst.setName(data['repository']['name'])
                object_inst.setURL(data['repository']['URL'])
                object_inst.setDescription(data['repository']['description'])
                object_inst.setType(data['repository']['type'])
                object_inst.setRelease(data['repository']['release'])
                if object_inst.type == 'APT':
                    object_inst.setPath(data['repository']['path'])
                object_inst.setDistribution(data['repository']['distribution'])
                object_inst.setComponents(data['repository']['components'])
                object_inst.setArchitectures(data['repository']['architectures'])
                
                # check if we can reach the remote url
                try:
                    if app_engine.config.px_host != "":
                        proxies = {
                            "http"  : app_engine.config.px_host + ":" + str(app_engine.config.px_port)
                        }
                    else:
                        proxies = None

                    if requests.get(object_inst.URL, proxies=proxies).status_code != 200:
                        return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + object_inst.URL + "."})
                        
                except Exception as exception:
                    return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + object_inst.URL + "."})

            elif object_name == 'channel':
                object_inst.setName(data['channel']['name'])
                object_inst.setDescription(data['channel']['description'])

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

        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})

        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})

        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})

        # update the new object to the database
        object_inst.update(app_engine.database)
        
        # if scheduled we need to add the cronjob to the cron file
        if object_name == 'scheduled':
            crontab = Crontab()
            if not crontab.generate_cron_file(app_engine.database):
                return jsonify({"status": 1, "message": "The scheduled task " + object_inst.name + " has been added but YARUS can't add the cronjob to the cron file."})
            if not crontab.set_cron_file():
                return jsonify({"status": 1, "message": "The scheduled task " + object_inst.name + " has been added but YARUS can't add the cronjob to the cron file."})

        return jsonify({"status": 0, "message": "The " + object_name + " " + object_inst.name + " was successfully updated."})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})

    finally:
        app_engine.database.close()

# delete the object of the given type and given id
@app.route('/api/delete/<string:object_name>', methods=['DELETE'])
def delete_object(object_name):
    try:
        app_engine.database.connect()
        
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})

        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})

        # check if exist in the database then delete
        try:
            for object_id in data['data']:
                object_inst = getobject(app_engine, object_name, object_id)
                if not object_inst:
                    continue
                # delete the object
                object_inst.delete(app_engine.database)
                continue

            # if scheduled we need to add the cronjob to the cron file
            if object_name == 'scheduled':
                print("toto")
                crontab = Crontab()
                crontab.generate_cron_file(app_engine.database)
                crontab.set_cron_file()
                      
            return jsonify({"status": 0, "message": "Successfully deleted from the database."})

        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})

        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})

        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})

    finally:
        app_engine.database.close()

# list all the object of a given type linked to the object
@app.route('/api/<string:object_name>/<string:object_id>/list/<string:info_list>', methods=['GET'])
def object_list(object_name, object_id, info_list):
    try:
        app_engine.database.connect()
        
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})

        # get the list of the object and return it
        object_data = getobject(app_engine, object_name, object_id)        
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_name + " found with the given ID (" + object_id + ")."})

        # get the list and return it
        if object_name == 'client':
            if info_list == 'tasks':                
                data = getobjecttasks(app_engine, object_data.ID)
            elif info_list == 'rc':
                data = getbinds(app_engine, object_data.ID)
            elif info_list == 'upgradables':
                data = getupgradables(app_engine, object_data.ID)
            elif info_list == 'scheduled':
                data = getobjectscheduled(app_engine, object_data.ID)
        elif object_name == 'group':
            if info_list == 'clients':
                data = app_engine.database.get_groupeds(object_data.ID)
            elif info_list == 'tasks':                
                data = getobjecttasks(app_engine, object_data.ID)
            elif info_list == 'scheduled':
                data = getobjectscheduled(app_engine, object_data.ID)
        elif object_name == 'channel':
            if info_list == 'repositories':
                data = app_engine.database.get_links(object_data.ID)
            elif info_list == 'tasks':                
                data = getobjecttasks(app_engine, object_data.ID)
            elif info_list == 'scheduled':
                data = getobjectscheduled(app_engine, object_data.ID)
        elif object_name == 'repository':
            if info_list == 'tasks':
                data = getobjecttasks(app_engine, object_data.ID)
            elif info_list == 'scheduled':
                data = getobjectscheduled(app_engine, object_data.ID)

        if len(data) > 0:
            return jsonify({"status": 0, "message": "", 'data': data})
        else:
            return jsonify({"status": -1, "message": "No " + info_list + " found for " + object_name + ".", 'data': data})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})

    finally:
        app_engine.database.close()

# link an object with an other
@app.route('/api/link/<string:object_name>/<string:object_id>', methods=['POST'])
def link(object_name, object_id):
    try:
        app_engine.database.connect()

        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})
        
        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})

        object_data = getobject(app_engine, object_name, object_id)        
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_name + " found with the given ID (" + object_id + ")."})

        if object_name == 'client':
            message = ""
            for rc in data['data']:
                otype, ID = rc.split(':')

                if otype == 'r':
                    
                    # check if the repository exist
                    repository = getobject(app_engine, 'repository', ID)        
                    if not repository:
                        message += "No repository found with the given ID (" + ID + "). "                    
                        continue

                    # check if they are already linked
                    if getbind(app_engine, object_data.ID, repository.ID, ""):
                        message += "The repository " + repository.name + " is already linked to the client " + object_data.name + ". "
                        continue

                    # create the bind
                    new_bind = Bind(object_data.ID, repo_id=repository.ID)

                    # push the bind to the database
                    new_bind.insert(app_engine.database)

                    message += "The repository " + repository.name + " has been linked to the client " + object_data.name + ". "
                    continue

                elif otype == 'c':

                    # check if the channel exist
                    channel = getobject(app_engine, 'channel', ID)        
                    if not channel:
                        message += "No channel found with the given ID (" + ID + "). "                    
                        continue

                    # check if they are already linked
                    if getbind(app_engine, object_data.ID, "", channel.ID):
                        message += "The channel " + channel.name + " is already linked to the client " + object_data.name + ". "
                        continue

                    # create the bind
                    new_bind = Bind(object_data.ID, channel_id=channel.ID)

                    # push the bind to the database
                    new_bind.insert(app_engine.database)

                    message += "The channel " + channel.name + " has been linked to the client " + object_data.name + ". "
                    continue

        elif object_name == 'group':
            message = ""
            for client_id in data['data']:
                # check if client exists
                client = getobject(app_engine, 'client', client_id)        
                if not client:
                    message += "No client found with the given ID (" + client_id + "). "
                    continue

                # check if they are already binded
                if getgrouped(app_engine, object_data.ID, client.ID):
                    message += "The client " + client.name + " is already in the group " + object_data.name + "."
                    continue

                # create the bind
                new_grouped = Grouped(client.ID, object_data.ID)
                # push the bind to the database
                new_grouped.insert(app_engine.database)
                message += "The client " + client.name + " has been added to the group " + object_data.name + "."
                continue

        elif object_name == 'channel':
            message = ""
            for channel_id in data['data']:
                # check if the repository exist
                repository = getobject(app_engine, 'repository', channel_id)        
                if not repository:
                    message += "No repository found with the given ID (" + channel_id + "). "                    
                    continue            
                        
                # check if they are already linked
                if getlink(app_engine, object_data.ID, repository.ID):
                    message += "Repository " + repository.name + " is already in the channel " + object_data.name + ". "
                    continue
            
                # create the link
                new_link = Link(repository.ID, object_data.ID)

                # push the link to the database
                new_link.insert(app_engine.database)

                message += "The repository " + repository.name + " was successfully added to the channel " + object_data.name + ". "

        return jsonify({"status": 0, "message": message})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})

    finally:
        app_engine.database.close()

# unlink an object with an other
@app.route('/api/unlink/<string:object_name>/<string:object_id>', methods=['DELETE'])
def unlink(object_name, object_id):
    try:
        app_engine.database.connect()

        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})
        
        # extract the information about the object
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})

        object_data = getobject(app_engine, object_name, object_id)        
        if not object_data:
            return jsonify({"status": 103, "message": "No " + object_name + " found with the given ID (" + object_id + ")."})

        if object_name == 'client':
            message = ""
            for rc in data['data']:
                otype, ID = rc.split(':')

                if otype == 'r':

                     # check if the repository exist
                    repository = getobject(app_engine, 'repository', ID)        
                    if not repository:
                        message += "No repository found with the given ID (" + ID + "). "                    
                        continue

                    # check if they are already linked
                    link = getbind(app_engine, object_data.ID, repository.ID, "")
                    if not link:
                        message += "The repository " + repository.name + " isn't linked to the client " + object_data.name + ". "
                        continue

                    link.delete_bind(app_engine.database)
                    message += "The repository " + repository.name + " has been removed from the client " + object_data.name + ". "
                    continue

                elif otype == 'c':

                   # check if the channel exist
                    channel = getobject(app_engine, 'channel', ID)        
                    if not channel:
                        message += "No channel found with the given ID (" + ID + "). "                    
                        continue

                    # check if they are already linked
                    link = getbind(app_engine, object_data.ID, "", channel.ID)
                    if not link:
                        message += "The channel " + channel.name + " isn't linked to the client " + object_data.name + ". "
                        continue

                    link.delete_bind(app_engine.database)
                    message += "The channel " + channel.name + " has been removed from the client " + object_data.name + ". "
                    continue

        elif object_name == 'group':
            message = ""
            for client_id in data['data']:
                
                # check if client exists
                client = getobject(app_engine, 'client', client_id)        
                if not client:
                    message += "No client found with the given ID (" + client_id + "). "
                    continue
                
                # check if they are already linked
                link = getgrouped(app_engine, object_data.ID, client.ID)
                if not link:
                    message += "The client " + client.name + " isn't in the group " + object_data.name + "."
                    continue
                
                # delete the link
                link.delete_grouped(app_engine.database)
                message += "The client " + client.name + " has been removed from the group " + object_data.name + "."
                continue

        elif object_name == 'channel':
            message = ""
            for repo_id in data['data']:
                
                # check if repo exists
                repository = getobject(app_engine, 'repository', repo_id)        
                if not repository:
                    message += "No repository found with the given ID (" + repo_id + "). "
                    continue
                
                # check if the link exists
                link = getlink(app_engine, object_data.ID, repository.ID)
                if not link:
                    message += "Repository " + repository.name + " is already in the channel " + object_data.name + ". "
                    continue
                
                # delete the link
                link.delete_link(app_engine.database)
                message += "The repository " + repository.name + " has been removed from the channel " + object_data.name + ". "
                continue

        return jsonify({"status": 0, "message": message})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})

    finally:
        app_engine.database.close()

# approve packages to upgrade for the given client
@app.route('/api/client/<string:client_id>/approve', methods=['PUT'])
def approveupgradable(client_id):
    try:
        app_engine.database.connect()
        
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})
        
        # check if client exists
        client = getobject(app_engine, 'client', client_id)        
        if not client:
            return jsonify({"status": 103, "message": "No client found with the given ID (" + client_id + ")."})

        # extract the information about the approved packages
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        
        message = ""
        for package_id in data['data']:
            upgradable = getupgradable(app_engine, client.ID, package_id)
            if not upgradable:
                message += "The package " + upgradable.name + " doesn't exist in the list of upgradable packages of " + client.name + ". "
                continue            
            upgradable.approved = 1
            upgradable.update(app_engine.database)
            message += "The package " + upgradable.name + " is approved for update."
            continue
        
        return jsonify({"status": 0, "message": message})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})

    finally:
        app_engine.database.close()

# disapprove packages to upgrade for the given client
@app.route('/api/client/<string:client_id>/disapprove', methods=['PUT'])
def disapproveupgradable(client_id):
    try:
        app_engine.database.connect()
        
        user = getconnecteduser()
        if not user:
            return jsonify({"status": 1, "message": "No active session", "data": ""})
        
        # check if client exists
        client = getobject(app_engine, 'client', client_id)        
        if not client:
            return jsonify({"status": 103, "message": "No client found with the given ID (" + client_id + ")."})

        #extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        
        message = ""
        for package_id in data['data']:
            upgradable = getupgradable(app_engine, client_id, package_id)
            if not upgradable:
                message += "The package " + upgradable.name + " doesn't exist in the list of upgradable packages of " + client.name + ". "
                continue            
            upgradable.approved = 0
            upgradable.update(app_engine.database)
            message += "The package " + upgradable.name + " is approved for update."
            continue
        
        return jsonify({"status": 0, "message": message})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=6821)
