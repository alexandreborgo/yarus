
from flask import Flask, json, request, session, render_template, redirect, url_for
import requests
import os

server = "http://127.0.0.1:6821/api"

app = Flask("Yarus Engine")
app.secret_key = "=kdRfVYg!Xgst-vV?bys6&Z@28s7FJXy4hwFtNHfnb#myFxwf+BgHYzwt+uaaMBN"

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

def checksession():
    if 'token' in session:
        return True
    return False

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
                return render_template('home.html', invalid='1')
        else:
            return render_template('home.html', invalid='1')

    if not checksession():
        return render_template('home.html')
    else:
        return render_template('home.html', connected='1')

@app.route('/logout', methods=['GET'])
def logout():
    if not checksession():
        return redirect(url_for('home'))
    del session['token']
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

"""
    The following functions deal with repositories.
"""
@app.route('/repositories', methods=['GET'])
def repositories():
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/repositories")
    return render_template('repositories.html', result=result, connected='1')
@app.route('/repository/<string:repo_id>/see/', methods=['GET'])
def seerepository(repo_id):
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/repository/" + repo_id)
    return render_template('repository.html', result=result, connected='1')
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
        data['repository']['components'] = request.form['components']
        data['repository']['architectures'] = request.form['architectures']
        data['repository']['name'] = request.form['name']
        data['repository']['description'] = request.form['description']
        result = callapi("post", "/repository", data)
        return render_template('addrepository.html', result=result, connected='1', data=data)

    return render_template('addrepository.html', connected='1')
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
        data['repository']['components'] = request.form['components']
        data['repository']['architectures'] = request.form['architectures']
        data['repository']['name'] = request.form['name']
        data['repository']['description'] = request.form['description']
        result = callapi("put", "/repository/" + repo_id, data)
        return render_template('addrepository.html', result=result, connected='1', data=data)

    result = callapi("get", "/repository/" + repo_id)
    data = {}
    data['repository'] = result['data']
    return render_template('addrepository.html', data=data, connected='1')
@app.route('/repository/<string:repo_id>/delete/', methods=['GET'])
def deleterepository(repo_id):
    if not checksession():
        return redirect(url_for('home'))
    result2 = callapi("delete", "/repository/" + repo_id)
    result = callapi("get", "/repositories")
    result['message'] = result2['message']
    return render_template('repositories.html', result=result, connected='1')
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
    return render_template('repository.html', result=result, connected='1')

"""
    The following functions deal with channels.
"""
@app.route('/channels', methods=['GET'])
def channels():
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/channels")
    return render_template('channels.html', result=result, connected='1')
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
@app.route('/channel/<string:channel_id>/delete/', methods=['GET'])
def deletechannel(channel_id):
    if not checksession():
        return redirect(url_for('home'))
    result2 = callapi("delete", "/channel/" + channel_id)
    result = callapi("get", "/channels")
    result['message'] = result2['message']
    return render_template('channels.html', result=result, connected='1')
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

"""
The following functions deal with clients.
"""
@app.route('/clients', methods=['GET'])
def clients():
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/clients")
    return render_template('clients.html', result=result, connected='1')
@app.route('/client/<string:client_id>/see/', methods=['GET'])
def seeclient(client_id, status=0, message=""):
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/client/" + client_id)
    result2 = callapi("get", "/client/" + client_id + "/rc")
    result['data']['linked'] = result2['data']
    result2 = callapi("get", "/channels")
    result['data']['channels'] = result2['data']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    result2 = callapi("get", "/client/" + client_id + "/upgradable/")
    result['data']['upgradables'] = result2['data']
    if message != "":
        result['message'] = message
        result['status'] = status
    return render_template('client.html', result=result, connected='1')
@app.route('/client/<string:client_id>/link/', methods=['POST'])
def linkclient(client_id):
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/client/" + client_id)

    if request.method == 'POST':
        if request.form['rc']:
            type, ID = request.form['rc'].split(':')
            if type == 'r':
                result2 = callapi("post", "/client/" + client_id + "/repository/" + ID)
            elif type == 'c':
                result2 = callapi("post", "/client/" + client_id + "/channel/" + ID)
            result['message'] = result2['message']
            result['status'] = result2['status']

    result2 = callapi("get", "/client/" + client_id + "/rc")
    result['data']['linked'] = result2['data']
    result2 = callapi("get", "/channels")
    result['data']['channels'] = result2['data']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    return render_template('client.html', result=result, connected='1')
@app.route('/client/<string:client_id>/unlink/<string:object_id>/<string:type>', methods=['GET'])
def unlinkclient(client_id, object_id, type):
    if not checksession():
        return redirect(url_for('home'))

    result = callapi("get", "/client/" + client_id)

    if type == 'r':
        result2 = callapi("delete", "/client/" + client_id + "/repository/" + object_id)
    elif type == 'c':
        result2 = callapi("delete", "/client/" + client_id + "/channel/" + object_id)
    result['message'] = result2['message']
    result['status'] = result2['status']

    result2 = callapi("get", "/client/" + client_id + "/rc")
    result['data']['linked'] = result2['data']
    result2 = callapi("get", "/channels")
    result['data']['channels'] = result2['data']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    return render_template('client.html', result=result, connected='1')
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
@app.route('/client/<string:client_id>/delete/', methods=['GET'])
def deleteclient(client_id):
    if not checksession():
        return redirect(url_for('home'))
    result2 = callapi("delete", "/client/" + client_id)
    result = callapi("get", "/clients")
    result['message'] = result2['message']
    return render_template('clients.html', result=result, connected='1')
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
    result = callapi("get", "/client/" + client_id)
    result['message'] = result2['message']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    return render_template('client.html', result=result, connected='1')
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
    result = callapi("get", "/client/" + client_id)
    result['message'] = result2['message']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    return render_template('client.html', result=result, connected='1')
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
    result = callapi("get", "/client/" + client_id)
    result['message'] = result2['message']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    return render_template('client.html', result=result, connected='1')
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
    result = callapi("get", "/client/" + client_id)
    result['message'] = result2['message']
    result2 = callapi("get", "/repositories")
    result['data']['repositories'] = result2['data']
    return render_template('client.html', result=result, connected='1')
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
@app.route('/client/<string:client_id>/approve/<string:package_id>', methods=['GET'])
def approveupgradable(client_id, package_id):
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("put", "/client/" + client_id + "/upgradable/" + package_id + "/approve")
    return seeclient(client_id, result['status'], result['message'])
@app.route('/client/<string:client_id>/disapprove/<string:package_id>', methods=['GET'])
def disapproveupgradable(client_id, package_id):
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("put", "/client/" + client_id + "/upgradable/" + package_id + "/disapprove")
    return seeclient(client_id, result['status'], result['message'])

"""
The following functions deal with tasks.
"""
@app.route('/tasks', methods=['GET'])
def tasks():
    if not checksession():
        return redirect(url_for('home'))
    result = callapi("get", "/tasks")
    return render_template('tasks.html', result=result, connected='1')
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
@app.route('/task/<string:task_id>/delete/', methods=['GET'])
def deletetask(task_id):
    if not checksession():
        return redirect(url_for('home'))
    result2 = callapi("delete", "/task/" + task_id)
    result = callapi("get", "/tasks")
    result['message'] = result2['message']
    return render_template('tasks.html', result=result, connected='1')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
