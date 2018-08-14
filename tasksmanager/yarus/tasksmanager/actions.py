import os
import sys
import gzip
import re
import json
import datetime
import shutil
from lxml import etree

from yarus.common.repository import Repository
from yarus.common.daterepository import Daterepository
from yarus.common.functions import *
from yarus.common.exceptions import *
from yarus.common.upgradable import Upgradable
from yarus.tasksmanager.ansible import Ansible
from yarus.tasksmanager.functions import *

def show_playbook(app, playbook):
	app.log.logtask("The following playbook will be executed:")
	with open(playbook) as file:
		for line in file:
			app.log.logtask(line)

def getAnsibleOutput(response, host, taskname):
	if 'plays' in response:
		for play in response['plays']:
			if 'tasks' in play:
				for task in play['tasks']:
					if task['task']['name'] == taskname:
						if host in task['hosts']:
							return task['hosts'][host]['stdout_lines']

def taskFailed(response, host):
	if 'stats' in response:
		if host in response['stats']:
			if response['stats'][host]['failures'] == 0:
				return False
			else:
				return True
	return True

def add_upgradable(app, client, lines):
	if len(lines) == 0:
		app.log.logtask("No package to update found.")
		return False
	
	if client.type == 'YUM':
		# first lines is useless
		lines.pop(0)

		for line in lines:
			l = line.split(" ")
			l = list(filter(lambda a: a != '', l))
			name = l[0].split('.')[0]
			release = l[1]
			type = l[2]
			package_id = getnewid()
			if getupgradablebyinfo(app, client.ID, name, release, type):
				continue
			upgradable = Upgradable(name=name, release=release, type=type, ID=package_id, client_id=client.ID, approved=0)
			upgradable.insert(app.database)

	elif client.type == 'APT':
		# first lines is useless
		lines.pop(0)

		for line in lines:
			l = line.split(" ")
			name, type = l[0].split('/')
			release = l[1]
			package_id = getnewid()
			if getupgradablebyinfo(app, client.ID, name, release, type):
				continue
			upgradable = Upgradable(name=name, release=release, type=type, ID=package_id, client_id=client.ID, approved=0)
			upgradable.insert(app.database)

# --------------------------------------------------------

