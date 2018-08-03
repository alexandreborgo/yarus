
from flask import Flask, json, request, session, render_template, redirect, url_for
import requests, datetime
import os

server = "http://127.0.0.1:6821/api"

app = Flask("Yarus Engine")
app.secret_key = "=kdRfVYg!Xgst-vV?bys6&Z@28s7FJXy4hwFtNHfnb#myFxwf+BgHYzwt+uaaMBN"

user = None

# call the API
def callapi(method, path, more_data=None):
    # prepare data
    data = {}

    if 'token' in session:
        user = {}
        user['token'] = session['token']
        data['user'] = user

    if more_data:
        data = {**data, **more_data}

    # transform data into json
    data = json.dumps(data)

    # send request
    call = getattr(requests, method)
    if call:
        try:
            response = call(server + path, data=data)
        except requests.exceptions.ConnectionError as error:
            print(error)
            return {"status": 1,  "message": "Error connecting YARUS Engine, is it running?"}
    else:
        return False

    # extract content
    return json.loads(response.content)

# check if the session token is still valid
def checksession():
    if 'token' in session:
        result = callapi("get", "/login/check/" + session['token'])
        if result['status'] == 0:
            return True
    return False

# login page and dashboard if connected
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form['username'] and request.form['password']:
            user = {}
            user['username'] = request.form['username']
            user['password'] = request.form['password']
            data = {}
            data['user'] = user
            result = callapi("get", "/login", data)
            if result['status'] == 0:
                if 'data' in result:
                    if 'token' in result['data']:
                        session['token'] = result['data']['token']
                        print(session['token'])
            else:
                return render_template('login.html', invalid='1')
        else:
            return render_template('login.html', invalid='1')

    if not checksession():
        return render_template('login.html')
    else:
        return render_template('home.html', connected='1')

# logout page
@app.route('/logout', methods=['GET'])
def logout():
    if not checksession():
        return redirect(url_for('home'))
    del session['token']
    return redirect(url_for('home'))

# error 404 page
@app.errorhandler(404)
def page_not_found(error):
    if not checksession():
        return redirect(url_for('home'))
    return render_template('404.html', connected='1'), 404

# fonction that is executed after the view is called
@app.after_request
def after_request(response):
    # change the Content-Security-Policy header to allow the web browser to get Bootstrap Datatable and other useful tools for the interface (CSS ans JS files)
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' https://debug.datatables.net/ https://api.datatables.net/ https://ajax.googleapis.com/ https://stackpath.bootstrapcdn.com/ https://cdnjs.cloudflare.com/ http://cdnjs.cloudflare.com/ https://use.fontawesome.com/ https://cdn.datatables.net/ http://cdn.datatables.net/"
    return response

# list repositories
@app.route('/repositories', methods=['GET'])
def repositories(status=0, message=""):
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/repositories")
    if 'data' in result:
        new_data = []
        for repository in result['data']:
            if repository['last_sync'] != 0:
                repository['last_sync'] = str(datetime.datetime.fromtimestamp(repository['last_sync']))
            else:
                repository['last_sync'] = "Never synced"
            new_data.append(repository)
        result['data'] = new_data

    if message != "":
        result['message'] = message
        result['status'] = status
    return render_template('repositories.html', result=result, connected='1')

# see one repository
@app.route('/repository/<string:repo_id>/see/', methods=['GET'])
def seerepository(repo_id, status=0, message=""):
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/repository/" + repo_id)
    if result['status'] == 0:
        if 'creation_date' in result['data']:
            result['data']['creation_date'] = str(datetime.datetime.fromtimestamp(int(result['data']['creation_date'])))
            if result['data']['last_sync'] != "0":
                result['data']['last_sync'] = str(datetime.datetime.fromtimestamp(int(result['data']['last_sync'])))
            else:
                result['data']['last_sync'] = "Never synced"
        if 'manager_id' in result['data']:
            result2 = callapi("get", "/user/" + result['data']['manager_id'])
            if 'data' in result2:
                result['data']['manager_id'] = result2['data']['name']

        if message != "":
            result['message'] = message
            result['status'] = status

    return render_template('repository.html', result=result, connected='1')

