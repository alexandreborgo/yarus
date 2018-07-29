
from flask import Flask, json, jsonify, request
from yarus.engine.appengine import AppEngine
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
def getuser():
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
        user = getuser()
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

"""
    The following functions deal with repositories.
"""
@app.route('/api/repositories', methods=['GET'])
def list_repository():
    try:
        app_engine.database.connect()
        user = getuser()
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
        user = getuser()
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
        user = getuser()
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
                print(data['repository'])
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
        user = getuser()
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
@app.route('/api/repository/<string:repo_id>', methods=['DELETE'])
def delete_repository(repo_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # check if the repository exists
        repo = getrepo(app_engine, repo_id)
        if not repo:
            return jsonify({"status": 103, "message": "The repository doesn't exist in the database."})
        # delete the repository
        repo.delete(app_engine.database)
        return jsonify({"status": 0, "message": "The repository was successfully deleted."})
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
        user = getuser()
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
        user = getuser()
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
        user = getuser()
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
        user = getuser()
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
        user = getuser()
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
        user = getuser()
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
        user = getuser()
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
        user = getuser()
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
The following functions deal with clients.
"""
@app.route('/api/clients', methods=['GET'])
def list_client():
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_all_object('yarus_client')
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/client/<string:client_id>', methods=['GET'])
def see_client(client_id):
    try:
        app_engine.database.connect()
        user = getuser()
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
@app.route('/api/client', methods=['POST'])
def create_client():
    try:
        app_engine.database.connect()
        user = getuser()
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
        return jsonify({"status": 0, "message": "The client " + client.name + " was successfully created."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/client/<string:client_id>', methods=['PUT'])
def update_client(client_id):
    try:
        app_engine.database.connect()
        user = getuser()
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
@app.route('/api/client/<string:client_id>', methods=['DELETE'])
def delete_client(client_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # check if the channel exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "The client doesn't exist in the database."})
        # delete the channel
        client.delete(app_engine.database)
        return jsonify({"status": 0, "message": "The client was successfully deleted."})
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
        user = getuser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_all_object('yarus_group')
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/group/<string:group_id>', methods=['GET'])
def see_group(group_id):
    try:
        app_engine.database.connect()
        user = getuser()
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
        user = getuser()
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
        user = getuser()
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
        user = getuser()
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
        user = getuser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_groupeds(group_id)
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/group/<string:group_id>/link/<string:client_id>', methods=['POST'])
def group_link(group_id, client_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # check if group and channel exists
        group = getgroup(app_engine, group_id)
        if not group:
            return jsonify({"status": 103, "message": "No group found."})
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})
        # check if they are already binded
        if getgrouped(app_engine, group_id, client_id):
            return jsonify({"status": 102, "message": "The client " + client.name + " is already in the group " + group.name})
        # create the bind
        new_grouped = Grouped(client.ID, group.ID)
        # push the bind to the database
        new_grouped.insert(app_engine.database)
        return jsonify({"status": 0, "message": "The client " + client.name + " was successfully added to the group " + group.name + "."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/group/<string:group_id>/unlink/<string:client_id>', methods=['DELETE'])
def group_unlink(group_id, client_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # check if the grouped exists
        grouped = getgrouped(app_engine, group_id, client_id)
        if not grouped:
            return jsonify({"status": 103, "message": "The link doesn't exist in the database."})
        # delete the grouped
        grouped.delete_grouped(app_engine.database)
        return jsonify({"status": 0, "message": "The link was successfully deleted."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

"""
    The following functions deal with links between client and channels/repositories.
"""
@app.route('/api/client/<string:client_id>/rc', methods=['GET'])
def client_rc(client_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # get the list and return it
        data = getbinds(app_engine, client_id)
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/client/<string:client_id>/repository/<string:repo_id>', methods=['POST'])
def client_add_repository(client_id, repo_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # check if repository and channel exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})
        repo = getrepo(app_engine, repo_id)
        if not repo:
            return jsonify({"status": 103, "message": "No repository found."})
        # check if client can handle repository type
        if client.type != repo.type:
            return jsonify({"status": 102, "message": "The repository " + repo.name + " (" + repo.type + ") isn't compatible with the client " + client.name + " (" + client.type + ")"})
        # check if they are already binded
        if getbind(app_engine, client_id, repo_id, ""):
            return jsonify({"status": 102, "message": "Repository " + repo.name + " is linked to the client " + client.name})
        # create the bind
        new_bind = Bind(client.ID, repo_id=repo.ID)
        # push the bind to the database
        new_bind.insert(app_engine.database)
        return jsonify({"status": 0, "message": "The repository " + repo.name + " was successfully linked to the client " + client.name + "."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/client/<string:client_id>/channel/<string:channel_id>', methods=['POST'])
def client_add_channel(client_id, channel_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # check if repository and channel exists
        client = getclient(app_engine, client_id)
        if not client:
            return jsonify({"status": 103, "message": "No client found."})
        channel = getchannel(app_engine, channel_id)
        if not channel:
            return jsonify({"status": 103, "message": "No repository found."})
        # check if they are already binded
        if getbind(app_engine, client_id, "", channel_id):
            return jsonify({"status": 102, "message": "Channel " + channel.name + " is linked to the client " + client.name})
        # create the bind
        new_bind = Bind(client.ID, channel_id=channel.ID)
        # push the bind to the database
        new_bind.insert(app_engine.database)
        return jsonify({"status": 0, "message": "The channel " + channel.name + " was successfully linked to the client " + client.name + "."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/client/<string:client_id>/repository/<string:repo_id>', methods=['DELETE'])
def client_delete_repository(client_id, repo_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # check if the channel exists
        bind = getbind(app_engine, client_id, repo_id, "")
        if not bind:
            return jsonify({"status": 103, "message": "The bind doesn't exist in the database."})
        # delete the channel
        bind.delete_bind(app_engine.database)
        return jsonify({"status": 0, "message": "The bind was successfully deleted."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/client/<string:client_id>/channel/<string:channel_id>', methods=['DELETE'])
def client_delete_channel(client_id, channel_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # check if the channel exists
        bind = getbind(app_engine, client_id, "", channel_id)
        if not bind:
            return jsonify({"status": 103, "message": "The bind doesn't exist in the database."})
        # delete the channel
        bind.delete_bind(app_engine.database)
        return jsonify({"status": 0, "message": "The bind was successfully deleted."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

"""
    The following functions deal with upgradable packages.
"""
@app.route('/api/client/<string:client_id>/upgradable/', methods=['GET'])
def seeupgradable(client_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # get the list and return it
        data = getupgradables(app_engine, client_id)
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/client/<string:client_id>/upgradable/<string:package_id>/approve', methods=['PUT'])
def approveupgradable(client_id, package_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        upgradable = getupgradable(app_engine, client_id, package_id)
        if not upgradable:
            return jsonify({"status": 103, "message": "No upgradable found."})
        upgradable.approved = 1
        upgradable.update(app_engine.database)
        return jsonify({"status": 0, "message": "Package " + upgradable.name + " approved for update."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/client/<string:client_id>/upgradable/<string:package_id>/disapprove', methods=['PUT'])
def disapproveupgradable(client_id, package_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        upgradable = getupgradable(app_engine, client_id, package_id)
        if not upgradable:
            return jsonify({"status": 103, "message": "No upgradable found."})
        upgradable.approved = 0
        upgradable.update(app_engine.database)
        return jsonify({"status": 0, "message": "Package " + upgradable.name + " disapproved for update."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

"""
The following functions deal with groups.
"""

"""
The following functions deal with tasks.
"""
@app.route('/api/tasks', methods=['GET'])
def list_task():
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # get the list and return it
        data = app_engine.database.get_all_object('yarus_task')
        return jsonify({"status": 0, "message": "", 'data': data})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()
@app.route('/api/task/<string:task_id>', methods=['GET'])
def see_task(task_id):
    try:
        app_engine.database.connect()
        user = getuser()
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
@app.route('/api/task', methods=['POST'])
def create_task():
    try:
        app_engine.database.connect()
        user = getuser()
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
@app.route('/api/task/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        app_engine.database.connect()
        user = getuser()
        if type(user) != User:
            return user
        # check if the task exists
        task = gettask(app_engine, task_id)
        if not task:
            return jsonify({"status": 103, "message": "The task doesn't exist in the database."})
        # delete the task
        task.delete(app_engine.database)
        return jsonify({"status": 0, "message": "The task was successfully deleted."})
    except DatabaseError:
        return jsonify({"status": 1, "message": "Database error. If this error persist please contact the administrator.", "data": ""})
    finally:
        app_engine.database.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=6821)
