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
from yarus.common.update import Update
from yarus.common.upgraded import Upgraded
from yarus.common.functions import *
from yarus.common.exceptions import *
from yarus.common.upgradable import Upgradable
from yarus.tasksmanager.ansible import Ansible
from yarus.tasksmanager.functions import *

# --------------------------------------------------------

def getAnsibleOutput(response, host, taskname):
	if 'plays' in response:
		for play in response['plays']:
			if 'tasks' in play:
				for task in play['tasks']:
					if task['task']['name'] == taskname:
						if host in task['hosts']:
							if 'stdout_lines' in task['hosts'][host]:
								return task['hosts'][host]['stdout_lines']
							elif 'results' in task['hosts'][host]:
								for result in task['hosts'][host]['results']:
									if 'results' in result:
										return result['results']
									elif 'stdout_lines' in result:
										return result['stdout_lines']

def getAnsibleGroupOutput(response, hosts, taskname):
	out = []
	if 'plays' in response:
		for play in response['plays']:
			if 'tasks' in play:
				for task in play['tasks']:
					if task['task']['name'] == taskname:
						for host in hosts:
							if host['IP'] in task['hosts']:
								tmp = {}
								tmp['host'] = host
								tmp['lines'] = ""
								if 'stdout_lines' in task['hosts'][host['IP']]:
									tmp['lines'] = task['hosts'][host['IP']]['stdout_lines']
								elif 'results' in task['hosts'][host['IP']]:
									for result in task['hosts'][host['IP']]['results']:
										if 'results' in result:
											tmp['lines'] = result['results']
										elif 'stdout_lines' in result:
											tmp['lines'] = result['stdout_lines']
								out.append(tmp)
	return out
	
def getAnsibleError(response, host, taskname):
	if 'plays' in response:
		for play in response['plays']:
			if 'tasks' in play:
				for task in play['tasks']:
					if task['task']['name'] == taskname:
						if host in task['hosts']:
							if 'results' in task['hosts'][host]:					
								for result in task['hosts'][host]['results']:
									if 'msg' in result:
										return result['msg']
							elif 'msg' in task['hosts'][host]:
								return task['hosts'][host]['msg']

def failure(response, host):
	if 'stats' in response:
		if host in response['stats']:
			if response['stats'][host]['failures'] > 0:
				return True
			elif response['stats'][host]['unreachable'] > 0:
				return True
			else:
				return False
	return True

def printfailure(app, response, host, taskname):
	if 'plays' in response:
		for play in response['plays']:
			if 'tasks' in play:
				for task in play['tasks']:
					if task['task']['name'] == taskname:
						if host in task['hosts']:
							if 'module_stderr' in task['hosts'][host] and 'module_stdout' in task['hosts'][host]:
								app.log.logtask(task['hosts'][host]['module_stderr'])
								app.log.logtask(task['hosts'][host]['module_stdout'])

def success(response, host):
	if 'stats' in response:
		if host in response['stats']:
			if response['stats'][host]['ok'] == 1:
				return True
			else:
				return False
	return True

def parse_upgradable(app, client, lines):
	if len(lines) <= 0:
		app.log.logtask("No packages need to be updated.")
		return True
	
	list_upgradable = []

	if client.type == 'YUM':
		# first lines is useless
		lines.pop(0)

		residuals = []
		for line in lines:
			# first we get all the information in an array
			l = line.split(" ")
			l = list(filter(lambda a: a != '', l))
			upg = {}
			if len(l) == 3:
				upg['name'], upg['arch'] = l[0].split(".")
				upg['version'], upg['release'] = l[1].split("-")
				upg['version'] = upg['version'].split(":")[-1]
				upg['component'] = l[2]
				upg['upgradable_id'] = getnewid()
				list_upgradable.append(upg)
			else:
				residuals.append(l)
		
		app.log.logtask("Line that couldn't be parsed:")
		for resid in residuals:
			app.log.logtask(resid)

	elif client.type == 'APT':
		# first lines is useless
		lines.pop(0)

		for line in lines:
			l = line.split(" ")
			upg = {}
			upg['name'], uselesstmpvar = l[0].split('/')
			upg['version'] = l[1]
			upg['arch'] = l[2]
			upg['component'] = 'unknown'
			upg['release'] = 'none'
			upg['upgradable_id'] = getnewid()
			list_upgradable.append(upg)

	return list_upgradable