def sync_repo(app, repo_id):
	
	# check if repo exists
	repository = getobject(app, 'repository', repo_id)        
	if not repository:
		app.log.logtask("Error: no repository with ID: " + repo_id + " in the database.")
		return False

	app.log.logtask("Syncing repository " + repository.name)

	# the date for the date versionning of the repository
	# need to be here!
	date = datetime.datetime.now()

	if repository.type == 'APT':

		# transform comps and arch into a list
		comps = repository.components.split(',')
		archs = repository.architectures.split(',')

		dremote = repository.URL + "dists/" + repository.path
		dlocal = app.config.rp_folder + "/" + repository.distribution + "/dists/" + repository.path

		# check if local root exists, if not create it
		if not os.path.isdir(dlocal):
			os.makedirs(dlocal)
		 
		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 1: downloading metadata files
		# ------------------------------------------------------------------------------------------------------------------------------

		app.log.logtask("Downloading metadata files...")

		release = getFile_rsync(app, dremote, dlocal, "/Release")
		releasegpg = getFile_rsync(app, dremote, dlocal, "/Release.gpg")
		inrelease = getFile_rsync(app, dremote, dlocal, "/InRelease")

		if release and releasegpg:
			metafile = "release"
		else:
			if inrelease:
				metafile = "inrelease"
			else:
				app.log.logtask("Unable to find metadata files on the remote repository.")
				return False

		# check if the pgp signature is valid
		# gpg --import RPM-GPG-KEY-CentOS-7
		# gpg --verify repomd.xml.asc repomd.xml

		if metafile == "release":
			try:
				release_f = open(release, "r")
			except Exception as error:
				app.log.logtask("Can't open local Release file.")
				app.log.logtask(error)
				return False

		# we don't need the "header" of the file
		# so go to next line until we see sha256
					
		line = release_f.readline()
		while "SHA256:" not in line:
			line = release_f.readline()

		# after this line we have the content we need
		# so we keep it
		line = release_f.readline()
		file_line = []

		# we take the lines until the begening of SHA1 section or the line Acquire-By-Hash:
		while "SHA1:" not in line and "Acquire-By-Hash:" not in line and line:
			l = line.split()
			# we check if the line match our needs
			l = parseReleaseLine(l, comps, archs)
			if l:
				file_line.append(l)
			line = release_f.readline()

		# if we get 0 line there's nothing to do
		if len(file_line) == 0:
			app.log.logtask("No packages corresponding the components " + repo.components + " and architectures " + repo.architectures + ".")
			return False

		# downloading the files containing package list and other files useful to apt
		for item in file_line:

			file = "/" + item[2].split("/")[-1]
			remote_file_dir = dremote
			local_file_dir = dlocal

			for x in item[2].split("/"):
				if x not in file:
					remote_file_dir += "/" + x
					local_file_dir += "/" + x

			if not os.path.isdir(local_file_dir):
				os.makedirs(local_file_dir)
				
			if not tryDownloadFile(app, remote_file_dir, local_file_dir, file, 'sha256', item[0]):
				app.log.logtask("Couldn't download the metafile: " + file)
				
		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 2: download all packages
		# ------------------------------------------------------------------------------------------------------------------------------
		
		for comp in comps:
			for arch in archs:
				
				# extract content (list of packages) of archives
				if os.path.isfile(dlocal + "/" + comp + "/binary-" + arch + "/Packages.gz"):
					packages_gz = gzip.GzipFile(dlocal + "/" + comp + "/binary-" + arch + "/Packages.gz", "rb")
					packages_content = packages_gz.read()
					packages_gz.close()

					packages = open(dlocal + "/" + comp + "/binary-" + arch + "/Packages", "wb")
					packages.write(packages_content)
					packages.close()

				else:
					app.log.logtask("Can't find local file Packages.gz for " + comps + ":" + arch)
					app.log.logtask(dlocal + "/" + comp + "/binary-" + arch + "/Packages.gz")
					continue

				# read packages file content
				if os.path.isfile(dlocal + "/" + comp + "/binary-" + arch + "/Packages"):
					packages = open(dlocal + "/" + comp + "/binary-" + arch + "/Packages", "r")

					line = packages.readline()

					while line:

						pkg = []
						while line != "\n":
							pkg.append(line)
							line = packages.readline()
						
						deb = Package()

						deb.ID = getnewid()
						deb.repository = repository.ID
						deb.component = comp

						deb.type = "deb"
						deb.release = "none"

						# deb and ubu Packages metadata in the Packages file aren't in the same order !!!
						package_url = ''
						signature = ''
						pkg_name = ''

						for l in pkg:
							if "Package:" in l:
								deb.name = l.replace('Package: ', '').replace('\n', '')
							elif "Architecture:" in l:
								deb.architecture = l.replace('Architecture: ', '').replace('\n', '')
							elif "Version:" in l:
								deb.version = l.replace('Version: ', '').replace('\n', '')
							elif "Description:" in l:
								deb.summary = l.replace('Description: ', '').replace('\n', '')
							elif "Filename:" in l:
								deb.location = re.search('pool\/[\/a-zA-Z0-9-_+*.~]*\.deb', l).group()
								filename = re.search('[a-zA-Z0-9-_+*.~]*\.deb', l).group()
							elif "SHA256:" in l:
								deb.checksum_type = 'sha256'
								deb.checksum =l.replace('SHA256: ', '').replace('\n', '')

						deb_in_db = getpackage(app, deb.repository, deb.component, deb.name, deb.version, deb.architecture, deb.release)
						if deb_in_db:
							dl = False
							# deb in database so we check if the checksum is the same to see if the file changed (unlikely to happen)
							if deb_in_db.checksum != deb.checksum:
								# the file has changed so we add it to the list and we update it in the db
								deb_in_db.checksum_type = deb.checksum_type
								deb_in_db.checksum = deb.checksum
								deb_in_db.summary = deb.summary
								deb_in_db.location = deb.location
								deb_in_db.update(app.database)
								dl = True
							else:
								# need to check if the deb is present, if not we add it to the dl list
								if not os.path.isfile(app.config.rp_folder + "/" + repository.distribution + "/" + deb.location):
									dl = True

							if dl:
								# download the package
								path = deb_in_db.location.split(deb_in_db.name)[0]
								# create directories if needed
								if not os.path.isdir(app.config.rp_folder + "/" + repository.distribution + "/" + path):
									os.makedirs(app.config.rp_folder + "/" + repository.distribution + "/" + path)
								if not tryDownloadFile(app, repository.URL + path, app.config.rp_folder + "/" + repository.distribution + "/" + path, filename, deb_in_db.checksum_type, deb_in_db.checksum):
									app.log.logtask("Couldn't download the RPM: " + deb_in_db.name)
								
						else:
							# deb not in database so we add it and add it to the dl list
							deb.insert(app.database)
							
							# download the package
							path = deb.location.split(deb.name)[0]
							# create directories if needed
							if not os.path.isdir(app.config.rp_folder + "/" + repository.distribution + "/" + path):
								os.makedirs(app.config.rp_folder + "/" + repository.distribution + "/" + path)
							if not tryDownloadFile(app, repository.URL + path, app.config.rp_folder + "/" + repository.distribution + "/" + path, filename, deb.checksum_type, deb.checksum):
								app.log.logtask("Couldn't download the RPM: " + deb.name)

						line = packages.readline()
				
				else:
					app.log.logtask("Can't find local file Packages")
					return False			

			# ------------------------------------------------------------------------------------------------------------------------------
			# Step 3: create the date repository
			# ------------------------------------------------------------------------------------------------------------------------------
			
			daterepo = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
			datedir = app.config.rp_folder + "/" + repository.distribution + "/dists/" + repository.path + "-" + daterepo + "/"
			
			# create the directory
			if not os.path.isdir(datedir):
				os.makedirs(datedir)

			for item in os.listdir(dlocal):
				if os.path.isdir(dlocal + "/" + item):
					shutil.copytree(dlocal + "/" + item, datedir + item)
				else:
					shutil.copy2(dlocal + "/" + item, datedir)

			# save it into the database				
			if not getdaterepository(app, repository.ID, daterepo):
				dr = Daterepository()
				dr.ID = getnewid()
				dr.repository = repository.ID
				dr.date = daterepo
				dr.insert(app.database)
		

	elif repository.type == 'YUM':

		# transform comps and arch into a list
		comps = repository.components.split(',')
		archs = repository.architectures.split(',')	
		
		for comp in comps:
			for arch in archs:

				# display current comp/arch
				app.log.logtask(comp + "/" + arch)

				# set remote root url and local root
				remote = repository.URL + repository.release + "/" + comp + "/" + arch
				local = app.config.rp_folder + "/" + repository.distribution + "/" + repository.release + "/" + comp + "/" + arch

				# check if local root exists, if not create it
				if not os.path.isdir(local):
					os.makedirs(local)

				# ------------------------------------------------------------------------------------------------------------------------------
				# Step 1: downloading metadata files: repodata directory
				# ------------------------------------------------------------------------------------------------------------------------------

				app.log.logtask("Downloading metadata files...")

				# download the repodata directory
				result = getDir_rsync(app, remote + "/repodata/", local + "/repodata/")

				if not result:
					app.log.logtask("RSYNC failed to sync repodata directory for " + comp + "/" + arch + " are you sure this combination of component/architecture exists?")
					return False

				# check if the pgp signature is valid
				# gpg --import RPM-GPG-KEY-CentOS-7
				# gpg --verify repomd.xml.asc repomd.xml

				# ------------------------------------------------------------------------------------------------------------------------------
				# Step 2: download packages and register them in the database if needed
				# ------------------------------------------------------------------------------------------------------------------------------
				
				# package list is in -primary.xml.gz file
				listfile = os.listdir(local + "/repodata/")

				primary = ""
				delta = ""
				
				for file in listfile:
					if re.match(".*-primary.xml.gz", file):
						primary = file
					elif re.match(".*-prestodelta.xml.gz", file):
						delta = file

				# rpms
				app.log.logtask("Checking for new rpms...")
				
				if primary == "":
					app.log.logtask("Can't find primary file (which contains the rpm list).")
					return False
					
				tree = etree.parse(local + "/repodata/" + primary)
				root = tree.getroot()
				for pkg in root.iter('{http://linux.duke.edu/metadata/common}package'):
					
					rpm = Package()

					rpm.ID = getnewid()
					rpm.repository = repository.ID
					rpm.component = comp

					rpm.type = "rpm"

					rpm.name = pkg.findtext('{http://linux.duke.edu/metadata/common}name', default = 'none')
					rpm.architecture = pkg.findtext('{http://linux.duke.edu/metadata/common}arch', default = 'none')

					rpm.version = pkg.find('{http://linux.duke.edu/metadata/common}version').get('ver')
					rpm.release = pkg.find('{http://linux.duke.edu/metadata/common}version').get('rel')

					rpm.location = pkg.find('{http://linux.duke.edu/metadata/common}location').get('href')

					rpm.checksum_type = pkg.find('{http://linux.duke.edu/metadata/common}checksum').get('type')
					rpm.checksum = pkg.findtext('{http://linux.duke.edu/metadata/common}checksum', default = 'none')

					rpm.summary = pkg.findtext('{http://linux.duke.edu/metadata/common}summary', default = 'none')
					
					rpm_in_db = getpackage(app, rpm.repository, rpm.component, rpm.name, rpm.version, rpm.architecture, rpm.release)
					if rpm_in_db:
						dl = False
						# rpm in database so we check if the checksum is the same to see if the file changed (unlikely to happen)
						if rpm_in_db.checksum != rpm.checksum:
							# the file has changed so we add it to the list and we update it in the db
							rpm_in_db.checksum_type = rpm.checksum_type
							rpm_in_db.checksum = rpm.checksum
							rpm_in_db.summary = rpm.summary
							rpm_in_db.location = rpm.location
							rpm_in_db.update(app.database)
							dl = True
						else:
							# need to check if the rpm is present, if not we add it to the dl list
							if not os.path.isfile(local + "/" + rpm_in_db.location):
								dl = True

						if dl:
							# download the package
							path = rpm_in_db.location.split(rpm_in_db.name)[0]
							file = rpm_in_db.name + "-" + rpm_in_db.version + "-" + rpm_in_db.release + "." + rpm_in_db.architecture + "." + rpm_in_db.type  
							if not tryDownloadFile(app, remote + "/" + path, local + "/" + path, file, rpm_in_db.checksum_type, rpm_in_db.checksum):
								app.log.logtask("Couldn't download the RPM: " + rpm_in_db.name)
					else:
						# rpm not in database so we add it and add it to the dl list
						rpm.insert(app.database)
						
						# download the package
						path = rpm.location.split(rpm.name)[0]
						file = rpm.name + "-" + rpm.version + "-" + rpm.release + "." + rpm.architecture + "." + rpm.type 
						if not tryDownloadFile(app, remote + "/" + path, local + "/" + path, file, rpm.checksum_type, rpm.checksum):
							app.log.logtask("Couldn't download the RPM: " + rpm.name)
				
				# ------------------------------------------------------------------------------------------------------------------------------
				# Step 3: create the date repository
				# ------------------------------------------------------------------------------------------------------------------------------
				
				daterepo = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
				datedir = app.config.rp_folder + "/" + repository.distribution + "/" + repository.release + "-" + daterepo + "/" + comp + "/" + arch
				
				# create the directory
				if not os.path.isdir(datedir):
					os.makedirs(datedir)

				# copy directory repodata
				if not os.path.isdir(datedir + "/repodata/"):
					os.makedirs(datedir + "/repodata/")

				for item in os.listdir(local + "/repodata/"):
					shutil.copy2(local + "/repodata/" + item, datedir + "/repodata/")

				# link all other files
				for item in os.listdir(local):
					if item != "repodata":
						if not os.path.exists(datedir + "/" + item):
							os.symlink(local + "/" + item, datedir + "/" + item)

				# save it into the database				
				if not getdaterepository(app, repository.ID, daterepo):
					dr = Daterepository()
					dr.ID = getnewid()
					dr.repository = repository.ID
					dr.date = daterepo
					dr.insert(app.database)
									
		return True
	
	else:
		app.log.logtask("The repository type " + repository.type + " isn't implemented yet.")

	repository.setLastSyncDate()
	repository.update(app.database)

	app.log.logtask("The repository " + repository.name + " is up to date.")

	return True

