
"""
    YARUS Web User Interface
"""

import datetime
import os
import sys
import requests
import yaml

from flask import Flask, json, request, session, render_template, redirect, url_for

# open the configuration file
try:
    CONFIG_FILE = open('/etc/yarus/webui.yml', 'r')
except IOError as error:
    print("Unable to read configuration file: /etc/yarus/webui.yml.")
    print(error)
    sys.exit(1)

# parse yaml
try:
    CONFIG = yaml.load(CONFIG_FILE)
except yaml.YAMLError as error:
    print("Configuration file is malformed, it is not good YAML format: /etc/yarus/webui.yml.")
    print(error)
    sys.exit(1)

# engine system related information: address, port
if 'engine' in CONFIG:
    if 'address' in CONFIG['engine']:
        SV_ADDRESS = CONFIG['engine']['address']
    else:
        print("Missing engine's IP address.")
    if 'port' in CONFIG['engine']:
        SV_PORT = CONFIG['engine']['port']
    else:
        print("Missing engine's port.")
else:
    print("Missing engine's information")

if SV_ADDRESS and SV_PORT:
    SERVER = "http://" + str(SV_ADDRESS) + ":" + str(SV_PORT) + "/api"
else:
    sys.exit(1)

APP = Flask("Yarus Engine")
APP.secret_key = "=kdRfVYg!Xgst-vV?bys6&Z@28s7FJXy4hwFtNHfnb#myFxwf+BgHYzwt+uaaMBN"

def callapi(method, path, more_data=None):
    """ call the API """
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
            response = call(SERVER + path, data=data)
        except requests.exceptions.ConnectionError:
            return {"status": 404, "message": "Error connecting YARUS Engine, is it running on " + SV_ADDRESS + ":" + str(SV_PORT) + "?"}
    else:
        return False

    # extract content
    return json.loads(response.content)

def checksession():
    """ check if the session token is still valid """
    if 'token' in session:
        result = callapi("get", "/login/check/" + session['token'])
        if result['status'] == 0:
            return True
    return False

@APP.route('/', methods=['GET', 'POST'])
def home():
    """ login page and dashboard if connected """
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
            else:
                return render_template('login.html', result=result)
        else:
            return render_template('login.html', invalid='1')

    if not checksession():
        return render_template('login.html')
    return render_template('home.html', connected='1')

@APP.route('/logout', methods=['GET'])
def logout():
    """ logout page """
    if not checksession():
        return redirect(url_for('home'))
    del session['token']
    return redirect(url_for('home'))

@APP.errorhandler(404)
def page_not_found(error):
    """ error 404 page """
    if not checksession():
        return redirect(url_for('home'))
    return render_template('404.html', connected='1'), 404

@APP.before_request
def before_request():
    """ before request """
    if request.endpoint != 'home':
        if not checksession():
            return redirect(url_for('home'))


@APP.after_request
def after_request(response):
    """ after request """
    # change the Content-Security-Policy header to allow the web browser to get Bootstrap Datatable and other useful tools for the interface (CSS ans JS files)
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' https://debug.datatables.net/ https://api.datatables.net/ https://ajax.googleapis.com/ https://stackpath.bootstrapcdn.com/ https://cdnjs.cloudflare.com/ http://cdnjs.cloudflare.com/ https://use.fontawesome.com/ https://cdn.datatables.net/ http://cdn.datatables.net/"
    return response

@APP.route("/<string:object_name>/<string:object_id>/task/<string:action>", methods=['GET'])
def add_task(object_name, object_id, action):
    """ add a task """
    data = {}
    new_task = {}
    new_task['action'] = action
    new_task['object_id'] = object_id
    data['task'] = new_task
    result = callapi("post", "/create/task", data)

    if object_name == 'repository':
        return see_object('repository', object_id, result['status'], result['message'])
    elif object_name == 'channel':
        return see_object('channel', object_id, result['status'], result['message'])
    elif object_name == 'client':
        return see_object('client', object_id, result['status'], result['message'])
    elif object_name == 'group':
        return see_object('group', object_id, result['status'], result['message'])

    return render_template('404.html', connected='1'), 404