def parse_group_upgradable(app, glines):
	list_upgradable = []
	for lines in glines:
		app.log.logtask(lines['host']['name'])
		app.log.logtask(lines)
		if len(lines['lines']) <= 0:
			continue

		if lines['host']['type'] == 'YUM':
			# first lines is useless
			lines['lines'].pop(0)

			residuals = []
			for line in lines['lines']:
				# first we get all the information in an array
				l = line.split(" ")
				l = list(filter(lambda a: a != '', l))
				upg = {}
				if len(l) == 3:
					upg['name'], upg['arch'] = l[0].split(".")
					upg['version'], upg['release'] = l[1].split("-")
					upg['version'] = upg['version'].split(":")[-1]
					upg['component'] = l[2]
					upg['upgradable_id'] = getnewid()
					list_upgradable.append(upg)
				else:
					residuals.append(l)
			
			app.log.logtask("Line that couldn't be parsed:")
			for resid in residuals:
				app.log.logtask(resid)

		elif lines['host']['type'] == 'APT':
			# first lines is useless
			lines['lines'].pop(0)

			for line in lines['lines']:
				l = line.split(" ")
				upg = {}
				upg['name'], uselesstmpvar = l[0].split('/')
				upg['version'] = l[1]
				upg['arch'] = l[2]
				upg['component'] = 'unknown'
				upg['release'] = 'none'
				upg['upgradable_id'] = getnewid()
				list_upgradable.append(upg)

	return list_upgradable

def ansibleparseresponse(app, response):
	try:
		response_lines = response.split('{', 1)[-1]
		response_lines = "{\n" + response_lines

		app.log.logtask("Ansible output:")
		app.log.logtask(response_lines)
		
		response = json.loads(response_lines)

		return response

	except json.decoder.JSONDecodeError as error:
		app.log.logtask("Couldn't parse Ansible output.")
		app.log.logtask(error)
		return None

def generatingconfigfile(app, client):
	links = getbinds(app, client.ID)
	if not links:
		app.log.logtask("The system " + client.name + " isn't linked with any repository or channel.")
		return None

	# list of repositories linked
	linked_repositories = []
	# we add all repository inside, including repositories inside linked channels
	for item in links:
		if item['type'] == 'c':
			tmp_links = getlinks(app, item['ID'])
			if tmp_links:
				for repository in tmp_links:
					linked_repositories.append(repository['ID'])
					app.log.logtask("repository: " + repository['ID'] + " is linked (inside a channel).")
		elif item['type'] == 'r':
			app.log.logtask("repository: " + item['ID'] + " is linked.")
			linked_repositories.append(item['ID'])

	done = []
	if client.type == 'YUM':
		repo_file = "/opt/yarus/tmp/yarus_" + client.IP + ".repo"
	elif client.type == 'APT':
		repo_file = "/opt/yarus/tmp/sources_" + client.IP + ".list"
	config_file = open(repo_file, 'w')
	
	for repo_id in linked_repositories:

		# check if repo isn't duplicate
		if repo_id in done:
			continue
		else:
			done.append(repo_id)

		# check if repository exist
		repository = getobject(app, 'repository', repo_id)        
		if not repository:
			app.log.logtask("The repository with ID " + repo_id + " doesn't exist.")
			return None

		if repository.type != client.type:
			app.log.logtask("The repository " + repository.name + " (" + repository.type + ") isn't compatible with the client " + client.name + " (" + client.type + ").")
			continue
		
		# check for repository with good arch for the client
		archs = repository.architectures.split(',')
		arch_comp = False
		for arch in archs:
			if arch == client.architecture:
				arch_comp = True
		if not arch_comp:
			app.log.logtask("The repository " + repository.name + " (" + str(repository.architectures) + ") isn't compatible with the client " + client.name + " (" + client.architecture + ").")
			continue

		if client.type == 'YUM':			
			repo_dir_name = repository.name.replace(' ', '_').replace('/', '_').lower()
			repo_version = repository.release
			repo_major = repository.release.split('.')[0]
			config_file.write("[" + repo_dir_name + "]\n")
			config_file.write("name=Yarus - " + repository.name + "\n")
			baseurl = "baseurl=http://" + app.config.sv_address + "/yum/" + repository.distribution + "/" + repo_major + "/" + repo_version + "/" + repo_dir_name + "/"
			config_file.write(baseurl + "\n")
			config_file.write("gpgcheck=0\n")
			#config_file.write("gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7\n\n")
			
		elif client.type == 'APT':
			components = ""
			for comp in repository.components.split(","):
				components += comp + " "
			config_file.write("deb http://" + app.config.sv_address + "/apt/" + repository.distribution + " " + repository.path + " " + components + "\n")		

	config_file.close()
	return repo_file

