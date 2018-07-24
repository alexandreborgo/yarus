import os
import sys
import gzip
import re
import json

from yarus.common.repository import Repository
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

def getAnsibleOutput(response, host):
	if 'plays' in response:
		for play in response['plays']:
			if 'tasks' in play:
				for task in play['tasks']:
					if host in task['hosts']:
						return task['hosts'][host]['stdout_lines']

def sync_repo(app, repo_id):

	# check if repo-id is present
	repo = getrepo(app, repo_id)

	if not repo:
		app.log.logtask("Error: no repository with ID: " + repo_id + " in the database.")
		return False

	app.log.logtask("Syncing repository " + repo.name)

	if repo.type == 'APT':

		# declare variables with better names
		repo_id = repo.ID
		root_url = repo.URL
		dist = repo.repository
		comps = repo.components
		archs = repo.architectures
		repo_type = repo.type
		last_sync = repo.last_sync

		# transform comps and arch into a list
		comps = repo.components.split(',')
		archs = repo.architectures.split(',')

		# repos folder
		repo_folder = app.config.rp_folder

		# root path of the remote mirror
		root_remote = repo.URL
		# root path of the local mirror
		root_local = repo_folder + "/" + repo.repository
		# pool path of the local mirror
		pool = root_local + "/pool"

		# url of the distribution folder
		dist_remote = root_remote + "dists/" + repo.release
		# distribution path of the local mirror
		dist_local = root_local + "/dists/" + repo.release

		# architectures path of the local mirror
		arch_local = []
		for comp in comps:
			for arch in archs:
				arch_dir = dist_local + "/" + comp + "/binary-" + arch
				arch_local.append(arch_dir)

				if not os.path.isdir(arch_dir):
					os.makedirs(arch_dir)

		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 1: downloading metadata files: Release, Release.gpg and InRelease
		# ------------------------------------------------------------------------------------------------------------------------------

		# first we're looking for Release and Release.gpg
		# if we don't find them then we're looking for InRelease
		# and finally if we don't find it we stop the script
		# because we don't have metadata file to keep going
		app.log.logtask("Syncing: metadata files.")
		app.log.logtask("")

		release = getFile_rsync(dist_remote, dist_local, "Release")
		releasegpg = getFile_rsync(dist_remote, dist_local, "Release.gpg")

		if release and releasegpg:
			app.log.logtask("Release and Release.gpg found.")
		else:
			inrelease = getFile_rsync(dist_remote, dist_local, "InRelease")

			if inrelease:
				app.log.logtask("InRelease find")
			else:
				app.log.logtask("Can't find InRelease or Release file, the script can't keep going without one of these files")
				return False

		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 2: check metadata files' signatures
		# ------------------------------------------------------------------------------------------------------------------------------

		# TODO

		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 3: from the release file we extract the lines of files we're interested in (regarding comps and archs)
		# ------------------------------------------------------------------------------------------------------------------------------

		try:
			release_f = open(release, "r")
		except FileNotFoundError as error:
			app.log.logtask("Can't open local Release file")
			app.log.logtask(error)
			return False

		# we don't need the "header" of the file
		# so go to next line until we see sha256
		# after this line we have the content we need
		line = release_f.readline()
		while "SHA256:" not in line:
			line = release_f.readline()

		# we keep sha256 line
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
			app.log.logtask("No file corresponding the components '" + repo.components + "' and architectures '" + repo.architectures + "'")
			return True

		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 4: downloading more metedata files and checking their signatures
		# ------------------------------------------------------------------------------------------------------------------------------

		# downloading the files
		for item in file_line:

			file = item[2].split("/")[-1]
			remote_file_dir = dist_remote
			local_file_dir = dist_local

			for x in item[2].split("/"):
				if x not in file:
					remote_file_dir += "/" + x
					local_file_dir += "/" + x

			if not os.path.isdir(local_file_dir):
				os.makedirs(local_file_dir)

			# check if we already have the latest version
			# by comparing the signature of the local file and the signature in the Release file
			if checkingSignature(local_file_dir + "/" + file, item[0]):
				continue

			if not tryDownloadFile(remote_file_dir, local_file_dir, file, item[0]):
				app.log.logtask("Couldn't download the metafile: " + file)

		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 6: extract compressed packages file
		# ------------------------------------------------------------------------------------------------------------------------------

		for arch in arch_local:
			if os.path.isfile(arch + "/Packages.gz"):
				packages_gz = gzip.GzipFile(arch + "/Packages.gz", "rb")
				packages_content = packages_gz.read()
				packages_gz.close()

				packages = open(arch + "/Packages", "wb")
				packages.write(packages_content)
				packages.close()

			else:
				app.log.logtask("Can't find local file Packages.gz for architecture: " + arch)
				app.log.logtask(arch + "/Packages.gz")
				return False

		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 7: downloading .deb
		# ------------------------------------------------------------------------------------------------------------------------------

		for arch in arch_local:

			app.log.logtask("")
			app.log.logtask("Syncing: " + arch)
			app.log.logtask("")

			# read packages file content
			if os.path.isfile(arch + "/Packages"):
				packages = open(arch + "/Packages", "r")

				line = packages.readline()

				while line:
					pkg = []
					while line != "\n":
						pkg.append(line)
						line = packages.readline()

					# deb and ubu Packages metadata in the Packages file aren't in the same order !!!
					package_url = ''
					signature = ''
					pkg_name = ''

					for l in pkg:
						if "Filename:" in l:
							pkg_url = re.search('pool\/[\/a-zA-Z0-9-_+*.~]*\.deb', l).group()
							pkg_name = re.search('[a-zA-Z0-9-_+*.~]*\.deb', l).group()
						elif "SHA256:" in l:
							signature = l.replace('SHA256: ', '').replace('\n', '')

					# check if we already have the latest version
					# by comparing the signature of the local file and the signature in the Release file
					if checkingSignature(root_local + "/" + pkg_url, signature):
						# we read the next line and continue to the next package
						line = packages.readline()
						continue
					else:
						if not tryDownloadPkg(root_remote, root_local, pkg_url, pkg_name, signature):
							app.log.logtask("Couldn't download the package: " + pkg_name)
						line = packages.readline()

			else:
				app.log.logtask("Can't find local file Packages")
				return False

	elif repo.type == 'YUM':

		# we're going for a simple rsync of the arch file
		# and check the signature of all file ofc !

		# transform comps and arch into a list
		comps = repo.components.split(',')
		archs = repo.architectures.split(',')

		for comp in comps:
			for arch in archs:
				url = repo.URL + repo.release + "/" + comp + "/" + arch
				repos = app.config.rp_folder

				path = repos + "/" + repo.repository + "/" + repo.release + "/" + comp

				# we create the dir if he isn't already present
				# we don't put arch in the path because rsync will create it
				# if we put arch in the path we will end ip with os_name/dist/comp/arch/arch/
				if not os.path.isdir(path):
					os.makedirs(path)

				app.log.logtask("Syncing: " + comp + "/" + arch)

				# starting sync
				result = getDir_rsync(url, path)

				if result != 0:
					app.log.logtask("Error while trying to sync the repository, RSYNC failled to download the whole repository or a part.")
					app.log.logtask(str(result))
					return False

	else:
		app.log.logtask("The repository type " + repo.type + " isn't implemented yet.")

	repo.setLastSyncDate()
	repo.update(app.database)

	return True