# add one repository
@app.route('/repository/add/', methods=['GET', 'POST'])
def addrepository():
    if not checksession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = {}
        data['repository'] = {}
        data['repository']['URL'] = request.form['URL']
        data['repository']['type'] = request.form['type']
        data['repository']['repository'] = request.form['distribution']
        data['repository']['release'] = request.form['release']
        data['repository']['path'] = request.form['path']
        data['repository']['components'] = request.form['components']
        data['repository']['architectures'] = request.form['architectures']
        data['repository']['name'] = request.form['name']
        data['repository']['description'] = request.form['description']
        result = callapi("post", "/repository", data)
        return render_template('addrepository.html', result=result, connected='1', data=data)

    return render_template('addrepository.html', connected='1')

# edit one repository
@app.route('/repository/<string:repo_id>/edit/', methods=['GET', 'POST'])
def editrepository(repo_id):
    if not checksession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = {}
        data['repository'] = {}
        data['repository']['URL'] = request.form['URL']
        data['repository']['type'] = request.form['type']
        data['repository']['repository'] = request.form['distribution']
        data['repository']['release'] = request.form['release']
        data['repository']['path'] = request.form['path']
        data['repository']['components'] = request.form['components']
        data['repository']['architectures'] = request.form['architectures']
        data['repository']['name'] = request.form['name']
        data['repository']['description'] = request.form['description']
        result = callapi("put", "/repository/" + repo_id, data)
        return render_template('addrepository.html', result=result, connected='1', data=data)

    result = callapi("get", "/repository/" + repo_id)
    
    if 'data' in result:
        data = {}
        data['repository'] = result['data']
        return render_template('addrepository.html', data=data, connected='1')
    else:
        return redirect(url_for('repositories'))
    
