
import hashlib
import mysql.connector
from mysql.connector import Error

from yarus.common.exceptions import *

class Mysql:

	def __init__(self, app, host, username, password, database):
		self.host = host
		self.username = username
		self.password = password
		self.database = database
		self.app = app
	def connect(self):
		try:
			self.connection = mysql.connector.connect(host=self.host, user=self.username, password=self.password, database=self.database)

			if not self.connection.is_connected():
				raise(DatabaseError("Unable to connect to the MySQL database."))

			self.cursor = self.connection.cursor(buffered=True, dictionary=True)

			if not self.cursor:
				raise(DatabaseError("Can't initiate cursor."))

		except Error as error:
			raise(DatabaseError(error))

		return True
	def close(self):
		try:
			self.cursor.close()
			self.connection.close()
		except Exception as error:
			raise(DatabaseError("Unable to close the connection to the database correctly."))

	def get_object_what(self, what, object_id, object_type):
		request = "SELECT * FROM yarus_" + what + " WHERE object_id=%s AND object_type=%s"
		data = (object_id, object_type)
		return self.get_all(request, data)
	
	def get_upgraded(self, update_id):
		request = "SELECT * FROM yarus_upgraded INNER JOIN yarus_package ON yarus_upgraded.package_id=yarus_package.ID WHERE update_id=%s"
		data = (update_id,)
		return self.get_all(request, data)
	

	def get_upgradables(self, object_id, object_type):
		select = "yarus_upgradable.ID, yarus_upgradable.package_id, yarus_upgradable.approved, yarus_package.name, yarus_package.release, yarus_package.version, yarus_package.summary, yarus_package.component, yarus_package.type"
		request = "SELECT " + select + " FROM yarus_upgradable INNER JOIN yarus_package ON yarus_upgradable.package_id=yarus_package.ID WHERE object_id=%s AND object_type=%s"
		data = (object_id, object_type)
		return self.get_all(request, data)








	def get_user_t(self, token):
		request = "SELECT ID,token_expire FROM yarus_user WHERE token='" + token + "'"
		return self.get_one(request)
	def get_user_up(self, name, password):
		sha256_hash = hashlib.sha256()
		sha256_hash.update(password.encode('utf-8'))
		hashed_password = sha256_hash.hexdigest()
		request = "SELECT ID FROM yarus_user WHERE name='" + name + "' AND password='" + hashed_password + "'"
		return self.get_one(request)
	def get_user_by_name(self, name):
		request = "SELECT ID FROM yarus_user WHERE name=%s"
		data = (name,)
		return self.get_one(request,data)
	
	def get_links(self, channel_id):
		request = "SELECT * FROM yarus_link INNER JOIN yarus_repository ON yarus_link.repo_id=yarus_repository.ID WHERE yarus_link.channel_id='" + channel_id + "' "
		return self.get_all(request)
	

	def get_binded_repository(self, client_id):
		request = "SELECT yarus_repository.ID, yarus_repository.name, yarus_repository.description FROM yarus_bind INNER JOIN yarus_repository ON yarus_bind.repo_id=yarus_repository.ID WHERE yarus_bind.client_id='" + client_id + "' "
		return self.get_all(request)
	def get_binded_channel(self, client_id):
		request = "SELECT yarus_channel.ID, yarus_channel.name, yarus_channel.description FROM yarus_bind INNER JOIN yarus_channel ON yarus_bind.channel_id=yarus_channel.ID WHERE yarus_bind.client_id='" + client_id + "' "
		return self.get_all(request)
	

	def get_upgradable(self, client_id, package_id):
			request = "SELECT * FROM yarus_upgradable WHERE client_id='" + client_id + "' AND ID='" + package_id + "'"
			return self.get_one(request)

	def get_pending_task(self):
		request = "SELECT ID FROM yarus_task WHERE status='pending' ORDER BY creation_date ASC"
		return self.get_all(request)

	
	def get_groupeds(self, group_id):
		request = "SELECT * FROM yarus_grouped INNER JOIN yarus_client ON yarus_grouped.client_id=yarus_client.ID WHERE group_id='" + group_id + "'"
		return self.get_all(request)
	

	def get_scheduled_tasks(self):
		request = "SELECT * FROM yarus_scheduled"
		return self.get_all(request)

	def get_corresponding_repositories(self, distribution, release):
		request = "SELECT * FROM yarus_repository WHERE repository='" + distribution + "' AND `release`='" + release + "'"
		return self.get_all(request)

