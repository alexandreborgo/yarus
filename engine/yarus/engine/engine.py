
from flask import Flask, json, jsonify, request
from yarus.engine.appengine import AppEngine
from yarus.engine.crontab import Crontab
from yarus.common.exceptions import *
from yarus.common.functions import *
from yarus.common.user import User
import requests

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
            return jsonify({"status": 101, "message": "The content must be JSON format."})

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
                    return jsonify({"status": 100, "message": "Missing user's password."})
            elif 'token' in data['user']:
                token = data['user']['token']
            else:
                return jsonify({"status": 101, "message": "Missing username/password and token."})
        else:
            return jsonify({"status": 101, "message": "Missing username/password and token."})

        # creating the user
        tmp_user = User()
        try:
            if username and password:
                tmp_user.setName(username)
                tmp_user.setPassword(password)
            elif token:
                tmp_user.setToken(token)
        except InvalidValueException as error:
            return jsonify({"status": 102, "message": "Invalid username/password or token."})
        except MissingValueException as error:
            return jsonify({"status": 101, "message": "Missing username/password or token."})

        # checkout user
        user = connectuser(app_engine, tmp_user)
        if not user:
            return jsonify({"status": 102, "message": "No user found correponding to the given information."})
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


"""
    The following functions deal with repositories.
"""
@app.route('/api/repositories', methods=['GET'])
def list_repository():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_all_object('yarus_repository')
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