# --------------------------------------------------------

def sync_repo(app, task, repo_id):
	
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

		rlocal = app.config.rp_folder  + "/apt/" +  repository.distribution + "/"
		dlocal = app.config.rp_folder  + "/apt/" +  repository.distribution + "/dists/" + repository.path + "/"
		
		rremote = repository.URL
		dremote = repository.URL + "dists/" + repository.path + "/"

		app.log.logtask("Repo URL: " + rremote)
		app.log.logtask("Repo dist URL: " + dremote)
		app.log.logtask("Root local: " + rlocal)
		app.log.logtask("Dist local: " + dlocal)

		# check if local exists, if not create it
		if not os.path.isdir(dlocal):
			os.makedirs(dlocal)
		 
		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 1: downloading metadata files
		# ------------------------------------------------------------------------------------------------------------------------------

		# calculate metadata file signature
		release_sig = ""
		if os.path.isfile(dlocal + "/Release"):
			release_sig = getSigFile(dlocal + "/Release")

		app.log.logtask("Downloading metadata files...")

		release = getFile_rsync(app, dremote, dlocal, "Release")
		releasegpg = getFile_rsync(app, dremote, dlocal, "Release.gpg")
		inrelease = getFile_rsync(app, dremote, dlocal, "InRelease")

		if release and releasegpg:
			metafile = "release"
		else:
			if inrelease:
				metafile = "inrelease"
			else:
				app.log.logtask("Unable to find metadata files on the remote repository.")
				return False

		# calculate the new signature of the metadata files
		if os.path.isfile(dlocal + "/Release"):
			new_release_sig = getSigFile(dlocal + "/Release")

		# check if it is the same or not
		if release_sig == new_release_sig:
			app.log.logtask("The repository " + repository.name + " is already up to date.")
			return True

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
			app.log.logtask("No packages corresponding the components " + repository.components + " and architectures " + repository.architectures + ".")
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

				app.log.logtask("")
				app.log.logtask("")
				app.log.logtask(comp + "/" + arch)
				app.log.logtask("")
				
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
								if not os.path.isfile(rlocal + deb.location):
									dl = True

							if dl:
								# download the package
								path = ""
								for x in deb_in_db.location.split("/"):
									if x != deb_in_db.location.split("/")[-1]:
										path += x + "/"
								# create directories if needed
								if not os.path.isdir(rlocal + path):
									os.makedirs(rlocal + path)
								if not tryDownloadFile(app, rremote + path, rlocal + path, filename, deb_in_db.checksum_type, deb_in_db.checksum):
									app.log.logtask("Couldn't download the RPM: " + deb_in_db.name)
								
						else:
							# deb not in database so we add it and add it to the dl list
							deb.insert(app.database)
							
							# download the package
							path = ""
							for x in deb.location.split("/"):
								if x != deb.location.split("/")[-1]:
									path += x + "/"
							# create directories if needed
							if not os.path.isdir(rlocal + path):
								os.makedirs(rlocal + path)
							if not tryDownloadFile(app, rremote + path, rlocal + path, filename, deb.checksum_type, deb.checksum):
								app.log.logtask("Couldn't download the RPM: " + deb.name)

						line = packages.readline()
				
				else:
					app.log.logtask("Can't find local file Packages")
					return False			
			
			# ------------------------------------------------------------------------------------------------------------------------------
			# Step 3: create the date repository
			# ------------------------------------------------------------------------------------------------------------------------------
			
			daterepo = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
			datedir = rlocal + "dists/" + repository.path + "-" + daterepo + "/"
			
			app.log.logtask("Creating date repo " + datedir + ".")

			# create the directory
			if not os.path.isdir(datedir):
				os.makedirs(datedir)

			for item in os.listdir(dlocal):
				if not os.path.exists(datedir + item):
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

		# this variable is here to check if there's something new in the repository
		# we will use it to determine if we need to create a dateversion repository or not
		new = False

		# set remote root url and local root
		remote = repository.URL

		repo_dir_name = repository.name.replace(' ', '_').replace('/', '_').lower()
		if repo_dir_name[0] == '.':
			repo_dir_name = repo_dir_name[1:]

		repo_version = repository.release
		repo_major = repository.release.split('.')[0]

		local = app.config.rp_folder + "/yum/" + repository.distribution + "/" + repo_major + "/" + repo_version + "/" + repo_dir_name + "/"

		app.log.logtask("Release: " + repo_version + ' ' + repo_major)
		app.log.logtask("Remote root URL: " + remote)
		app.log.logtask("Local root directory: " + local)

		# check if local root exists, if not create it
		if not os.path.isdir(local):
			os.makedirs(local)
		
		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 1: downloading metadata files: repodata directory
		# ------------------------------------------------------------------------------------------------------------------------------

		# calculate repomd.xml signature
		repomd_sig = ""
		if os.path.isfile(local + "repodata/repomd.xml"):
			repomd_sig = getSigFile(local + "repodata/repomd.xml")

		app.log.logtask("Downloading metadata files...")

		# download the repodata directory
		result = getDir_rsync(app, remote + "repodata/", local + "repodata/")

		if not result:
			app.log.logtask("RSYNC failed to sync repodata directory.")
			return False

		# check if the pgp signature is valid
		# gpg --import RPM-GPG-KEY-CentOS-7
		# gpg --verify repomd.xml.asc repomd.xml

		# calculate the new signature of the file repomd.xml
		if os.path.isfile(local + "repodata/repomd.xml"):
			new_repomd_sig = getSigFile(local + "repodata/repomd.xml")

		# check if it is the same or not
		if repomd_sig == new_repomd_sig:
			app.log.logtask("The repository " + repository.name + " is already up to date.")
			return True

		new = True
		
		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 2: download packages and register them in the database if needed
		# ------------------------------------------------------------------------------------------------------------------------------
		
		# package list is in -primary.xml.gz file		
		mdtree = etree.parse(local + "repodata/repomd.xml")
		root = mdtree.getroot()

		primary = ""
		for pkg in root.iter('{http://linux.duke.edu/metadata/repo}data'):
			if pkg.get('type') == 'primary':
				primary = pkg.find('{http://linux.duke.edu/metadata/repo}location').get('href')
				break

		if not primary:
			app.log.logtask("No primary file could be find (primary is the file where YARUS check the list of packages).")
			return False

		# rpms
		app.log.logtask("Checking rpms...")
				
		tree = etree.parse(local + primary)
		root = tree.getroot()
		app.log.logtask("Parsing primary file over.")
		
		for pkg in root.iter('{http://linux.duke.edu/metadata/common}package'):
			rpm = Package()

			rpm.ID = getnewid()
			rpm.repository = repository.ID
			rpm.component = ""

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
					app.log.logtask("Old RPM found changed: " + rpm_in_db.name)
					dl = True
				else:
					# need to check if the rpm is present, if not we add it to the dl list
					if not os.path.isfile(local + rpm_in_db.location):
						app.log.logtask("Old RPM found but not present on the disk: " + rpm_in_db.name)
						dl = True

				if dl:
					# download the package
					path = rpm_in_db.location.split(rpm_in_db.name)[0]
					file = rpm_in_db.name + "-" + rpm_in_db.version + "-" + rpm_in_db.release + "." + rpm_in_db.architecture + "." + rpm_in_db.type  
					if not tryDownloadFile(app, remote + path, local + path, file, rpm_in_db.checksum_type, rpm_in_db.checksum):
						app.log.logtask("Couldn't download the RPM: " + rpm_in_db.name)
			else:
				app.log.logtask("New RPM found: " + rpm.name)
				# rpm not in database so we add it and add it to the dl list
				rpm.insert(app.database)
				
				# download the package
				path = rpm.location.split(rpm.name)[0]
				file = rpm.name + "-" + rpm.version + "-" + rpm.release + "." + rpm.architecture + "." + rpm.type 
				if not tryDownloadFile(app, remote + path, local + path, file, rpm.checksum_type, rpm.checksum):
					app.log.logtask("Couldn't download the RPM: " + rpm.name)
	
		# ------------------------------------------------------------------------------------------------------------------------------
		# Step 3: create the date repository
		# ------------------------------------------------------------------------------------------------------------------------------

		if new:
			daterepo = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
			datedir = local[:-1] + "-" + daterepo + "/"		

			# create the directory
			if not os.path.isdir(datedir):
				os.makedirs(datedir)

			# copy directory repodata
			if not os.path.isdir(datedir + "repodata/"):
				os.makedirs(datedir + "repodata/")

			for item in os.listdir(local + "repodata/"):
				shutil.copy2(local + "repodata/" + item, datedir + "repodata/")

			# link all other files
			if os.path.isdir(local):
				for item in os.listdir(local):
					if item != "repodata":
						if not os.path.exists(datedir + item):
							os.symlink(local + item, datedir + item)

			# save it into the database				
			if not getdaterepository(app, repository.ID, daterepo):
				dr = Daterepository()
				dr.ID = getnewid()
				dr.repository = repository.ID
				dr.date = daterepo
				dr.insert(app.database)
	
	else:
		app.log.logtask("The repository type " + repository.type + " isn't implemented yet.")

	repository.setLastSyncDate()
	repository.update(app.database)

	app.log.logtask("The repository " + repository.name + " is up to date.")

	return True