def sync_channel(app, channel_id):
	return True

	channel = getchannel(app, channel_id)

	if not channel:
		app.log.logtask("Error: no channel with ID: " + channel_id + " in the database.")
		return False

	links = app.database.get_links(channel.ID)

	if not links:
		app.log.logtask("This channel has no repository. So there is nothing to sync.")
		return False

	for repo in links:
		if not sync_repo(app, repo['ID']):
			app.log.logtask("An error occured while trying to sync the repository: " + repo.name)
			return False

	channel.setLastSyncDate()
	channel.update(app.database)

	return True

# --------------------------------------------------------

def check_client(app, client_id):
	return True
	# get client
	client = getclient(app, client_id)

	if not client:
		app.log.logtask("Client with ID: " + client_id + " not found.")
		return False

	app.log.logtask("Check client on " + client.name + "(" + client.IP + ")")

	result = Ansible().ping(client.IP)

	if result:
		app.log.logtask("Ansible can connect to the client.")
		return True
	else:
		app.log.logtask("Ansible can not connect to the client.")
		return False

def config_client(app, client_id):
	return True

	# get client
	client = getclient(app, client_id)

	if not client:
		return False

	app.log.logtask("Generating configuration file for client " + client.name + "(" + client.IP + ")")

	linkedrc = getbinds(app, client.ID)

	if not linkedrc:
		app.log.logtask("No channels or repositories linked to this client.")
		return False

	linkedr = []
	for item in linkedrc:
		if item['type'] == 'c':
			links = app.database.get_links(item['ID'])
			if links:
				for repository in links:
					linkedr.append({'ID': repository['ID']})
		elif item['type'] == 'r':
			linkedr.append({'ID': item['ID']})

	if client.type == 'YUM':

		repo_file = "/var/lib/yarus/yarus.repo"
		config_file = open(repo_file, 'w')
		
		for repository in linkedr:
			repo = getrepo(app, repository['ID'])

			if not repo:
				return False

			if repo.type != client.type:
				app.log.logtask("The repository " + repo.name + " (" + repo.type + ") isn't compatible with the client " + client.name + " (" + client.type + ")")
				continue

			for comp in repo.components.split(","):
				config_file.write("[" + comp + "]\n")
				config_file.write("name=Yarus - " + repo.name + " - " + comp + "\n")
				baseurl = "baseurl=http://155.6.102.161/repos/" + repo.distribution + "/" + repo.release + "/" + comp + "/" + repo.architectures
				config_file.write(baseurl + "\n")
				config_file.write("gpgcheck=1\n")
				config_file.write("gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7\n\n")

		config_file.close()

		ansible = Ansible()
		playbook = ansible.generate_playbook_config_yum_client(client, repo_file)
		if  not playbook:
			return False

		show_playbook(app, playbook)

		if ansible.executeplaybook(playbook):
			os.remove(playbook)
			os.remove(repo_file)
			return True

	elif client.type == 'APT':
		done = []
		repo_file = "/var/lib/yarus/sources.list"
		config_file = open(repo_file, 'w')

		for repository in linkedr:
			if repository['ID'] in done:
				continue
			else:
				done.append(repository['ID'])

			repo = getrepo(app, repository['ID'])

			if not repo:
				return False

			if repo.type != client.type:
				app.log.logtask("The repository " + repo.name + " (" + repo.type + ") isn't compatible with the client " + client.name + " (" + client.type + ")")
				continue

			components = ""

			for comp in repo.components.split(","):
				components += comp + " "

			config_file.write("deb http://155.6.102.161/repos/" + repo.distribution + " " + repo.path + " " + components + "\n")

		config_file.close()

		ansible = Ansible()
		playbook = ansible.generate_playbook_config_apt_client(client, repo_file)
		if  not playbook:
			return False

		show_playbook(app, playbook)

		if ansible.executeplaybook(playbook):
			os.remove(playbook)
			os.remove(repo_file)
			return True

		else:
			app.log.logtask("The repository " + repo.name + "  is not compatible with the client " + client.name)
			return False

	return False