@app.route('/api/repository/<string:repo_id>', methods=['GET'])
def see_repository(repo_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the repository and return the data
        repo = getrepo(app_engine, repo_id)
        if not repo:
            return jsonify({"status": 103, "message": "No repository found."})
        data = repo.todata()
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

@app.route('/api/repository', methods=['POST'])
def create_repository():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # create a new repository
        new_repo = Repository()
        # extract information from received data about the new repository
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        # validate new data
        try:
            new_repo.setID(getnewid())
            new_repo.setName(data['repository']['name'])
            new_repo.setURL(data['repository']['URL'])
            new_repo.setDescription(data['repository']['description'])
            new_repo.setType(data['repository']['type'])
            new_repo.setRelease(data['repository']['release'])
            if new_repo.type == 'APT':
                new_repo.setPath(data['repository']['path'])
            new_repo.setRepository(data['repository']['repository'])
            new_repo.setComponents(data['repository']['components'])
            new_repo.setArchitectures(data['repository']['architectures'])
            new_repo.setManagerID(user.ID)
            new_repo.setCreationDate()
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        
        # check if the repository already exist in the database
        if getrepobyname(app_engine, new_repo.name):
            return jsonify({"status": 102, "message": "Repository with the name " + new_repo.name + " already exists in the database."})
        
        # check if we can reach the remote url
        try:
            if app_engine.config.px_host != "":
                proxies = {
                    "http"  : app_engine.config.px_host + ":" + str(app_engine.config.px_port)
                }
                print(app_engine.config.px_host + ":" + str(app_engine.config.px_port))
            else:
                proxies = None

            if requests.get(new_repo.URL, proxies=proxies).status_code != 200:
                return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + new_repo.URL + "."})
                
        except Exception as exception:
            print(exception)
            return jsonify({"status": 1, "message": "YARSU can't connect to the remote URL " + new_repo.URL + "."})

        # push the new repository to the database
        new_repo.insert(app_engine.database)
        return jsonify({"status": 0, "message": "The repository " + new_repo.name + " was successfully created."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

@app.route('/api/repository/<string:repo_id>', methods=['PUT'])
def update_repository(repo_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # check if the repository exists
        repo = getrepo(app_engine, repo_id)
        if not repo:
            return jsonify({"status": 103, "message": "No repository found."})
        # extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 1, "message": "The content must be JSON format."})
        # validate data
        try:
            repo.setName(data['repository']['name'])
            repo.setURL(data['repository']['URL'])
            repo.setDescription(data['repository']['description'])
            repo.setType(data['repository']['type'])
            repo.setRelease(data['repository']['release'])
            if repo.type == 'APT':
                repo.setPath(data['repository']['path'])
            repo.setRepository(data['repository']['repository'])
            repo.setComponents(data['repository']['components'])
            repo.setArchitectures(data['repository']['architectures'])
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        # update the database
        repo.update(app_engine.database)
        return jsonify({"status": 0, "message": "The repository was successfully updated."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# delete one or more repository
@app.route('/api/repositories', methods=['DELETE'])
def delete_repositories():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list of repositories to delete
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        
        try:
            for repo_id in data['data']:
                repo = getrepo(app_engine, repo_id)
                if not repo:
                    continue
                # delete the repo
                repo.delete(app_engine.database)
                continue
            return jsonify({"status": 0, "message": "The repositories were successfully deleted from the database."})
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

# get information about user (note: all information except password are returned)
@app.route('/api/user/<string:user_id>', methods=['GET'])
def see_user(user_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the repository and return the data
        user2 = getuser(app_engine, user_id)
        if not user2:
            return jsonify({"status": 103, "message": "No user found."})
        user2.password = ""
        data = user2.todata()
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

"""
    The following functions deal with channels.
"""
@app.route('/api/channels', methods=['GET'])
def list_channel():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_all_object('yarus_channel')
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/channel/<string:channel_id>', methods=['GET'])
def see_channel(channel_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the channel and return the data
        channel = getchannel(app_engine, channel_id)
        if not channel:
            return jsonify({"status": 103, "message": "No channel found."})
        data = channel.todata()
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/channel', methods=['POST'])
def create_channel():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # create a new repository
        channel = Channel()
        # extract information from received data about the new repository
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        # validate new data
        try:
            channel.setID(getnewid())
            channel.setName(data['channel']['name'])
            channel.setDescription(data['channel']['description'])
            channel.setManagerID(user.ID)
            channel.setCreationDate()
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        # check if the repository already exist in the database
        if getchannelbyname(app_engine, channel.name):
            return jsonify({"status": 102, "message": "Channel with the name " + channel.name + " already exists in the database."})
        # push the new repository to the database
        channel.insert(app_engine.database)
        return jsonify({"status": 0, "message": "The channel " + channel.name + " was successfully created."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/channel/<string:channel_id>', methods=['PUT'])
def update_channel(channel_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # check if the repository exists
        channel = getchannel(app_engine, channel_id)
        if not channel:
            return jsonify({"status": 103, "message": "No channel found."})
        # extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 1, "message": "The content must be JSON format."})
        # validate datarepository
        try:
            channel.setName(data['channel']['name'])
            channel.setDescription(data['channel']['description'])
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        # update the database
        channel.update(app_engine.database)
        return jsonify({"status": 0, "message": "The channel was successfully updated."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/channel/<string:channel_id>', methods=['DELETE'])
def delete_channel(channel_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # check if the channel exists
        channel = getchannel(app_engine, channel_id)
        if not channel:
            return jsonify({"status": 103, "message": "The channel doesn't exist in the database."})
        # delete the channel
        channel.delete(app_engine.database)
        return jsonify({"status": 0, "message": "The channel was successfully deleted."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

"""
    The following functions deal with links between channels and repositories.
"""
@app.route('/api/channel/<string:channel_id>/repositories', methods=['GET'])
def channel_repositories(channel_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_links(channel_id)
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/channel/<string:channel_id>/repository/<string:repo_id>', methods=['POST'])
def channel_add_repository(channel_id, repo_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # check if repository and channel exists
        repo = getrepo(app_engine, repo_id)
        if not repo:
            return jsonify({"status": 103, "message": "No repository found."})
        channel = getchannel(app_engine, channel_id)
        if not channel:
            return jsonify({"status": 103, "message": "No channel found."})
        # check if they are already linked
        if getlink(app_engine, channel_id, repo_id):
            return jsonify({"status": 102, "message": "Repository " + repo.name + " is already in the channel " + channel.name})
        # create the link
        new_link = Link(repo.ID, channel.ID)
        # push the link to the database
        new_link.insert(app_engine.database)
        return jsonify({"status": 0, "message": "The repository " + repo.name + " was successfully added to the channel " + channel.name + "."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/channel/<string:channel_id>/repository/<string:repo_id>', methods=['DELETE'])
def channel_delete_repository(channel_id, repo_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # check if the channel exists
        link = getlink(app_engine, channel_id, repo_id)
        if not link:
            return jsonify({"status": 103, "message": "The link doesn't exist in the database."})
        # delete the channel
        link.delete_link(app_engine.database)
        return jsonify({"status": 0, "message": "The link was successfully deleted."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

"""
    CLIENTS
"""

# list all clients in the database
@app.route('/api/clients', methods=['GET'])
def list_client():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_all_object('yarus_client')
        if len(data) > 0:
            return jsonify({"status": 0, "message": "", 'data': data})
        else:
            return jsonify({"status": -1, "message": "No system found.", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# return information about the given client
@app.route('/api/client/<string:client_id>', methods=['GET'])
def see_client(client_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the channel and return the data
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})
        data = client.todata()
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# create a new client
@app.route('/api/client', methods=['POST'])
def create_client():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # create a new repository
        client = Client()
        # extract information from received data about the new repository
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        # validate new data
        try:
            client.setID(getnewid())
            client.setIP(data['client']['IP'])
            client.setName(data['client']['name'])
            client.setDescription(data['client']['description'])
            client.setVersion(data['client']['version'])
            client.setType(data['client']['type'])
            client.setDistribution(data['client']['distribution'])
            client.setManagerID(user.ID)
            client.setCreationDate()
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        # check if the repository already exist in the database
        if getclientbyip(app_engine, client.IP):
            return jsonify({"status": 102, "message": "Client with the IP " + client.IP + " already exists in the database."})
        # push the new repository to the database
        client.insert(app_engine.database)

        repositories = getcorrespondingrepositories(app_engine, client.distribution, client.version)
        if not repositories:            
            return jsonify({"status": 0, "message": "The client " + client.name + " was successfully created but no corresponding repositories were found in the database."})

        for repository in repositories:
            # create the bind
            new_bind = Bind(client.ID, repo_id=repository['ID'])
            # push the bind to the database
            new_bind.insert(app_engine.database)

        return jsonify({"status": 0, "message": "The client " + client.name + " was successfully created. And was linked to corresponding repositories."})
        
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# update the information of the given client
@app.route('/api/client/<string:client_id>', methods=['PUT'])
def update_client(client_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # check if the repository exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})
        # extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 1, "message": "The content must be JSON format."})
        # validate datarepository
        try:
            client.setIP(data['client']['IP'])
            client.setName(data['client']['name'])
            client.setDescription(data['client']['description'])
            client.setVersion(data['client']['version'])
            client.setDistribution(data['client']['distribution'])
            client.setType(data['client']['type'])
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        # update the database
        client.update(app_engine.database)
        return jsonify({"status": 0, "message": "The client was successfully updated."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# remove the given clients from the database
@app.route('/api/clients/', methods=['DELETE'])
def delete_clients():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        
        try:
            for client_id in data['data']:
                client = getclient(app_engine, client_id)
                if not client:
                    continue
                # delete the client
                client.delete(app_engine.database)
                continue
            return jsonify({"status": 0, "message": "The client where successfully deleted from the database."})
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

# return the list of linked channels and repositories to the given client
@app.route('/api/client/<string:client_id>/rc', methods=['GET'])
def client_rc(client_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = getbinds(app_engine, client_id)
        print(data)
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# return the list of task in the database about the given client
@app.route('/api/client/<string:client_id>/tasks', methods=['GET'])
def client_tasks(client_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
       
        # check if client exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})
       
        # get the list and return it
        data = getclienttasks(app_engine, client.ID)
        if len(data) > 0:
            return jsonify({"status": 0, "message": "", 'data': data})
        else:
            return jsonify({"status": -1, "message": "No tasks found linked to the client " + client.name + ".", 'data': data})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# link a channel/repository to a client
@app.route('/api/client/<string:client_id>/link/', methods=['POST'])
def client_add(client_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # check if client exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})
        
        #extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})

        message = ""
        for rc in data['data']:
            otype, ID = rc.split(':')

            if otype == 'r':

                repo = getrepo(app_engine, ID)
                if not repo:
                    message += "No repository found. "
                    continue

                # check if they are already binded
                if getbind(app_engine, client_id, repo.ID, ""):
                    message += "The repository " + repo.name + " is already linked to the client " + client.name + ". "
                    continue

                # create the bind
                new_bind = Bind(client.ID, repo_id=repo.ID)
                # push the bind to the database
                new_bind.insert(app_engine.database)
                message += "The repository " + repo.name + " has been binded to the client " + client.name + ". "
                continue

            elif otype == 'c':

                chan = getchannel(app_engine, ID)
                if not chan:
                    message += "No channel found. "
                    continue

                # check if they are already binded
                if getbind(app_engine, client_id, "", chan.ID):
                    message += "The channel " + chan.name + " is already linked to the client " + client.name + ". "
                    continue

                # create the bind
                new_bind = Bind(client.ID, channel_id=chan.ID)
                # push the bind to the database
                new_bind.insert(app_engine.database)
                message += "The channel " + chan.name + " has been binded to the client " + client.name + ". "
                continue

        return jsonify({"status": 0, "message": message})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# unlink a channel/repository to a client
@app.route('/api/client/<string:client_id>/unlink/', methods=['DELETE'])
def client_remove(client_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # check if client exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})
        
        #extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})

        message = ""
        for rc in data['data']:
            otype, ID = rc.split(':')

            if otype == 'r':

                repo = getrepo(app_engine, ID)
                if not repo:
                    message += "No repository found. "
                    continue

                # check if they are already binded
                bind = getbind(app_engine, client_id, repo.ID, "")
                if not bind:
                    message += "The repository " + repo.name + " isn't linked to the client " + client.name + ". "
                    continue

                bind.delete_bind(app_engine.database)
                message += "The repository " + repo.name + " has been removed from the client " + client.name + ". "
                continue

            elif otype == 'c':

                chan = getchannel(app_engine, ID)
                if not chan:
                    message += "No channel found. "
                    continue

                # check if they are already binded
                bind = getbind(app_engine, client_id, "", chan.ID)
                if not bind:
                    message += "The channel " + chan.name + " isn't linked to the client " + client.name + ". "
                    continue

                bind.delete_bind(app_engine.database)
                message += "The channel " + chan.name + " has been removed from the client " + client.name + ". "
                continue

        return jsonify({"status": 0, "message": message})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# return the list of upgradables packages for the given client
@app.route('/api/client/<string:client_id>/upgradable/', methods=['GET'])
def seeupgradable(client_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        
        # check if client exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})
        
        # get the list and return it
        data = getupgradables(app_engine, client_id)
        return jsonify({"status": 0, "message": "", 'data': data})
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
        if type(user) != User:
            return user
        
        # check if client exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})

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
        if type(user) != User:
            return user
        
        # check if client exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})

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


"""
The following functions deal with group of clients.
"""
@app.route('/api/groups', methods=['GET'])
def list_groups():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_all_object('yarus_group')
        if len(data) > 0:
            return jsonify({"status": 0, "message": "", 'data': data})
        else:
            return jsonify({"status": -1, "message": "No group found.", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/group/<string:group_id>', methods=['GET'])
def see_group(group_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the group and return the data
        group = getgroup(app_engine, group_id)
        if not group:
            return jsonify({"status": 103, "message": "No group found."})
        data = group.todata()
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/group', methods=['POST'])
def create_group():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # create a new repository
        group = Group()
        # extract information from received data about the new repository
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        # validate new data
        try:
            group.setID(getnewid())
            group.setName(data['group']['name'])
            group.setDescription(data['group']['description'])
            group.setManagerID(user.ID)
            group.setCreationDate()
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        # check if the repository already exist in the database
        if getgroupbyname(app_engine, group.name):
            return jsonify({"status": 102, "message": "Group with the name " + group.name + " already exists in the database."})
        # push the new repository to the database
        group.insert(app_engine.database)
        return jsonify({"status": 0, "message": "The group " + group.name + " was successfully created."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/group/<string:group_id>', methods=['PUT'])
def update_group(group_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # check if the repository exists
        group = getgroup(app_engine, group_id)
        if not group:
            return jsonify({"status": 103, "message": "No group found."})
        # extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 1, "message": "The content must be JSON format."})
        # validate datarepository
        try:
            group.setName(data['group']['name'])
            group.setDescription(data['group']['description'])
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        # update the database
        group.update(app_engine.database)
        return jsonify({"status": 0, "message": "The group was successfully updated."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/group/<string:group_id>', methods=['DELETE'])
def delete_group(group_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # check if the group exists
        group = getgroup(app_engine, group_id)
        if not group:
            return jsonify({"status": 103, "message": "The group doesn't exist in the database."})
        # delete the group
        group.delete(app_engine.database)
        return jsonify({"status": 0, "message": "The group was successfully deleted."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

@app.route('/api/group/<string:group_id>/clients', methods=['GET'])
def group_clients(group_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_groupeds(group_id)
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

#
# this function link group with clients
#
@app.route('/api/group/<string:group_id>/link/', methods=['POST'])
def group_link(group_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # check if group exists
        group = getgroup(app_engine, group_id)
        if not group:
            return jsonify({"status": 103, "message": "No group with ID:" + group_id})
        
        #extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})

        message = ""
        for client_id in data['data']:
            client = getclient(app_engine, client_id)
            if not client:
                message += "The client with ID: " + client_id + " doesn't exist."
                continue
            # check if they are already binded
            if getgrouped(app_engine, group_id, client_id):
                message += "The client " + client.name + " is already in the group " + group.name + "."
                continue
            # create the bind
            new_grouped = Grouped(client.ID, group.ID)
            # push the bind to the database
            new_grouped.insert(app_engine.database)
            message += "The client " + client.name + " has been added to the group " + group.name + "."
            continue
        return jsonify({"status": 0, "message": message})
        
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()


@app.route('/api/group/<string:group_id>/unlink/', methods=['DELETE'])
def group_unlink(group_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # check if group exists
        group = getgroup(app_engine, group_id)
        if not group:
            return jsonify({"status": 103, "message": "No group with ID:" + group_id})
        
        #extract data
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})

        message = ""
        for client_id in data['data']:
            client = getclient(app_engine, client_id)
            if not client:
                message += "The client with ID: " + client_id + " doesn't exist."
                continue
            
            # check if the grouped exists
            grouped = getgrouped(app_engine, group_id, client_id)
            if not grouped:
                message += "The client " + client.name + " isn't in the group " + group.name + "."
                continue
            
            # delete the grouped
            grouped.delete_grouped(app_engine.database)
            message += "The client " + client.name + " has been removed from the group " + group.name + "."
            continue
        return jsonify({"status": 0, "message": message})

    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

"""
The following functions deal with groups.
"""

# list tasks
@app.route('/api/tasks', methods=['GET'])
def list_task():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_all_object('yarus_task')
        if len(data) > 0:
            return jsonify({"status": 0, "message": "", 'data': data})
        else:
            return jsonify({"status": -1, "message": "No tasks found.", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# see a task
@app.route('/api/task/<string:task_id>', methods=['GET'])
def see_task(task_id):
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the repository and return the data
        task = gettask(app_engine, task_id)
        if not task:
            return jsonify({"status": 103, "message": "No task found."})
        data = task.todata()
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# create a task
@app.route('/api/task', methods=['POST'])
def create_task():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # create a new repository
        task = Task()
        # extract information from received data about the new repository
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        # validate new data
        try:
            task.setID(getnewid())
            task.setStatus('pending')
            task.setCreationDate()
            task.setAction(data['task']['action'])
            task.setObjectID(data['task']['object_id'])
            task.setManagerID(user.ID)
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        # push the new repository to the database
        task.insert(app_engine.database)
        return jsonify({"status": 0, "message": "The task " + task.action + " will be executed."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# delete tasks
@app.route('/api/tasks/', methods=['DELETE'])
def delete_tasks():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        
        try:
            for task_id in data['data']:
                task = gettask(app_engine, task_id)
                if not task:
                    continue
                # delete the task
                task.delete(app_engine.database)
                continue
            return jsonify({"status": 0, "message": "The tasks where successfully deleted from the database."})
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

# list scheduled tasks
@app.route('/api/scheduled', methods=['GET'])
def list_scheduled():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_all_object('yarus_scheduled')
        if len(data) > 0:
            return jsonify({"status": 0, "message": "", 'data': data})
        else:
            return jsonify({"status": -1, "message": "No scheduled tasks found.", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# create a scheduled task
@app.route('/api/scheduledtask', methods=['POST'])
def create_scheduled():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user

        # create a new scheduled task
        schedule = Scheduled()
        # extract information from received data about the new scheduled task
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        # validate new data
        try:
            schedule.setID(getnewid())
            schedule.setCreationDate()
            schedule.last_date = 0
            schedule.setName(data['scheduledtask']['name'])            
            schedule.setDescription(data['scheduledtask']['description'])            
            schedule.setHour(data['scheduledtask']['hour'])            
            schedule.setMinute(data['scheduledtask']['minute'])            
            schedule.setDayofmonth(data['scheduledtask']['day_of_month'])            
            schedule.setMonth(data['scheduledtask']['month'])            
            schedule.setAction(data['scheduledtask']['task_action'])
            schedule.setObjectID(data['scheduledtask']['object_id'])
            schedule.setDayofweek(data['scheduledtask']['day_of_week'])
            schedule.setDayofplace(data['scheduledtask']['day_place'])
            schedule.setManagerID(user.ID)
        except MissingValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 100, "message": str(error)})
        except KeyError as error:
            app_engine.log.debug("Missing key: " + str(error))
            return jsonify({"status": 100, "message": "Missing key: " + str(error)})
        except InvalidValueException as error:
            app_engine.log.debug(str(error))
            return jsonify({"status": 101, "message": str(error)})
        # push the new repository to the database
        schedule.insert(app_engine.database)

        crontab = Crontab()
        if not crontab.generate_cron_file(app_engine.database):
            return jsonify({"status": 1, "message": "The scheduled task " + schedule.name + " has been added but YARUS can't add the cronjob to the cron file."})
        if not crontab.set_cron_file():
            return jsonify({"status": 1, "message": "The scheduled task " + schedule.name + " has been added but YARUS can't add the cronjob to the cron file."})

        return jsonify({"status": 0, "message": "The scheduled task " + schedule.name + " has been added."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

# delete scheduled tasks
@app.route('/api/scheduledtasks/', methods=['DELETE'])
def delete_scheduled():
    try:
        app_engine.database.connect()
        user = getconnecteduser()
        if type(user) != User:
            return user
        # get the list and return it
        data = extract_data()
        if not data:
            return jsonify({"status": 101, "message": "The content must be JSON format."})
        
        try:
            for scheduledtask_id in data['data']:
                scheduledtask = getscheduled(app_engine, scheduledtask_id)
                if not scheduledtask:
                    continue
                # delete the task
                scheduledtask.delete(app_engine.database)
                continue

            crontab = Crontab()
            if not crontab.generate_cron_file(app_engine.database):
                return jsonify({"status": 1, "message": "The scheduled task " + scheduledtask.name + " has been removed but YARUS can't generate the new cron file."})
            if not crontab.set_cron_file():
                return jsonify({"status": 1, "message": "The scheduled task " + scheduledtask.name + " has been removed but YARUS can't remove the cronjob from the cron file."})

            return jsonify({"status": 0, "message": "The tasks where successfully deleted from the database."})
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=6821)