def sync_channel(app, task, channel_id):

	# check for the channel
	channel = getobject(app, 'channel', channel_id)
	if not channel:
		app.log.logtask("No channel found with the given ID (" + rc_id + ").")
		return False

	# check for links
	links = getlinks(app, channel_id)
	if not links:
		app.log.logtask("This channel has no repository. So there is nothing to sync.")
		return False

	# start repository sync for each repository
	for repository in links:
		if not sync_repo(app, task, repository['ID']):
			app.log.logtask("An error occured while trying to sync the repository: " + repository.name)

	channel.setLastSyncDate()
	channel.update(app.database)

	return True

# --------------------------------------------------------

def check_client(app, task, client_id):
	
	# check if client exists
	client = getobject(app, 'client', client_id)        
	if not client:
		app.log.logtask("Error: no system with ID: " + client_id + " in the database.")
		return False

	app.log.logtask("Ansible will check connection with the system " + client.name + "(" + client.IP + ").")
	
	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_check_client(task.ID, client)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		ansible.clean()
	except IOError as error:
		app.log.logtask(error)
		return False

	response = ansibleparseresponse(app, result)

	if failure(response, client.IP):
		app.log.logtask("Ansible can not connect to the client!")
		app.log.logtask(getAnsibleError(response, client.IP, 'check'))
		return False

	app.log.logtask("Ansible can connect to the client.")
	return True