def upgradable_client(app, client_id):
	return True

	# get client
	client = getclient(app, client_id)

	if not client:
		return False

	app.log.logtask("Retrieving the list of upgradable packages for client " + client.name + "(" + client.IP + ")")

	ansible = Ansible()

	if client.type == 'YUM':
		playbook = ansible.generate_playbook_upgradable_yum_client(client)
	elif client.type == 'APT':
		playbook = ansible.generate_playbook_upgradable_apt_client(client)

	if  not playbook:
		return False

	show_playbook(app, playbook)

	response = ansible.executeplaybook(playbook)
	if not response:
		app.log.logtask("No response from Ansible playbook execution.")
		return False

	response = json.loads(response)
	print(response)
	lines = getAnsibleOutput(response, client.IP, 'upgradable')

	if not lines:
		app.log.logtask("Error parsing Ansible response.")
		return False

	if len(lines) <= 0:
		app.log.logtask("No packages need to be updated.")
		return True

	removeupgradables(app, client_id)

	add_upgradable(app, client, lines)

	os.remove(playbook)
	return True

def all_update_client(app, client_id):
	return True
	# get client
	client = getclient(app, client_id)
	if not client:
		app.log.logtask("No client with the ID: " + cliend_id)
		return False

	app.log.logtask("Updating all packages of client " + client.name + " (" + client.IP + ")")

	ansible = Ansible()

	# get list of approved packages
	upgradables = getupgradables(app, client_id)

	# generating package names list
	package_list = []
	for package in upgradables:
		package_list.append(package['name'])

	# if there's not package in the list 
	if len(package_list) == 0:
		app.log.logtask("Client is already up to date.")
		return True

	# generating playbook
	playbook = ansible.generate_playbook_update_client(client, package_list)

	if  not playbook:
		app.log.logtask("Error during the generation of the playbook.")
		return False

	# log the playbook
	show_playbook(app, playbook)

	# execute the playbook
	response = ansible.executeplaybook(playbook)

	if not response:
		app.log.logtask("No response from Ansible playbook execution.")
		return False

	# load the response
	response = json.loads(response)
	
	# check for failure
	if taskFailed(response, client.IP):
		app.log.logtask("Task failed.")
		return False
	
	# update upgradables in the database

	# remove all current upgradables
	removeupgradables(app, client_id)

	# extract new upgradables from the playbook's answer
	lines = getAnsibleOutput(response, client.IP, 'upgradable')

	# add them into the database
	add_upgradable(app, client, lines)
	
	# remove the playbook file
	os.remove(playbook)

	return True

