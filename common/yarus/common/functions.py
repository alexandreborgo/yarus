
import random
import string
import time

from yarus.common.repository import Repository
from yarus.common.daterepository import Daterepository
from yarus.common.channel import Channel
from yarus.common.user import User
from yarus.common.link import Link
from yarus.common.update import Update
from yarus.common.client import Client
from yarus.common.bind import Bind
from yarus.common.linkrcs import Linkrcs
from yarus.common.task import Task
from yarus.common.group import Group
from yarus.common.upgradable import Upgradable
from yarus.common.grouped import Grouped
from yarus.common.scheduled import Scheduled
from yarus.common.package import Package
from yarus.common.exceptions import *

def getnewid():
	ID = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=32))
	return ID
	
def getnewpassword():
	passwd = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation, k=10))
	return passwd

def connectuser(app, user):
	if user.name and user.password:
		info = app.database.get_user_up(user.name, user.password)
	elif user.token:
		info = app.database.get_user_t(user.token)

	if not info:
		return False

	if 'token_expire' in info:
		if int(time.time()) > info['token_expire']:
			return False
			
	return User().load(app.database, info['ID'])

def getobject(app, object_name, object_id):
	try:
		if object_name == 'repository':
			return Repository().load(app.database, object_id)
		elif object_name == 'update':
			return Update().load(app.database, object_id)
		elif object_name == 'channel':
			return Channel().load(app.database, object_id)
		elif object_name == 'client':
			return Client().load(app.database, object_id)
		elif object_name == 'group':
			return Group().load(app.database, object_id)
		elif object_name == 'task':
			return Task().load(app.database, object_id)
		elif object_name == 'scheduled':
			return Scheduled().load(app.database, object_id)
		elif object_name == 'user':
			return User().load(app.database, object_id)
		elif object_name == 'linkrcs':
			return Linkrcs().load(app.database, object_id)
		elif object_name == 'update':
			return Update().load(app.database, object_id)

	except InvalidValueException as error:
		app.log.debug(str(error))
		return None

	except InvalidValueException as error:
		app.log.debug(str(error))
		return None

def getlinkrcschannels(app, channels_id):
	try:
		return app.database.get_linkrcs_channels(channels_id)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getobjectscheduled(app, object_id):
	try:
		return app.database
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None

def getpackage(app, repository, comp, name, version, arch, rel):
	try:
		return Package().load_package(app.database, repository, comp, name, version, arch, rel)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getpackagebyinfo(app, name, arch, version, release):
	try:
		return Package().load_package_by_info(app.database, name, arch, version, release)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getlinkrcsbyinfo(app, distribution, release, architecture):
	try:
		return Linkrcs().load_linkrcs_by_info(app.database, distribution, release, architecture)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getchannelbyinfo(app, distribution, version):
	try:
		return Channel().load_channel_by_info(app.database, distribution, version)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getdaterepository(app, repository, daterepo):
	try:
		return Daterepository().load_daterepository(app.database, repository, daterepo)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None

def getrepobyname(app, name):
	try:
		return Repository().load_by_name(app.database, name)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getclientbyip(app, client_ip):
	try:
		return Client().load_by_ip(app.database, client_ip)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getgrouped(app, group_id, client_id):
	try:
		return Grouped().load_grouped(app.database, client_id, group_id)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getgroupbyname(app, name):
	try:
		return Group().load_by_name(app.database, name)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getbind(app, client_id, repo_id, channel_id):
	try:
		return Bind().load_bind(app.database, client_id, repo_id, channel_id)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None

def getchannelbyname(app, name):
	try:
		return Channel().load_by_name(app.database, name)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getlink(app, channel_id, repo_id):
	try:
		return Link().load_link(app.database, channel_id, repo_id)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
def getlinks(app, channel_id):
	try:
		return app.database.get_links(channel_id)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None

def getupgradable(app, upgradable_id):
	try:
		return Upgradable().load(app.database, upgradable_id)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None

def getupgradablebyinfo(app, obj, object_id, package_id):
	try:
		return Upgradable().load_upgradable_by_info(app.database, obj, object_id, package_id)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None

def getcorrespondingrepositories(app, distribution, release):
	try:
		return app.database.get_corresponding_repositories(distribution, release)
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None







# keep

def getbinds(app, client_id):
	try:
		bindedr = app.database.get_binded_repository(client_id)
		bindedc = app.database.get_binded_channel(client_id)
		linked = []
		if bindedc:
			for item in bindedc:
				linked.append({'ID': item['ID'], 'name': item['name'], 'description': item['description'], 'type': 'c'})
		if bindedr:
			for item in bindedr:
				linked.append({'ID': item['ID'], 'name': item['name'], 'description': item['description'], 'type': 'r'})
		return linked
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
	except InvalidValueException as error:
		app.log.debug(str(error))
		return None