def config_client(app, task, client_id):
	#repo_version = repository.release
	#repo_major = repository.release.split('.')[0]
	#local = app.config.rp_folder + "/yum/" + repository.distribution + "/" + repo_major + "/" + repo_version + "/" + repo_dir_name + "/"
	
	# check if client exists
	client = getobject(app, 'client', client_id)        
	if not client:
		app.log.logtask("Error: no system with ID: " + client_id + " in the database.")
		return False

	app.log.logtask("Generating configuration file for client " + client.name + "(" + client.IP + ")")

	repo_file = generatingconfigfile(app, client)
	with open(repo_file) as rfile:
		for line in rfile:
			app.log.logtask(line.strip("\n"))

	if not repo_file:
		app.log.logtask("Error during the generation of the repository file.")
		return False

	app.log.logtask("Ansible will check connection with the system " + client.name + "(" + client.IP + ").")
	
	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_config_client(task.ID, client, repo_file)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		ansible.clean()
		os.remove(repo_file)
	except IOError as error:
		app.log.logtask(error)
		return False

	response = ansibleparseresponse(app, result)

	if failure(response, client.IP):
		app.log.logtask("The client could not be configured.")
		app.log.logtask(getAnsibleError(response, client.IP, 'config'))
		return False

	app.log.logtask("The client is configured with the linked repositories.")
	return True

