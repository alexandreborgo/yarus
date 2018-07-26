
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

			self.cursor = self.connection.cursor(dictionary=True)

			if not self.cursor:
				raise(DatabaseError("Can't initiate cursor."))

		except Error as error:
			raise(DatabaseError(error))

		return True
	def close(self):
		try:
			self.cursor.close()
			self.connection.close()
		except Exception:
			raise(DatabaseError("Unable to close the connection to the database correctly."))

	def execute(self, request):
		try:
			self.cursor.execute(request)
			self.connection.commit()
			return True
		except Error as error:
			self.app.log.error(str(error))
			raise(DatabaseError(error))
	def get_one(self, request):
		self.cursor.execute(request)
		return self.cursor.fetchone()
	def get_all(self, request):
		self.cursor.execute(request)
		return self.cursor.fetchall()

	def get_object(self, object_table, ID):
		request = "SELECT * FROM " + object_table + " WHERE ID='" + ID + "'"
		return self.get_one(request)
	def get_all_object(self, object_table):
		request = "SELECT * FROM " + object_table + " ORDER BY creation_date ASC"
		return self.get_all(request)
	def update_object(self, object_table, values):
		inds = ''
		vals = ''
		first = list(values.keys())[0]
		for k, v in values.items():
			tmp = ('null' if v == None else "'" + str(v) + "'")
			if k == first:
				vals += "`" + k + "`" + "=" + tmp
			else:
				vals += ", " + "`" + k + "`" + "=" + tmp
		request = "UPDATE " + object_table + " SET " + vals + " WHERE ID='" + values['ID'] + "'"
		self.execute(request)
		return True
	def insert_object(self, object_table, values):
		inds = ''
		vals = ''
		first = list(values.keys())[0]
		for k, v in values.items():
			tmp = ('null' if v == None else "'" + str(v) + "'")
			if k == first:
				inds += "`" + k + "`"
				vals += tmp
			else:
				inds += ", " + "`" + k + "`"
				vals += ", " + tmp
		request = "INSERT INTO " + object_table + " (" + inds + ") VALUES(" + vals + ")"
		self.execute(request)
		return True
	def delete_object(self, object_table, values):
		for k, v in values.items():
			request = "DELETE FROM " + object_table + " WHERE " + k + "='" + v + "'"
			self.execute(request)

	def get_user_t(self, token):
		request = "SELECT ID,token_expire FROM yarus_user WHERE token='" + token + "'"
		return self.get_one(request)
	def get_user_up(self, name, password):
		sha256_hash = hashlib.sha256()
		sha256_hash.update(password.encode('utf-8'))
		hashed_password = sha256_hash.hexdigest()
		request = "SELECT ID FROM yarus_user WHERE name='" + name + "' AND password='" + hashed_password + "'"
		return self.get_one(request)

	def get_by_name(self, object_table, name):
		request = "SELECT * FROM " + object_table + " WHERE name='" + name + "'"
		return self.get_one(request)

	def get_link(self, channel_id, repo_id):
		request = "SELECT * FROM yarus_link WHERE repo_id='" + repo_id + "' AND channel_id='" + channel_id + "'"
		return self.get_one(request)
	def get_links(self, channel_id):
		request = "SELECT yarus_repository.ID, yarus_repository.name FROM yarus_link INNER JOIN yarus_repository ON yarus_link.repo_id=yarus_repository.ID WHERE yarus_link.channel_id='" + channel_id + "' "
		return self.get_all(request)
	def delete_link(self, channel_id, repo_id):
		request = "DELETE FROM yarus_link WHERE repo_id='" + repo_id + "' AND channel_id='" + channel_id + "'"
		return self.execute(request)

	def get_client_by_ip(self, IP):
		request = "SELECT * FROM yarus_client WHERE IP='" + IP + "'"
		return self.get_one(request)
	def get_binded_repository(self, client_id):
		request = "SELECT yarus_repository.ID, yarus_repository.name FROM yarus_bind INNER JOIN yarus_repository ON yarus_bind.repo_id=yarus_repository.ID WHERE yarus_bind.client_id='" + client_id + "' "
		return self.get_all(request)
	def get_binded_channel(self, client_id):
		request = "SELECT yarus_channel.ID, yarus_channel.name FROM yarus_bind INNER JOIN yarus_channel ON yarus_bind.channel_id=yarus_channel.ID WHERE yarus_bind.client_id='" + client_id + "' "
		return self.get_all(request)
	def get_bind(self, client_id, repo_id, channel_id):
		request = "SELECT * FROM yarus_bind WHERE client_id='" + client_id + "' AND repo_id='" + str(repo_id) + "' AND channel_id='" + str(channel_id) + "'"
		return self.get_one(request)
	def delete_bind(self, client_id, repo_id, channel_id):
		request = "DELETE FROM yarus_bind WHERE client_id='" + client_id + "' AND repo_id='" + str(repo_id) + "' AND channel_id='" + str(channel_id) + "'"
		return self.execute(request)
	def get_upgradable(self, client_id, package_id):
			request = "SELECT * FROM yarus_upgradable WHERE client_id='" + client_id + "' AND ID='" + package_id + "'"
			return self.get_one(request)
	def remove_upgradables(self, client_id):
		request = "DELETE FROM yarus_upgradable WHERE client_id='" + client_id + "'"
		return self.execute(request)
		
	def get_upgradable_by_info(self, client_id, name, release, type):
		request = "SELECT * FROM yarus_upgradable WHERE client_id='" + client_id + "' AND name='" + name + "' AND `release`='" + release + "' AND type='" + type + "'"
		return self.get_all(request)
	def get_upgradables(self, client_id):
		request = "SELECT * FROM yarus_upgradable WHERE client_id='" + client_id + "' "
		return self.get_all(request)

	def get_pending_task(self):
		request = "SELECT ID FROM yarus_task WHERE status='pending' ORDER BY creation_date ASC LIMIT 1"
		return self.get_one(request)