def sync_channel(app, channel_id):

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

def check_client(app, client_id):
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
		print(linkedr)
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
				baseurl = "baseurl=http://155.6.102.161/repos/" + repo.repository + "/" + repo.release + "/" + comp + "/" + repo.architectures
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

			config_file.write("deb http://155.6.102.161/repos/" + repo.repository + " " + repo.release + " " + components + "\n")

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
	lines = getAnsibleOutput(response, client.IP)

	if len(lines) <= 0:
		app.log.logtask("No packages need to be updated.")
		return True

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
			if getupgradablebyinfo(app, client_id, name, release, type):
				continue
			upgradable = Upgradable(name=name, release=release, type=type, ID=package_id, client_id=client_id, approved=0)
			upgradable.insert(app.database)

	elif client.type == 'APT':
		# first lines is useless
		lines.pop(0)

		for line in lines:
			l = line.split(" ")
			name, type = l[0].split('/')
			release = l[1]
			package_id = getnewid()
			if getupgradablebyinfo(app, client_id, name, release, type):
				continue
			upgradable = Upgradable(name=name, release=release, type=type, ID=package_id, client_id=client_id, approved=0)
			upgradable.insert(app.database)

	os.remove(playbook)
	return True

	return False

def approved_update_client(app, client_id):
	return False

def all_update_client(app, client_id):
	# get client
	client = getclient(app, client_id)

	if not client:
		return False

	app.log.logtask("Updating all package of client " + client.name + " (" + client.IP + ")")

	ansible = Ansible()

	upgradables = getupgradables(app, client_id)

	package_list = []

	for package in upgradables:
		package_list.append(package['name'])

	if client.type == 'YUM':
		playbook = ansible.generate_playbook_all_update_yum_client(client, package_list)
	elif client.type == 'APT':
		playbook = ansible.generate_playbook_all_update_apt_client(client, package_list)

	if  not playbook:
		app.log.logtask("Error during the generation of the playbook.")
		return False

	show_playbook(app, playbook)

	response = ansible.executeplaybook(playbook)

	if not response:
		app.log.logtask("No response from Ansible playbook execution.")
		return False

	response = json.loads(response)
	app.log.logtask(response)

	os.remove(playbook)
	return True

	return False