def upgradable_client(app, task, client_id):
	# check if client exists
	client = getobject(app, 'client', client_id)        
	if not client:
		app.log.logtask("Error: no system with ID: " + client_id + " in the database.")
		return False

	app.log.logtask("Retrieving the list of upgradable packages for client " + client.name + "(" + client.IP + ").")
	
	# config
	config_client(app, task, client_id)

	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_upgradable_client(task.ID, client)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		ansible.clean()
	except IOError as error:
		app.log.logtask(error)
		return False

	response = ansibleparseresponse(app, result)

	if failure(response, client.IP):
		app.log.logtask("The list of upgradable packages could not be retrieved.")
		app.log.logtask(getAnsibleError(response, client.IP, 'upgradable'))
		return False

	# first remove all upgradable linked to the client
	app.database.remove_upgradables(client.ID, 'client')

	lines = getAnsibleOutput(response, client.IP, 'upgradable')

	if not lines:
		app.log.logtask("No package to update.")
		return True

	app.log.logtask("Output:")
	for line in lines:
		app.log.logtask(line)

	list_upgradable = parse_upgradable(app, client, lines)

	for upg in list_upgradable:

		# get the package from the db
		pkg = getpackagebyinfo(app, upg['name'], upg['arch'], upg['version'], upg['release'])
		if not pkg:
			#app.log.logtask("ERROR: the package " + upg['name'] + "-" + upg['version'] + "-" + upg['release'] + " doesn't come from a repository handled by YARUS.")
			continue

		# check if this upgradable is already register
		if getupgradablebyinfo(app, 'client', client.ID, pkg.ID):
			continue

		upgradable = Upgradable(object_id=client.ID, object_type="client", approved=0, ID=upg['upgradable_id'], package_id=pkg.ID)
		upgradable.insert(app.database)

	app.log.logtask("The list of upgradable packages has been retrieved.")
	return True

def approved_update_client(app, task, client_id):
	
	# check if client exists
	client = getobject(app, 'client', client_id)        
	if not client:
		app.log.logtask("Error: no system with ID: " + client_id + " in the database.")
		return False

	app.log.logtask("Updating approved packages of client " + client.name + " (" + client.IP + ")")

	# get list of approved packages
	upgradables = app.database.get_approved_upgradables(client_id, 'client')

	# generating package names list which will be gave to ansible
	package_list = []
	for package in upgradables:
		package_list.append(package['name'])

	# if there's not package in the list 
	if not package_list:
		app.log.logtask("The system " + client.name + " is already up to date.")
		return True
	
	# config
	config_client(app, task, client_id)

	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_update_client(task.ID, client, package_list)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		ansible.clean()
	except IOError as error:
		app.log.logtask(error)
		return False

	response = ansibleparseresponse(app, result)
	
	if failure(response, client.IP):
		app.log.logtask("Ansible could not run the update.")
		app.log.logtask(getAnsibleError(response, client.IP, 'upgrade'))
		return False

	# display output
	result = getAnsibleOutput(response, client.IP, 'upgrade')
	app.log.logtask("Output:")
	for line in result:
		app.log.logtask(line)

	# register the update into the system
	update = Update(client.ID, 'client', int(datetime.datetime.now().timestamp()), getnewid())
	update.insert(app.database)

	# insert all package that have been updated
	for package in upgradables:
		upgraded = Upgraded(package['ID'], update.ID)
		upgraded.insert(app.database)

	upgradable_client(app, task, client_id)

	app.log.logtask("Approved packages have been updated.")	
	return True

def all_update_client(app, task, client_id):
	
	# check if client exists
	client = getobject(app, 'client', client_id)        
	if not client:
		app.log.logtask("Error: no system with ID: " + client_id + " in the database.")
		return False

	app.log.logtask("Updating all packages of client " + client.name + " (" + client.IP + ")")

	# get list of all packages
	upgradables = app.database.get_upgradables(client.ID, 'client')

	# generating package names list which will be gave to ansible
	package_list = []
	for package in upgradables:
		package_list.append(package['name'])

	# if there's not package in the list 
	if not package_list:
		app.log.logtask("The system " + client.name + " is already up to date.")
		return True
	
	# config
	config_client(app, task, client_id)

	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_update_all_client(task.ID, client)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		#ansible.clean()
	except IOError as error:
		app.log.logtask(error)
		return False

	response = ansibleparseresponse(app, result)
	
	if failure(response, client.IP):
		app.log.logtask("Ansible could not update all package.")
		app.log.logtask(getAnsibleError(response, client.IP, 'upgrade'))
		return False

	# display output
	result = getAnsibleOutput(response, client.IP, 'upgrade')
	if result:
		app.log.logtask("Output:")
		for line in result:
			app.log.logtask(line)

	# register the update into the system
	update = Update(client.ID, 'client', int(datetime.datetime.now().timestamp()), getnewid())
	update.insert(app.database)

	# insert all package that have been updated
	for package in upgradables:
		upgraded = Upgraded(package['package_id'], update.ID)
		upgraded.insert(app.database)

	# update the database (delete all upgradables that are up to date now)
	app.database.remove_upgradables(client.ID, 'client')

	return True