# approved

	def execute(self, request, data=""):
		try:
			if data != "":
				self.cursor.execute(request, data)
			else:
				self.cursor.execute(request)
			
			self.connection.commit()

			return True
		except Error as error:
			self.app.log.error(str(error))
			raise(DatabaseError(error))
	def get_one(self, request, data=""):
		try:			
			if data != "":
				self.cursor.execute(request, data)
			else:
				self.cursor.execute(request)
			
			return self.cursor.fetchone()
		except Error as error:
			self.app.log.error(str(error))
			raise(DatabaseError(error))
	def get_all(self, request, data=""):
		try:			
			if data != "":
				self.cursor.execute(request, data)
			else:
				self.cursor.execute(request)
			
			return self.cursor.fetchall()
		except Error as error:
			self.app.log.error(str(error))
			raise(DatabaseError(error))

	def get_object(self, object_table, ID):
		request = "SELECT * FROM " + object_table + " WHERE ID=%s"
		data = (ID,)
		return self.get_one(request, data)
	def get_objects(self, object_table, IDs):
		request = "SELECT * FROM " + object_table + " WHERE ID in (%s)"
		data = tuple(IDs)
		return self.get_one(request, data)
	def get_all_object(self, object_table):
		request = "SELECT * FROM " + object_table + " ORDER BY creation_date ASC"
		return self.get_all(request)
	def get_all_object_own(self, object_table, user):
		request = "SELECT * FROM " + object_table + " WHERE manager_id=%s ORDER BY creation_date ASC"
		data = (user.ID,)
		return self.get_all(request, data)
	def get_all_object_with_manager(self, object_table):
		request = "SELECT " + object_table + ".*, yarus_user.name AS mname FROM " + object_table + " INNER JOIN yarus_user ON " + object_table + ".manager_id=yarus_user.ID"
		return self.get_all(request)
	def get_all_updates(self):
		request = "SELECT * FROM yarus_update ORDER BY date ASC"
		result = self.get_all(request)
		final_result = []
		for item in result:
			tmp = {}
			tmp['info'] = item
			if item['object_type'] == 'client':
				request = "SELECT * FROM yarus_client WHERE ID=%s"
				data = (item['object_id'],)
			elif item['object_type'] == 'group':
				request = "SELECT * FROM yarus_group WHERE ID=%s"
				data = (item['object_id'],)
			object_ = self.get_one(request,data)
			tmp['object'] = object_
			final_result.append(tmp)
		return final_result	

	def update_object(self, object_table, values):
		inds = ''
		vals = ''
		data = []
		first = list(values.keys())[0]
		for k, v in values.items():
			tmp = (None if v == None else str(v))
			if k == first:
				vals += "`" + k + "`" + "=%s"
				data.append(tmp)
			else:
				vals += ", " + "`" + k + "`" + "=%s"
				data.append(tmp)
		request = "UPDATE " + object_table + " SET " + vals + " WHERE ID='" + values['ID'] + "'"
		self.execute(request, tuple(data))
		return True
	def insert_object(self, object_table, values):
		inds = ''
		vals = ''
		data = []
		first = list(values.keys())[0]
		for k, v in values.items():
			tmp = (None if v == None else str(v))
			if k == first:
				inds += "`" + k + "`"
				vals += "%s"
				data.append(tmp)
			else:
				inds += ", " + "`" + k + "`"
				vals += ", %s"
				data.append(tmp)
		request = "INSERT INTO " + object_table + " (" + inds + ") VALUES(" + vals + ")"
		self.execute(request, tuple(data))
		return True
	def delete_object(self, object_table, values):
		for k, v in values.items():
			request = "DELETE FROM " + object_table + " WHERE " + k + "='" + v + "'"
			self.execute(request)

	def get_by_name(self, object_table, name):
		request = "SELECT * FROM " + object_table + " WHERE name=%s"
		data = (name,)
		return self.get_one(request, data)

	def get_client_by_ip(self, IP):
		request = "SELECT * FROM yarus_client WHERE IP=%s"
		data = (IP,)
		return self.get_one(request, data)
	
	def get_bind(self, client_id, repo_id, channel_id):
		request = "SELECT * FROM yarus_bind WHERE client_id=%s AND repo_id=%s AND channel_id=%s"
		data = (client_id, repo_id, channel_id)
		return self.get_one(request, data)
	def delete_bind(self, client_id, repo_id, channel_id):
		request = "DELETE FROM yarus_bind WHERE client_id=%s AND repo_id=%s AND channel_id=%s"
		data = (client_id, repo_id, channel_id)
		return self.execute(request, data)
	
	def get_link(self, channel_id, repo_id):
		request = "SELECT * FROM yarus_link WHERE channel_id=%s AND repo_id=%s"
		data = (channel_id, repo_id)
		return self.get_one(request, data)
	def delete_link(self, channel_id, repo_id):
		request = "DELETE FROM yarus_link WHERE channel_id=%s AND repo_id=%s"
		data = (channel_id, repo_id)
		return self.execute(request, data)

	def get_grouped(self, client_id, group_id):
		request = "SELECT * FROM yarus_grouped WHERE client_id=%s AND group_id=%s"
		data = (client_id, group_id)
		return self.get_one(request, data)
	def delete_grouped(self, client_id, group_id):
		request = "DELETE FROM yarus_grouped WHERE client_id=%s AND group_id=%s"
		data = (client_id, group_id)
		return self.execute(request, data)

	def get_daterepository(self, repository, date):
		request = "SELECT * FROM yarus_daterepository WHERE repository=%s AND date=%s"
		data = (repository, date)
		return self.get_one(request, data)

	def get_package(self, repository, comp, name, version, arch, rel):
		request = "SELECT * FROM yarus_package WHERE repository=%s AND component=%s AND name=%s AND version=%s AND architecture=%s AND `release`=%s"
		data = (repository, comp, name, version, arch, rel)
		return self.get_one(request, data)

	def get_channel_by_info(self, distribution, version):
		request = "SELECT * FROM yarus_channel WHERE distribution=%s AND `release`=%s"
		data = (distribution, version)
		return self.get_one(request, data)
	def get_package_by_info(self, name, arch, version, release):
		request = "SELECT * FROM yarus_package WHERE name=%s AND architecture=%s AND version=%s AND `release`=%s"
		data = (name, arch, version, release)
		return self.get_one(request, data)
	def get_linkrcs_by_info(self, distribution, release, architecture):
		request = "SELECT * FROM yarus_linkrcs WHERE `distribution`=%s AND `release`=%s AND `architecture`=%s"
		data = (distribution, release, architecture)
		return self.get_one(request, data)
	def get_linkrcs_channels(self, channels_id):
		t = str(tuple(channels_id)) if len(channels_id) > 1 else str(tuple(channels_id)).replace(',', '')
		request = "SELECT * FROM yarus_channel WHERE `ID` IN " + t
		return self.get_all(request)

	def get_updated_package(self, update_id):
		request = "SELECT * FROM yarus_upgraded WHERE update_id=%s"
		data = (update_id,)
		return self.get_all(request, data)

	def check_unique_mail(self, info):
		request = "SELECT * FROM yarus_user WHERE mail=%s"
		data = (info,)
		return self.get_one(request, data)
	def check_unique_username(self, info):
		request = "SELECT * FROM yarus_user WHERE name=%s"
		data = (info,)
		return self.get_one(request, data)

	def get_approved_upgradables(self, object_id, object_type):
		request = "SELECT * FROM yarus_upgradable INNER JOIN yarus_package ON yarus_upgradable.package_id=yarus_package.ID WHERE yarus_upgradable.object_id=%s AND yarus_upgradable.approved=1 AND yarus_upgradable.object_type=%s"
		data = (object_id,object_type)
		return self.get_all(request, data)
	def approve_upgradable(self, object_id, object_type, package_id):
		request = "UPDATE yarus_upgradable SET approved=1 WHERE object_id=%s AND object_type=%s AND package_id=%s"
		data = (object_id, object_type, package_id)
		return self.execute(request, data)
	def get_upgradable_by_info(self, obj, object_id, package_id):
		request = "SELECT * FROM yarus_upgradable WHERE object_type=%s AND object_id=%s AND package_id=%s"
		data = (obj, object_id, package_id)
		return self.get_one(request, data)
	def remove_upgradables(self, client_id, object_type):
		request = "DELETE FROM yarus_upgradable WHERE object_id=%s AND object_type=%s"
		data = (client_id,object_type)
		return self.execute(request, data)

	def get_client_group(self, client_id):
		request = "SELECT * FROM yarus_grouped INNER JOIN yarus_group ON yarus_grouped.group_id=yarus_group.ID WHERE client_id=%s"
		data = (client_id,)
		return self.get_one(request, data)