@APP.route("/<string:object_name>/<string:object_id>/scheduled/<string:action>/", methods=['GET', 'POST'])
def add_scheduled(object_name, object_id, action):
    """ add a scheduled task """
    if request.method == 'POST':
        data = {}
        data['scheduledtask'] = {}
        data['scheduledtask']['name'] = request.form['name']
        data['scheduledtask']['description'] = request.form['description']
        data['scheduledtask']['action'] = request.form['action']
        data['scheduledtask']['object_id'] = request.form['object_id']
        data['scheduledtask']['hour'] = request.form['hour']
        data['scheduledtask']['minute'] = request.form['minute']
        data['scheduledtask']['day_of_month'] = request.form['day_of_month']
        data['scheduledtask']['month'] = request.form['month']
        data['scheduledtask']['day_of_week'] = request.form['day_of_week']
        data['scheduledtask']['day_place'] = request.form['day_place']
        result = callapi("post", "/create/scheduled", data)
        return render_template('addscheduled.html', result=result, connected='1', object_name=object_name, object_id=object_id, action=action, data=data)

    return render_template('addscheduled.html', connected='1', object_name=object_name, object_id=object_id, action=action)

@APP.route('/list/<string:object_name>', methods=['GET'])
def list_object(object_name, status=0, message=""):
    """ list object """

    result = callapi("get", "/list/" + object_name)

    # clea4n up information
    if result['status'] == 0:
        if 'data' in result:
            new_data = []
            for item in result['data']:

                if 'creation_date' in item:
                    item['creation_date'] = str(datetime.datetime.fromtimestamp(int(item['creation_date'])))

                if 'last_sync' in item:
                    if item['last_sync'] != "0":
                        item['last_sync'] = str(datetime.datetime.fromtimestamp(int(item['last_sync'])))
                    else:
                        item['last_sync'] = "Never synced"

                if 'last_check' in item:
                    if item['last_check'] != "0":
                        item['last_check'] = str(datetime.datetime.fromtimestamp(int(item['last_check'])))
                    else:
                        item['last_check'] = "Never checked"

                if 'start_time' in item:
                    if item['start_time'] != 0:
                        item['start_time'] = str(datetime.datetime.fromtimestamp(item['start_time']))
                    else:
                        item['start_time'] = "Not started"

                if 'end_time' in item:
                    if item['end_time'] != 0:
                        item['end_time'] = str(datetime.datetime.fromtimestamp(item['end_time']))
                    else:
                        item['end_time'] = "Not finished"

                if 'manager_id' in item:
                    result2 = callapi("get", "/see/user/" + str(item['manager_id']))
                    if 'data' in result2:
                        item['manager_id'] = result2['data']['name']

                if 'action' in item:
                    if item['action'] == 'sync_repo':
                        result_tmp = callapi("get", "/see/repository/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'repository'
                        else:
                            item['object_name'] = "Repository: unknown"
                        item['action'] = "Sync repository"

                    elif item['action'] == 'sync_channel':
                        result_tmp = callapi("get", "/see/channel/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'channel'
                        else:
                            item['object_name'] = "Channel: unknown"
                        item['action'] = "Sync channel"

                    elif item['action'] == 'check_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'client'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "Check client"
                    elif item['action'] == 'config_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'client'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "Configure client"

                    elif item['action'] == 'upgradable_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'client'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "List upgradable packages"

                    elif item['action'] == 'config_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'group'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "Configure group"

                    elif item['action'] == 'check_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'group'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "Check group"

                    elif item['action'] == 'upgradable_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'group'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "List upgradable packages"

                    elif item['action'] == 'approved_update_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'group'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "Update approved packages"

                    elif item['action'] == 'approved_update_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'client'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "Update approved packages"

                    elif item['action'] == 'all_update_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'group'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "Update all packages"

                    elif item['action'] == 'all_update_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'client'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "Update all packages"

                if 'action' in item:
                    if item['action'] == 'sync_repo':
                        result_tmp = callapi("get", "/see/repository/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'repository'
                        else:
                            item['object_name'] = "Repository: unknown"
                        item['action'] = "Sync repository"

                    elif item['action'] == 'sync_channel':
                        result_tmp = callapi("get", "/see/channel/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'channel'
                        else:
                            item['object_name'] = "Channel: unknown"
                        item['action'] = "Sync channel"

                    elif item['action'] == 'check_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'client'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "Check client"

                    elif item['action'] == 'config_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'client'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "Configure client"

                    elif item['action'] == 'upgradable_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'v'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "List upgradable packages"

                    elif item['action'] == 'config_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'v'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "Configure group"

                    elif item['action'] == 'check_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'group'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "Check group"

                    elif item['action'] == 'upgradable_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'group'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "List upgradable packages"

                    elif item['action'] == 'approved_update_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'group'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "Update approved packages"

                    elif item['action'] == 'approved_update_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'client'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "Update approved packages"

                    elif item['action'] == 'all_update_group':
                        result_tmp = callapi("get", "/see/group/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'group'
                        else:
                            item['object_name'] = "Group: unknown"
                        item['action'] = "Update all packages"

                    elif item['action'] == 'all_update_client':
                        result_tmp = callapi("get", "/see/client/" + item['object_id'])
                        if result_tmp['status'] == 0:
                            item['object_name'] = result_tmp['data']['name']
                            item['object_type'] = 'client'
                        else:
                            item['object_name'] = "Client: unknown"
                        item['action'] = "Update all packages"

                new_data.append(item)
            result['data'] = new_data

    # add arguement message/status
    if message != "":
        result['message'] = message
        result['status'] = status

    if object_name == 'repository':
        return render_template('repositories.html', result=result, connected='1')
    elif object_name == 'channel':
        return render_template('channels.html', result=result, connected='1')
    elif object_name == 'client':
        return render_template('clients.html', result=result, connected='1')
    elif object_name == 'group':
        return render_template('groups.html', result=result, connected='1')
    elif object_name == 'task':
        return render_template('tasks.html', result=result, connected='1')
    elif object_name == 'scheduled':
        return render_template('scheduler.html', result=result, connected='1')

    return render_template('404.html', connected='1'), 404

@APP.route('/see/<string:object_name>/<string:object_id>', methods=['GET'])
def see_object(object_name, object_id, status=0, message=""):
    """ see an object """

    result = callapi("get", "/see/" + object_name + "/" + object_id)

    # clea4n up information
    if result['status'] == 0:
        if 'creation_date' in result['data']:
            result['data']['creation_date'] = str(datetime.datetime.fromtimestamp(int(result['data']['creation_date'])))

        if 'last_sync' in result['data']:
            if result['data']['last_sync'] != "0":
                result['data']['last_sync'] = str(datetime.datetime.fromtimestamp(int(result['data']['last_sync'])))
            else:
                result['data']['last_sync'] = "Never synced"

        if 'last_check' in result['data']:
            if result['data']['last_check'] != "0":
                result['data']['last_check'] = str(datetime.datetime.fromtimestamp(int(result['data']['last_check'])))
            else:
                result['data']['last_check'] = "Never checked"

        if 'manager_id' in result['data']:
            result2 = callapi("get", "/see/user/" + result['data']['manager_id'])
            if 'data' in result2:
                result['data']['manager_id'] = result2['data']['name']

        if 'start_time' in result['data']:
            if result['data']['start_time'] != "0":
                result['data']['start_time'] = str(datetime.datetime.fromtimestamp(int(result['data']['start_time'])))
            else:
                result['data']['start_time'] = "Not started"

        if 'end_time' in result['data']:
            if result['data']['end_time'] != "0":
                result['data']['end_time'] = str(datetime.datetime.fromtimestamp(int(result['data']['end_time'])))
            else:
                result['data']['end_time'] = "Not finished"

        if 'action' in result['data']:
            if result['data']['action'] == 'sync_repo':
                result_tmp = callapi("get", "/see/repository/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'repository'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Repository: unknown"
                result['data']['action'] = "Sync repository"

            elif result['data']['action'] == 'sync_channel':
                result_tmp = callapi("get", "/see/channel/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'channel'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Channel: unknown"
                result['data']['action'] = "Sync channel"

            elif result['data']['action'] == 'check_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "Check client"

            elif result['data']['action'] == 'config_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "Configure client"

            elif result['data']['action'] == 'upgradable_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "List upgradable packages"

            elif result['data']['action'] == 'config_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "Configure group"

            elif result['data']['action'] == 'check_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "Check group"

            elif result['data']['action'] == 'upgradable_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "List upgradable packages"

            elif result['data']['action'] == 'approved_update_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "Update approved packages"

            elif result['data']['action'] == 'approved_update_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "Update approved packages"

            elif result['data']['action'] == 'all_update_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "Update all packages"

            elif result['data']['action'] == 'all_update_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "Update all packages"

        if 'action' in result['data']:
            if result['data']['action'] == 'sync_repo':
                result_tmp = callapi("get", "/see/repository/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'repository'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Repository: unknown"
                result['data']['action'] = "Sync repository"

            elif result['data']['action'] == 'sync_channel':
                result_tmp = callapi("get", "/see/channel/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'channel'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Channel: unknown"
                result['data']['action'] = "Sync channel"

            elif result['data']['action'] == 'check_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "Check client"

            elif result['data']['action'] == 'config_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "Configure client"

            elif result['data']['action'] == 'upgradable_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "List upgradable packages"

            elif result['data']['action'] == 'config_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "Configure group"

            elif result['data']['action'] == 'check_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "Check group"

            elif result['data']['action'] == 'upgradable_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "List upgradable packages"

            elif result['data']['action'] == 'approved_update_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "Update approved packages"

            elif result['data']['action'] == 'approved_update_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "Update approved packages"

            elif result['data']['action'] == 'all_update_group':
                result_tmp = callapi("get", "/see/group/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'group'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Group: unknown"
                result['data']['action'] = "Update all packages"

            elif result['data']['action'] == 'all_update_client':
                result_tmp = callapi("get", "/see/client/" + result['data']['object_id'])
                if result_tmp['status'] == 0:
                    result['data']['object_type'] = 'client'
                    result['data']['object_name'] = result_tmp['data']['name']
                else:
                    result['data']['object_name'] = "Client: unknown"
                result['data']['action'] = "Update all packages"

    # get tasks and scheduled tasks
    #if object_name == 'repository' or object_name == 'channel' or object_name == 'client' or object_name == 'group':
    if object_name in ('repository', 'channel', 'client', 'group'):
        if result['status'] == 0:
            result_tasks = callapi("get", "/" + object_name + "/" + object_id + "/list/tasks")
            new_data = []
            for task in result_tasks['data']:
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

                if 'action' in task:
                    if task['action'] == 'sync_repo':
                        task['action'] = "Sync repository"

                    elif task['action'] == 'sync_channel':
                        task['action'] = "Sync channel"

                    elif task['action'] == 'check_client':
                        task['action'] = "Check client"

                    elif task['action'] == 'config_client':
                        task['action'] = "Configure client"

                    elif task['action'] == 'upgradable_client':
                        task['action'] = "List upgradable packages"

                    elif task['action'] == 'config_group':
                        task['action'] = "Configure group"

                    elif task['action'] == 'check_group':
                        task['action'] = "Check group"

                    elif task['action'] == 'upgradable_group':
                        task['action'] = "List upgradable packages"

                    elif task['action'] == 'approved_update_group':
                        task['action'] = "Update approved packages"

                    elif task['action'] == 'approved_update_client':
                        task['action'] = "Update approved packages"

                    elif task['action'] == 'all_update_group':
                        task['action'] = "Update all packages"

                    elif task['action'] == 'all_update_client':
                        task['action'] = "Update all packages"

                new_data.append(task)

            result['data']['tasks'] = new_data

            result_scheduled = callapi("get", "/" + object_name + "/" + object_id + "/list/scheduled")
            new_data = []
            for scheduled in result_scheduled['data']:

                if 'action' in scheduled:
                    if scheduled['action'] == 'sync_repo':
                        scheduled['action'] = "Sync repository"

                    elif scheduled['action'] == 'sync_channel':
                        scheduled['action'] = "Sync channel"

                    elif scheduled['action'] == 'check_client':
                        scheduled['action'] = "Check client"

                    elif scheduled['action'] == 'config_client':
                        scheduled['action'] = "Configure client"

                    elif scheduled['action'] == 'upgradable_client':
                        scheduled['action'] = "List upgradable packages"

                    elif scheduled['action'] == 'config_group':
                        scheduled['action'] = "Configure group"

                    elif scheduled['action'] == 'check_group':
                        scheduled['action'] = "Check group"

                    elif scheduled['action'] == 'upgradable_group':
                        scheduled['action'] = "List upgradable packages"

                    elif scheduled['action'] == 'approved_update_group':
                        scheduled['action'] = "Update approved packages"

                    elif scheduled['action'] == 'approved_update_client':
                        scheduled['action'] = "Update approved packages"

                    elif scheduled['action'] == 'all_update_group':
                        scheduled['action'] = "Update all packages"

                    elif scheduled['action'] == 'all_update_client':
                        scheduled['action'] = "Update all packages"

                new_data.append(scheduled)

            result['data']['scheduled'] = new_data

    # add arguement message/status
    if message != "":
        result['message'] = message
        result['status'] = status

    if object_name == 'repository':
        return render_template('repository.html', result=result, connected='1')

    elif object_name == 'channel':

        if result['status'] == 0:

            result2 = callapi("get", "/channel/" + object_id + "/list/repositories")
            result['data']['links'] = result2['data']

            result2 = callapi("get", "/list/repository")
            result['data']['repositories'] = result2['data']

        return render_template('channel.html', result=result, connected='1')

    elif object_name == 'client':

        if result['status'] == 0:
            # list linked channels/repositories
            result2 = callapi("get", "/client/" + object_id + "/list/rc")
            result['data']['linked'] = result2['data']

            # list channels and repositories
            result2 = callapi("get", "/list/channel")
            result['data']['channels'] = result2['data']
            result2 = callapi("get", "/list/repository")
            result['data']['repositories'] = result2['data']

            # list packages
            result2 = callapi("get", "/client/" + object_id + "/list/upgradables")
            result['data']['upgradables'] = result2['data']

        return render_template('client.html', result=result, connected='1')

    elif object_name == 'group':
        # list clients in the group
        result2 = callapi("get", "/group/" + object_id + "/list/clients")
        result['data']['links'] = result2['data']

        # list all clients
        result2 = callapi("get", "/list/client")
        result['data']['clients'] = result2['data']

        return render_template('group.html', result=result, connected='1')

    elif object_name == 'task':
        try:
            logsfile = '/var/log/yarus/tasks/' + object_id + '.log'
            if os.path.isfile(logsfile):
                logs = open(logsfile, 'r')
                result['data']['logs'] = logs.read()
                logs.close()
        except IOError:
            result['data']['logs'] = "Unable to read log file for the task " + object_id

        return render_template('task.html', result=result, connected='1')

    elif object_name == 'scheduled':
        return render_template('scheduled.html', result=result, connected='1')

    return render_template('404.html', connected='1'), 404

@APP.route('/add/<string:object_name>', methods=['GET', 'POST'])
def add_object(object_name):
    """ add an object """

    if object_name == 'repository':
        if request.method == 'POST':
            data = {}
            data['repository'] = {}
            data['repository']['URL'] = request.form['URL']
            data['repository']['type'] = request.form['type']
            data['repository']['distribution'] = request.form['distribution']
            data['repository']['release'] = request.form['release']
            data['repository']['path'] = request.form['path']
            data['repository']['components'] = request.form['components']
            data['repository']['architectures'] = request.form['architectures']
            data['repository']['name'] = request.form['name']
            data['repository']['description'] = request.form['description']
            result = callapi("post", "/create/repository", data)
            return render_template('addrepository.html', result=result, connected='1', data=data)

        return render_template('addrepository.html', connected='1')

    elif object_name == 'channel':
        if request.method == 'POST':
            data = {}
            data['channel'] = {}
            data['channel']['name'] = request.form['name']
            data['channel']['description'] = request.form['description']
            result = callapi("post", "/create/channel", data)
            return render_template('addchannel.html', result=result, connected='1', data=data)

        return render_template('addchannel.html', connected='1')

    elif object_name == 'client':
        if request.method == 'POST':
            data = {}
            data['client'] = {}
            data['client']['name'] = request.form['name']
            data['client']['description'] = request.form['description']
            data['client']['IP'] = request.form['IP']
            data['client']['version'] = request.form['version']
            data['client']['type'] = request.form['type']
            data['client']['distribution'] = request.form['distribution']
            result = callapi("post", "/create/client", data)
            return render_template('addclient.html', result=result, connected='1', data=data)

        return render_template('addclient.html', connected='1')

    elif object_name == 'group':
        if request.method == 'POST':
            data = {}
            data['group'] = {}
            data['group']['name'] = request.form['name']
            data['group']['description'] = request.form['description']
            result = callapi("post", "/create/group", data)
            return render_template('addgroup.html', result=result, connected='1', data=data)

        return render_template('addgroup.html', connected='1')

    return render_template('404.html', connected='1'), 404

@APP.route('/edit/<string:object_name>/<string:object_id>', methods=['GET', 'POST'])
def edit_object(object_name, object_id):
    """ edit an object """

    if object_name == 'repository':
        if request.method == 'POST':
            data = {}
            data['repository'] = {}
            data['repository']['URL'] = request.form['URL']
            data['repository']['type'] = request.form['type']
            data['repository']['distribution'] = request.form['distribution']
            data['repository']['release'] = request.form['release']
            data['repository']['path'] = request.form['path']
            data['repository']['components'] = request.form['components']
            data['repository']['architectures'] = request.form['architectures']
            data['repository']['name'] = request.form['name']
            data['repository']['description'] = request.form['description']
            result = callapi("put", "/update/repository/" + object_id, data)
            return render_template('addrepository.html', result=result, connected='1', data=data)

        result = callapi("get", "/see/" + object_name + "/" + object_id)

        if 'data' in result:
            data = {}
            data['repository'] = result['data']
            return render_template('addrepository.html', data=data, connected='1')
        else:
            return redirect(url_for('list_object', object_name='repository'))

    elif object_name == 'channel':
        if request.method == 'POST':
            data = {}
            data['channel'] = {}
            data['channel']['name'] = request.form['name']
            data['channel']['description'] = request.form['description']
            result = callapi("put", "/update/channel/" + object_id, data)
            return render_template('addchannel.html', result=result, connected='1', data=data)

        result = callapi("get", "/see/channel/" + object_id)
        data = {}
        data['channel'] = result['data']
        return render_template('addchannel.html', data=data, connected='1')

    elif object_name == 'client':
        if request.method == 'POST':
            data = {}
            data['client'] = {}
            data['client']['name'] = request.form['name']
            data['client']['description'] = request.form['description']
            data['client']['IP'] = request.form['IP']
            data['client']['version'] = request.form['version']
            data['client']['type'] = request.form['type']
            data['client']['distribution'] = request.form['distribution']
            result = callapi("put", "/update/client/" + object_id, data)
            return render_template('addclient.html', result=result, connected='1', data=data)

        result = callapi("get", "/see/client/" + object_id)
        data = {}
        data['client'] = result['data']
        return render_template('addclient.html', data=data, connected='1')

    elif object_name == 'group':
        if request.method == 'POST':
            data = {}
            data['group'] = {}
            data['group']['name'] = request.form['name']
            data['group']['description'] = request.form['description']
            result = callapi("put", "/update/group/" + object_id, data)
            return render_template('addgroup.html', result=result, connected='1', data=data)

        result = callapi("get", "/see/group/" + object_id)
        data = {}
        data['group'] = result['data']
        return render_template('addgroup.html', data=data, connected='1')

    elif object_name == 'scheduled':
        if request.method == 'POST':
            data = {}
            data['scheduledtask'] = {}
            data['scheduledtask']['name'] = request.form['name']
            data['scheduledtask']['description'] = request.form['description']
            data['scheduledtask']['hour'] = request.form['hour']
            data['scheduledtask']['minute'] = request.form['minute']
            data['scheduledtask']['day_of_month'] = request.form['day_of_month']
            data['scheduledtask']['month'] = request.form['month']
            data['scheduledtask']['day_of_week'] = request.form['day_of_week']
            data['scheduledtask']['day_place'] = request.form['day_place']
            result = callapi("put", "/update/scheduled/" + object_id, data)
            return render_template('addscheduled.html', result=result, connected='1', data=data, object_name=object_name, object_id=object_id)

        result = callapi("get", "/see/scheduled/" + object_id)
        data = {}
        data['scheduledtask'] = result['data']
        return render_template('addscheduled.html', data=data, connected='1', object_name=object_name, object_id=object_id)

    return render_template('404.html', connected='1'), 404

@APP.route('/delete/<string:return_object>/<string:return_id>/<string:object_name>/<string:objects_id>', methods=['GET'])
def delete_object(object_name, objects_id, return_object, return_id):
    """ delete an object """
    data = {}
    objects = []
    for obj in objects_id.split(','):
        if obj != "":
            objects.append(obj)
    data['data'] = objects
    result = callapi("delete", "/delete/" + object_name, data)

    if return_id != 'none':
        return see_object(return_object, return_id, result['status'], result['message'])

    return list_object(return_object, result['status'], result['message'])

@APP.route('/link/<string:object_name>/<string:object_id>/<string:lk_obj_id>', methods=['GET'])
def link(object_name, object_id, lk_obj_id):
    """ link an object with an other """

    if object_name == 'client':
        data = {}
        rcs = []
        for repochan in lk_obj_id.split(','):
            if repochan != "":
                rcs.append(repochan)
        data['data'] = rcs
        result = callapi("post", "/link/client/" + object_id, data)
        return see_object(object_name, object_id, result['status'], result['message'])

    elif object_name == 'group':
        data = {}
        clients = []
        for client in lk_obj_id.split(','):
            if client != "":
                clients.append(client)
        data['data'] = clients
        result = callapi("post", "/link/group/" + object_id, data)
        return see_object(object_name, object_id, result['status'], result['message'])

    elif object_name == 'channel':
        data = {}
        repositories = []
        for repo in lk_obj_id.split(','):
            if repo != "":
                repositories.append(repo)
        data['data'] = repositories
        result = callapi("post", "/link/channel/" + object_id, data)
        return see_object(object_name, object_id, result['status'], result['message'])

    return render_template('404.html', connected='1'), 404

@APP.route('/unlink/<string:object_name>/<string:object_id>/<string:lk_obj_id>', methods=['GET'])
def unlink(object_name, object_id, lk_obj_id):
    """ unlink an object with an other """
    data = {}
    obj_ids = []
    for obj_id in lk_obj_id.split(','):
        if obj_id != "":
            obj_ids.append(obj_id)
    data['data'] = obj_ids
    result = callapi("delete", "/unlink/" + object_name + "/" + object_id, data)
    return see_object(object_name, object_id, result['status'], result['message'])

# not up to date code

@APP.route('/client/<string:client_id>/approve/<string:packages_id>', methods=['GET'])
def approveupgradables(client_id, packages_id):
    """ set package as approved for the given list """
    data = {}
    packages = []
    for package in packages_id.split(','):
        if package != "":
            packages.append(package)
    data['data'] = packages
    result = callapi("put", "/client/" + client_id + "/approve", data)

    return seeclient(client_id, result['status'], result['message'])

@APP.route('/client/<string:client_id>/disapprove/<string:packages_id>', methods=['GET'])
def disapproveupgradables(client_id, packages_id):
    """ set package as disapproved for the given list """
    data = {}
    packages = []
    for package in packages_id.split(','):
        if package != "":
            packages.append(package)
    data['data'] = packages
    result = callapi("put", "/client/" + client_id + "/disapprove", data)

    return seeclient(client_id, result['status'], result['message'])

@APP.route('/group/<string:group_id>/unlink/<string:clients_id>', methods=['GET'])
def unlinkgroup(group_id, clients_id):
    """ remove a client from a group """
    data = {}
    clients = []
    for client in clients_id.split(','):
        if client != "":
            clients.append(client)
    data['data'] = clients
    result = callapi("delete", "/unlink/group/" + group_id, data)
    return seegroup(group_id, result['status'], result['message'])

if __name__ == "__main__":
    APP.run(debug=True, host='0.0.0.0', port=8000)