# --------------------------------------------------------

def check_group(app, task, group_id):
	# check if group exists
	group = getobject(app, 'group', group_id)        
	if not group:
		app.log.logtask("Error: no group with ID: " + group_id + " in the database.")
		return False
		
	app.log.logtask("Ansible will check connection with all systems in the group " + group.name + ".")

	groupeds = app.database.get_groupeds(group.ID)
	
	if not groupeds:
		app.log.logtask("No system found in the group " + group.name + ".")
		return False

	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_check_group(task.ID, group, groupeds)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		ansible.clean()
	except IOError as error:
		app.log.logtask(error)

	response = ansibleparseresponse(app, result)
	
	# check for failure for each client
	fail = False
	for client in groupeds:
		if not success(response, client['IP']):
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): can not be reached by Ansible.")
			fail = True
		else:
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): OK")

	if fail:
		app.log.logtask("One or more system couldn't be reached.")
		return False

	return True

def config_group(app, task, group_id):
	# check if group exists
	group = getobject(app, 'group', group_id)        
	if not group:
		app.log.logtask("Error: no group with ID: " + group_id + " in the database.")
		return False

	app.log.logtask("Generating configuration file for all the systems in the group " + group.name + ".")
	
	groupeds = app.database.get_groupeds(group.ID)
	if not groupeds:
		app.log.logtask("No system found in the group " + group.name + ".")
		return False

	client_list = []
	for client in groupeds:
		# check if client exists
		cl = getobject(app, 'client', client['ID'])        
		if not cl:
			app.log.logtask("Error: no system with ID: " + cl['ID'] + " in the database.")
			return False
		app.log.logtask("Client " + cl.name + ": ")
		tmp = {}
		tmp['client'] = cl
		tmp['repo_file'] = generatingconfigfile(app, cl)
		client_list.append(tmp)
		app.log.logtask(tmp)

	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_config_group(task.ID, group, client_list)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		ansible.clean()
	except IOError as error:
		app.log.logtask(error)
		return False

	response = ansibleparseresponse(app, result)

	# check for failure for each client
	fail = False
	for client in groupeds:
		if failure(response, client['IP']):
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): can not configured by Ansible.")
			fail = True
		else:
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): OK")

	if fail:
		app.log.logtask("One or more system couldn't be configured.")
		return False
	return True

def upgradable_group(app, task, group_id):
	# check if group exists
	group = getobject(app, 'group', group_id)        
	if not group:
		app.log.logtask("Error: no group with ID: " + group_id + " in the database.")
		return False

	groupeds = app.database.get_groupeds(group.ID)
	if not groupeds:
		app.log.logtask("No system found in the group " + group.name + ".")
		return False

	app.log.logtask("Retrieving the list of upgradable packages for the group " + group.name + ".")
	
	# config
	config_group(app, task, group_id)


	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_upgradable_group(task.ID, group, groupeds)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		ansible.clean()
	except IOError as error:
		app.log.logtask(error)
		return False

	response = ansibleparseresponse(app, result)

	# check for failure for each client
	fail = False
	for client in groupeds:
		if failure(response, client['IP']):
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): can not get the list.")
			printfailure(app, response, client['IP'], 'upgradable')
			fail = True
		else:
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): OK")

	# first remove all upgradable linked to the group
	app.database.remove_upgradables(group.ID, 'group')

	glines = getAnsibleGroupOutput(response, groupeds, 'upgradable')
	if not glines:
		app.log.logtask("No package to update.")
		return True

	list_upgradable = parse_group_upgradable(app, glines)

	for upg in list_upgradable:
		# get the package from the db
		pkg = getpackagebyinfo(app, upg['name'], upg['arch'], upg['version'], upg['release'])
		if not pkg:
			app.log.logtask("ERROR: the package " + upg['name'] + "-" + upg['version'] + "-" + upg['release'] + " doesn't come from a repository handled by YARUS.")
			continue
		# check if this upgradable is already register
		if getupgradablebyinfo(app, 'group', group.ID, pkg.ID):
			continue
		# register it
		upgradable = Upgradable(object_id=group.ID, object_type="group", approved=0, ID=upg['upgradable_id'], package_id=pkg.ID)
		upgradable.insert(app.database)

	app.log.logtask("The list of upgradable packages has been retrieved.")
	return True