# delete one or more repository
@app.route('/repository/<string:repos_id>', methods=['GET'])
def deleterepositories(repos_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    repos = []
    for repo in repos_id.split(','):
        if repo != "":
            repos.append(repo)
    data['data'] = repos
    result2 = callapi("delete", "/repositories", data )
    result = callapi("get", "/repositories")
    result['message'] = result2['message']
    return repositories(result['status'], result['message'])

# create a task sync_repo to sync the repository
@app.route('/repository/<string:repo_id>/sync/', methods=['GET'])
def syncrepository(repo_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'sync_repo'
    new_task['object_id'] = repo_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    result = callapi("get", "/repository/" + repo_id)
    result['message'] = result2['message']
    return seerepository(repo_id, result['status'], result['message'])

# list channels
@app.route('/channels', methods=['GET'])
def channels():
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/channels")
    if 'data' in result:
        new_data = []
        for channel in result['data']:
            if channel['last_sync'] != 0:
                pass #channel['last_sync'] = str(datetime.datetime.fromtimestamp(channel['last_sync']))
            else:
                channel['last_sync'] = "Never synced"
            new_data.append(channel)
        result['data'] = new_data
    return render_template('channels.html', result=result, connected='1')

# see one channel
@app.route('/channel/<string:channel_id>/see/', methods=['GET'])
def seechannel(channel_id):
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/channel/" + channel_id)
    result2 = callapi("get", "/channel/" + channel_id + "/repositories")
    result['data']['links'] = result2['data']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    return render_template('channel.html', result=result, connected='1')

# create a channel
@app.route('/channel/add/', methods=['GET', 'POST'])
def addchannel():
    if not checksession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = {}
        data['channel'] = {}
        data['channel']['name'] = request.form['name']
        data['channel']['description'] = request.form['description']
        result = callapi("post", "/channel", data)
        return render_template('addchannel.html', result=result, connected='1', data=data)

    return render_template('addchannel.html', connected='1')

# edit one channel
@app.route('/channel/<string:channel_id>/edit/', methods=['GET', 'POST'])
def editchannel(channel_id):
    if not checksession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = {}
        data['channel'] = {}
        data['channel']['name'] = request.form['name']
        data['channel']['description'] = request.form['description']
        result = callapi("put", "/channel/" + channel_id, data)
        return render_template('addchannel.html', result=result, connected='1', data=data)

    result = callapi("get", "/channel/" + channel_id)
    data = {}
    data['channel'] = result['data']
    return render_template('addchannel.html', data=data, connected='1')

# delete one channel
@app.route('/channel/<string:channel_id>/delete/', methods=['GET'])
def deletechannel(channel_id):
    if not checksession():
        return redirect(url_for('home'))
    result2 = callapi("delete", "/channel/" + channel_id)
    result = callapi("get", "/channels")
    result['message'] = result2['message']
    return render_template('channels.html', result=result, connected='1')

# add a repository to a given channel
@app.route('/channel/<string:channel_id>/link/', methods=['POST'])
def linkchannel(channel_id):
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/channel/" + channel_id)

    if request.method == 'POST':
        if request.form['repository']:
            result2 = callapi("post", "/channel/" + channel_id + "/repository/" + request.form['repository'])
            result['message'] = result2['message']
            result['status'] = result2['status']

    result2 = callapi("get", "/channel/" + channel_id + "/repositories")
    result['data']['links'] = result2['data']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    return render_template('channel.html', result=result, connected='1')

# remove a repository from a channel
@app.route('/channel/<string:channel_id>/unlink/<string:repo_id>', methods=['GET'])
def unlinkchannel(channel_id, repo_id):
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/channel/" + channel_id)

    result2 = callapi("delete", "/channel/" + channel_id + "/repository/" + repo_id)
    result['message'] = result2['message']
    result['status'] = result2['status']

    result2 = callapi("get", "/channel/" + channel_id + "/repositories")
    result['data']['links'] = result2['data']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    return render_template('channel.html', result=result, connected='1')

# create a task sync_channel to sync all the repositories inside the channel
@app.route('/channel/<string:channel_id>/sync/', methods=['GET'])
def syncchannel(channel_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'sync_channel'
    new_task['object_id'] = channel_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    result = callapi("get", "/channel/" + channel_id)
    result['message'] = result2['message']
    return render_template('channel.html', result=result, connected='1')

# list clients
@app.route('/clients', methods=['GET'])
def clients():
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/clients")
    return render_template('clients.html', result=result, connected='1')

# see one client
@app.route('/client/<string:client_id>/see/', methods=['GET'])
def seeclient(client_id, status=0, message=""):
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/client/" + client_id)
    
    if result['status'] == 0:
        result2 = callapi("get", "/client/" + client_id + "/rc")
        result['data']['linked'] = result2['data']
        result2 = callapi("get", "/channels")
        result['data']['channels'] = result2['data']
        result2 = callapi("get", "/repositories")
        result['data']['repositories'] = result2['data']
        result2 = callapi("get", "/client/" + client_id + "/upgradable/")
        result['data']['upgradables'] = result2['data']
        result2 = callapi("get", "/client/" + client_id + "/tasks")
        result['data']['tasks'] = result2['data']
        if message != "":
            result['message'] = message
            result['status'] = status

    return render_template('client.html', result=result, connected='1')

# add a client
@app.route('/client/add/', methods=['GET', 'POST'])
def addclient():
    if not checksession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = {}
        data['client'] = {}
        data['client']['name'] = request.form['name']
        data['client']['description'] = request.form['description']
        data['client']['IP'] = request.form['IP']
        data['client']['version'] = request.form['version']
        data['client']['type'] = request.form['type']
        data['client']['distribution'] = request.form['distribution']
        result = callapi("post", "/client", data)
        return render_template('addclient.html', result=result, connected='1', data=data)

    return render_template('addclient.html', connected='1')

# edit one client
@app.route('/client/<string:client_id>/edit/', methods=['GET', 'POST'])
def editclient(client_id):
    if not checksession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = {}
        data['client'] = {}
        data['client']['name'] = request.form['name']
        data['client']['description'] = request.form['description']
        data['client']['IP'] = request.form['IP']
        data['client']['version'] = request.form['version']
        data['client']['type'] = request.form['type']
        data['client']['distribution'] = request.form['distribution']
        result = callapi("put", "/client/" + client_id, data)
        return render_template('addclient.html', result=result, connected='1', data=data)

    result = callapi("get", "/client/" + client_id)
    data = {}
    data['client'] = result['data']
    return render_template('addclient.html', data=data, connected='1')

# remove clients
@app.route('/clients/<string:clients_id>', methods=['GET'])
def deleteclients(clients_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    clients = []
    for client in clients_id.split(','):
        if client != "":
            clients.append(client)
    data['data'] = clients
    result2 = callapi("delete", "/clients/", data )
    result = callapi("get", "/clients")
    result['message'] = result2['message']
    return render_template('clients.html', result=result, connected='1')

# link a client to a repository/channel
@app.route('/client/<string:client_id>/link/<string:rc_id>', methods=['GET'])
def linkclient(client_id, rc_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    rcs = []
    for rc in rc_id.split(','):
        if rc != "":
            rcs.append(rc)
    data['data'] = rcs
    result = callapi("post", "/client/" + client_id + "/link/", data)
    return seeclient(client_id, result['status'], result['message'])

# unlink a client to a repository/channel
@app.route('/client/<string:client_id>/unlink/<string:rc_id>', methods=['GET'])
def unlinkclient(client_id, rc_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    rcs = []
    for rc in rc_id.split(','):
        if rc != "":
            rcs.append(rc)
    data['data'] = rcs
    result = callapi("delete", "/client/" + client_id + "/unlink/", data)
    return seeclient(client_id, result['status'], result['message'])

# create a task chek_client 
@app.route('/client/<string:client_id>/check/', methods=['GET'])
def checkclient(client_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'check_client'
    new_task['object_id'] = client_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    return seeclient(client_id, result2['status'], result2['message'])

# create a task config_client
@app.route('/client/<string:client_id>/config/', methods=['GET'])
def configclient(client_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'config_client'
    new_task['object_id'] = client_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    return seeclient(client_id, result2['status'], result2['message'])

# create a task update_all_client
@app.route('/client/<string:client_id>/updateall/', methods=['GET'])
def allupdateclient(client_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'all_update_client'
    new_task['object_id'] = client_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    return seeclient(client_id, result2['status'], result2['message'])

# create a task update_approved_client
@app.route('/client/<string:client_id>/updateapproved/', methods=['GET'])
def approvedupdateclient(client_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'approved_update_client'
    new_task['object_id'] = client_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    return seeclient(client_id, result2['status'], result2['message'])

# create a task upgradable_client
@app.route('/client/<string:client_id>/upgradable/', methods=['GET'])
def upgradableclient(client_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'upgradable_client'
    new_task['object_id'] = client_id
    data['task'] = new_task
    result = callapi("post", "/task", data)
    return seeclient(client_id, result['status'], result['message'])

# set package as approved for the given list
@app.route('/client/<string:client_id>/approve/<string:packages_id>', methods=['GET'])
def approveupgradables(client_id, packages_id):
    if not checksession():
        return redirect(url_for('home'))

    data = {}
    packages = []
    for package in packages_id.split(','):
        if package != "":
            packages.append(package)
    data['data'] = packages
    result = callapi("put", "/client/" + client_id + "/approve", data)

    return seeclient(client_id, result['status'], result['message'])

# set package as disapproved for the given list
@app.route('/client/<string:client_id>/disapprove/<string:packages_id>', methods=['GET'])
def disapproveupgradables(client_id, packages_id):
    if not checksession():
        return redirect(url_for('home'))
    
    data = {}
    packages = []
    for package in packages_id.split(','):
        if package != "":
            packages.append(package)
    data['data'] = packages
    result = callapi("put", "/client/" + client_id + "/disapprove", data)

    return seeclient(client_id, result['status'], result['message'])

# list groups
@app.route('/groups', methods=['GET'])
def groups():
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/groups")
    return render_template('groups.html', result=result, connected='1')

# see one group
@app.route('/group/<string:group_id>/see/', methods=['GET'])
def seegroup(group_id, status=0, message=""):
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/group/" + group_id)
    result2 = callapi("get", "/group/" + group_id + "/clients")
    result['data']['links'] = result2['data']
    result2 = callapi("get", "/clients")
    result['data']['clients'] = result2['data']

    if message != "":
            result['message'] = message
            result['status'] = status

    return render_template('group.html', result=result, connected='1')

# create a group
@app.route('/group/add/', methods=['GET', 'POST'])
def addgroup():
    if not checksession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = {}
        data['group'] = {}
        data['group']['name'] = request.form['name']
        data['group']['description'] = request.form['description']
        result = callapi("post", "/group", data)
        return render_template('addgroup.html', result=result, connected='1', data=data)

    return render_template('addgroup.html', connected='1')

# edit a group
@app.route('/group/<string:group_id>/edit/', methods=['GET', 'POST'])
def editgroup(group_id):
    if not checksession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = {}
        data['group'] = {}
        data['group']['name'] = request.form['name']
        data['group']['description'] = request.form['description']
        result = callapi("put", "/group/" + group_id, data)
        return render_template('addgroup.html', result=result, connected='1', data=data)

    result = callapi("get", "/group/" + group_id)
    data = {}
    data['group'] = result['data']
    return render_template('addgroup.html', data=data, connected='1')

# delete a group
@app.route('/group/<string:group_id>/delete/', methods=['GET'])
def deletegroup(group_id):
    if not checksession():
        return redirect(url_for('home'))
    result2 = callapi("delete", "/group/" + group_id)
    result = callapi("get", "/groups")
    result['message'] = result2['message']
    return render_template('groups.html', result=result, connected='1')

# add a client to a group
@app.route('/group/<string:group_id>/link/<string:clients_id>', methods=['GET'])
def linkgroup(group_id, clients_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    clients = []
    for client in clients_id.split(','):
        if client != "":
            clients.append(client)
    data['data'] = clients
    result = callapi("post", "/group/" + group_id + "/link/", data)
    return seegroup(group_id, result['status'], result['message'])    

# remove a client from a group
@app.route('/group/<string:group_id>/unlink/<string:clients_id>', methods=['GET'])
def unlinkgroup(group_id, clients_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    clients = []
    for client in clients_id.split(','):
        if client != "":
            clients.append(client)
    data['data'] = clients
    result = callapi("delete", "/group/" + group_id + "/unlink/", data)
    return seegroup(group_id, result['status'], result['message']) 

# create a task check_group
@app.route('/group/<string:group_id>/check/', methods=['GET'])
def checkgroup(group_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'check_group'
    new_task['object_id'] = group_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    return seegroup(group_id, result2['status'], result2['message'])

# create a task config_group
@app.route('/group/<string:group_id>/config/', methods=['GET'])
def configgroup(group_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'config_group'
    new_task['object_id'] = group_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    return seegroup(group_id, result2['status'], result2['message'])

# create a task update_all_group
@app.route('/group/<string:group_id>/updateall/', methods=['GET'])
def allupdategroup(group_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'all_update_group'
    new_task['object_id'] = group_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    return seegroup(group_id, result2['status'], result2['message'])

# create a task upgrade_approved_group
@app.route('/group/<string:group_id>/updateapproved/', methods=['GET'])
def approvedupdategroup(group_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'approved_update_group'
    new_task['object_id'] = group_id
    data['task'] = new_task
    result2 = callapi("post", "/task", data)
    return seegroup(group_id, result2['status'], result2['message'])

# create a task upgradable_group
@app.route('/group/<string:group_id>/upgradable/', methods=['GET'])
def upgradablegroup(group_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    new_task = {}
    new_task['action'] = 'upgradable_group'
    new_task['object_id'] = group_id
    data['task'] = new_task
    result = callapi("post", "/task", data)
    return seegroup(group_id, result['status'], result['message'])

# list tasks
@app.route('/tasks', methods=['GET'])
def tasks():
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/tasks")
    if 'data' in result:
        new_data = []
        for task in result['data']:
            if task['creation_date'] != 0:
                task['creation_date'] = str(datetime.datetime.fromtimestamp(task['creation_date']))
            if task['start_time'] != 0:
                task['start_time'] = str(datetime.datetime.fromtimestamp(task['start_time']))
            else:
                task['start_time'] = "Not started"            
            if task['end_time'] != 0:
                task['end_time'] = str(datetime.datetime.fromtimestamp(task['end_time']))
            else:
                task['end_time'] = "Not finished"           
        
            if task['action'] == 'sync_repo':
                result_tmp = callapi("get", "/repository/" + task['object_id'])
                task['object_id'] = "Repository: " + result_tmp['data']['name']
                task['action'] = "Sync repository"        
            elif task['action'] == 'check_client':
                result_tmp = callapi("get", "/client/" + task['object_id'])
                task['object_id'] = "Client: " + result_tmp['data']['name']
                task['action'] = "Check client"        
            elif task['action'] == 'config_client':
                result_tmp = callapi("get", "/client/" + task['object_id'])
                task['object_id'] = "Client: " + result_tmp['data']['name']
                task['action'] = "Configure client"        
            elif task['action'] == 'upgradable_client':
                result_tmp = callapi("get", "/client/" + task['object_id'])
                task['object_id'] = "Client: " + result_tmp['data']['name']
                task['action'] = "List upgradable packages"

            new_data.append(task)
        result['data'] = new_data
    return render_template('tasks.html', result=result, connected='1')

# see one task
@app.route('/task/<string:task_id>/see/', methods=['GET'])
def seetask(task_id):
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/task/" + task_id)
    try:
        logsfile = '/var/log/yarus/tasks/' + task_id + '.log'
        if os.path.isfile(logsfile):
            logs = open(logsfile, 'r')
            result['data']['logs'] = logs.read()
            logs.close()
    except Exception as error:
        print(error)
        result['data']['logs'] = "Unable to read log file for the task " + task_id

    return render_template('task.html', result=result, connected='1')

# delete tasks
@app.route('/tasks/<string:tasks_id>', methods=['GET'])
def deletetasks(tasks_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    tasks = []
    for task in tasks_id.split(','):
        if task != "":
            tasks.append(task)
    data['data'] = tasks
    result2 = callapi("delete", "/tasks/", data )
    result = callapi("get", "/tasks")
    result['message'] = result2['message']
    return render_template('tasks.html', result=result, connected='1')

# list scheduled tasks
@app.route('/scheduler', methods=['GET'])
def scheduler():
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/scheduled")

    if 'data' in result:
        new_data = []
        for scheduledtask in result['data']:            
            scheduledtask['creation_date'] = str(datetime.datetime.fromtimestamp(int(scheduledtask['creation_date'])))
            if scheduledtask['task_action'] == 'sync_repo':
                result_tmp = callapi("get", "/repository/" + scheduledtask['object_id'])
                scheduledtask['object_id'] = "Repository: " + result_tmp['data']['name']
                scheduledtask['task_action'] = "Sync repository"

            new_data.append(scheduledtask)
        result['data'] = new_data

    return render_template('scheduler.html', result=result, connected='1')

# create a scheduled task
@app.route('/scheduler/add/<string:object_type>/<string:object_id>/<string:action>', methods=['GET', 'POST'])
def addscheduledtask(object_type, object_id, action):
    if not checksession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = {}
        data['scheduledtask'] = {}
        data['scheduledtask']['name'] = request.form['name']
        data['scheduledtask']['description'] = request.form['description']
        data['scheduledtask']['task_action'] = request.form['task_action']
        data['scheduledtask']['object_id'] = request.form['object_id']
        data['scheduledtask']['hour'] = request.form['hour']
        data['scheduledtask']['minute'] = request.form['minute']
        data['scheduledtask']['day_of_month'] = request.form['day_of_month']
        data['scheduledtask']['month'] = request.form['month']
        data['scheduledtask']['day_of_week'] = request.form['day_of_week']
        data['scheduledtask']['day_place'] = request.form['day_place']
        result = callapi("post", "/scheduledtask", data)
        return render_template('addscheduledtask.html', result=result, connected='1', object_type=object_type, object_id=object_id, task_action=action, data=data)

    return render_template('addscheduledtask.html', connected='1', object_type=object_type, object_id=object_id, task_action=action)

# delete scheduled tasks
@app.route('/scheduler/<string:scheduledtasks_id>', methods=['GET'])
def deletescheduledtasks(scheduledtasks_id):
    if not checksession():
        return redirect(url_for('home'))
    data = {}
    tasks = []
    for task in scheduledtasks_id.split(','):
        if task != "":
            tasks.append(task)
    data['data'] = tasks
    result2 = callapi("delete", "/scheduledtasks/", data)
    result = callapi("get", "/scheduled")
    result['message'] = result2['message']
    return render_template('scheduler.html', result=result, connected='1')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