def approved_update_client(app, client_id):
	return True
	# get client
	client = getclient(app, client_id)
	if not client:
		app.log.logtask("No client with the ID: " + cliend_id)
		return False

	app.log.logtask("Updating approved packages of client " + client.name + " (" + client.IP + ")")

	ansible = Ansible()

	# get list of approved packages
	upgradables = getapprovedupgradables(app, client_id)

	# generating package names list
	package_list = []
	for package in upgradables:
		package_list.append(package['name'])

	# if there's not package in the list 
	if len(package_list) == 0:
		app.log.logtask("Client is already up to date.")
		return True

	# generating playbook
	playbook = ansible.generate_playbook_update_client(client, package_list)

	if  not playbook:
		app.log.logtask("Error during the generation of the playbook.")
		return False

	# log the playbook
	show_playbook(app, playbook)

	# execute the playbook
	response = ansible.executeplaybook(playbook)

	if not response:
		app.log.logtask("No response from Ansible playbook execution.")
		return False

	# load the response
	response = json.loads(response)
	
	# check for failure
	if taskFailed(response, client.IP):
		app.log.logtask("Task failed.")
		return False
	
	# update upgradables in the database

	# remove all current upgradables
	removeupgradables(app, client_id)

	# extract new upgradables from the playbook's answer
	lines = getAnsibleOutput(response, client.IP, 'upgradable')

	# add them into the database
	add_upgradable(app, client, lines)
	
	# remove the playbook file
	os.remove(playbook)

	return True