def all_update_group(app, task, group_id):
	# check if group exists
	group = getobject(app, 'group', group_id)        
	if not group:
		app.log.logtask("Error: no group with ID: " + group_id + " in the database.")
		return False

	groupeds = app.database.get_groupeds(group.ID)
	if not groupeds:
		app.log.logtask("No system found in the group " + group.name + ".")
		return False

	app.log.logtask("Updating all packages for all systems in the group " + group.name + ".")
	
	# config
	config_group(app, task, group_id)


	# get list of all packages
	upgradables = app.database.get_upgradables(group.ID, 'group')

	# generating package names list which will be gave to ansible
	package_list = []
	for package in upgradables:
		pkg = {}
		pkg['name'] = package['name']
		pkg['type'] = package['type']
		package_list.append(pkg)

	# if there's not package in the list 
	if not package_list:
		app.log.logtask("The group " + group.name + " is already up to date.")
		return True
	
	# config
	config_group(app, task, group_id)

	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_update_all_group(task.ID, group, groupeds)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		ansible.clean()
	except IOError as error:
		app.log.logtask(error)
		return False

	response = ansibleparseresponse(app, result)

	# check for failure for each client
	fail = False
	for client in groupeds:
		if failure(response, client['IP']):
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): could not be updated.")
			printfailure(app, response, client['IP'], 'upgrade')
			fail = True
		else:
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): OK")
	
	# register the update into the system
	update = Update(group.ID, 'group', int(datetime.datetime.now().timestamp()), getnewid())
	update.insert(app.database)

	# insert all package that have been updated
	for package in upgradables:
		upgraded = Upgraded(package['ID'], update.ID)
		upgraded.insert(app.database)
			
	if fail:
		app.log.logtask("One or more systems could not be updated.")
		if not upgradable_group(app, task, group.ID):
			app.log.logtask("Could not retrieve the list of remainning packages to update.")
		return False
	
	# update the database (delete all upgradables that are up to date now)
	app.database.remove_upgradables(group.ID, 'group')

	return True

def approved_update_group(app, task, group_id):
	# check if group exists
	group = getobject(app, 'group', group_id)        
	if not group:
		app.log.logtask("Error: no group with ID: " + group_id + " in the database.")
		return False

	groupeds = app.database.get_groupeds(group.ID)
	if not groupeds:
		app.log.logtask("No system found in the group " + group.name + ".")
		return False

	app.log.logtask("Updating all packages for all systems in the group " + group.name + ".")
	
	# config
	config_group(app, task, group_id)

	# get list of all packages
	upgradables = app.database.get_approved_upgradables(group.ID, 'group')

	# generating package names list which will be gave to ansible
	package_list = []
	for package in upgradables:
		pkg = {}
		pkg['name'] = package['name']
		pkg['type'] = package['type']
		package_list.append(pkg)

	# if there's not package in the list 
	if not package_list:
		app.log.logtask("The group " + group.name + " is already up to date.")
		return True
	
	# config
	config_group(app, task, group_id)

	ansible = Ansible()
	try:
		app.log.logtask("Generating playbook...")
		ansible.generate_playbook_update_group(task.ID, group, groupeds, package_list)
		ansible.showplaybook(app)
		app.log.logtask("Executing playbook...")
		result = ansible.executeplaybook(app)
		app.log.logtask("Cleaning temporary files linked to the task...")
		ansible.clean()
	except IOError as error:
		app.log.logtask(error)
		return False

	response = ansibleparseresponse(app, result)

	# check for failure for each client
	fail = False
	for client in groupeds:
		if failure(response, client['IP']):
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): could not be updated.")
			printfailure(app, response, client['IP'], 'upgrade')
			fail = True
		else:
			app.log.logtask("System " + client['name'] + " (" + client['IP'] + "): OK")

	# register the update into the system
	update = Update(group.ID, 'group', int(datetime.datetime.now().timestamp()), getnewid())
	update.insert(app.database)

	# insert all package that have been updated
	for package in upgradables:
		upgraded = Upgraded(package['ID'], update.ID)
		upgraded.insert(app.database)

	if not upgradable_group(app, task, group.ID):
		app.log.logtask("Couldn't retrieve the new list of upgradable packages.")

	if fail:
		app.log.logtask("One or more system could not be updated.")
		return False

	return True

	