# --------------------------------------------------------

def check_group(app, group_id):
	return True
	# get group
	group = getgroup(app, group_id)

	if not group:
		app.log.logtask("The group with ID: " + group_id + " doesn't exist in the database")
		return False
		
	app.log.logtask("Check group " + group.name + ".")

	groupeds = app.database.get_groupeds(group.ID)
	
	if not groupeds:
		app.log.logtask("No clients found in group " + group.name + ".")
		return False

	ansible = Ansible()

	# generating playbook
	playbook = ansible.generate_playbook_check_group(group, groupeds)

	if  not playbook:
		app.log.logtask("Error during the generation of the playbook.")
		return False

	# log the playbook
	show_playbook(app, playbook)

	# execute the playbook
	response = ansible.executeplaybook(playbook)

	if not response:
		app.log.logtask("No response from Ansible playbook execution.")
		return False

	# load the response
	response = json.loads(response)
	
	# check for failure
	fail = False
	for client in groupeds:
		if taskFailed(response, client['IP']):
			app.log.logtask("Client " + client['name'] + " (" + client['IP'] + "): can't be reach by Ansible.")
			fail = True
		else:
			app.log.logtask("Client " + client['name'] + " (" + client['IP'] + "): OK")

	if fail:
		app.log.logtask("One or more client couldn't be reached.")
		return False

	return True

def config_group(app, group_id):
	return True

def upgradable_group(app, group_id):
	return True

def all_update_group(app, group_id):
	return True

def approved_update_group(app, group_id):
	return True