
import sys
import os
import argparse
import re
import time
import gzip
import subprocess
import requests
import hashlib
import time

# check if line matchs content we need (comps, archs)
# return the l if it matchs or None if it doesn't
def parseReleaseLine(line, comps, archs):
	for comp in comps:
		for arch in archs:
			if re.match("^" + comp + "\/[a-zA-Z-]*-" + arch + "(|\/Packages)\.[a-zA-Z0-9]*" , line[2]):
				return line

			if re.match("^" + comp + "\/i18n\/[a-zA-Z-_]*\.[a-zA-Z0-9]*", line[2]):
				return line

			if re.match("^" + comp + "\/dep11\/Components-" + arch + "\.yml\.[a-zA-Z0-9]*", line[2]):
				return line

			if re.match("^" + comp + "\/dep11\/icons-[x0-9@]*\.tar\.gz", line[2]):
				return line
	return None

# check if the host can reach the given url
def checkConnection(url):
	try:
		proxies = {
              "http"  : "proxy.reseau.ratp:80"
            }
		if requests.get(url).status_code == 200:
			return True
		return False
	except Exception as exception:
		print(exception)
		return False

# download file using rsync into /tmp/yarus and return the file path
def getFile_rsync(remote, local, file):
	try:
		remote = remote.replace('http', 'rsync')
		rsync_cmd = "rsync -azq --no-o --copy-links " + remote + "/" + file + " " + local
		result = subprocess.call(rsync_cmd, shell=True) # , env={'RSYNC_PROXY': 'proxy.reseau.ratp:80'}
		# check rsync result
		if result == 20:
			print("TOTO")
			sys.exit(0)
		elif result != 0:
			return False
		else:
			return local + "/" + file
	except Exception as exception:
		print(exception)
		return None

def getDir_rsync(url, local):
	try:
		new_url = url.replace('http', 'rsync')
		rsync_cmd = "rsync -azv --no-o --copy-links " + new_url + " " + local
		result = subprocess.call(rsync_cmd, shell=True, env={'RSYNC_PROXY': 'proxy.reseau.ratp:80'})

		# check rsync result
		if result != 0:
			return result
		return 0
	except Exception as exception:
		print("Can't get dir: " + url)
		print(exception)
		return None

def checkingSignature(path, signature):
	# checking sha256 signature
	sha256_hash = hashlib.sha256()

	# open the local file
	try:
		f = open(path, 'rb')
	except Exception as error:
		return False

	# read data and calculate hash
	while True:
		data = f.read(65536)
		if not data:
			break
		sha256_hash.update(data)

	# compare hashs
	if signature == sha256_hash.hexdigest():
		return True

	return False

def checkingSignatureFromSig(path, signature):

	# open the local sig file
	try:
		f = open(path, 'r')
	except:
		return False

	# read data and calculate hash
	sig = f.read()

	# compare sigs
	if signature == sig:
		return True

	return False

"""
	check for a valid text (valid means it contains only a-z A-Z 0-9 - _ .)
	this function is used to check distribution, components, architectures of a repository
	input:	text to check
	output:
		 	True if the text is valid
		 	False if the text is wrong
"""

def tryDownloadFile(remote_file_dir, local_file_dir, file, signature):
	# downloading the file
	print("Downloading: " + file)

	# we'll try 3 times to get the file with the valid signature
	# if we can't get it, we remove the file and print a mistake
	for try_dl in range(1,4):

		if try_dl > 1:
			print("Trying downloading again (" + str(try_dl) + ")...")

		# downloading
		path = getFile_rsync(remote_file_dir, local_file_dir, file)

		if not path:
			print("The file: " + file + " couldn't be downloaded.")
			continue

		if not checkingSignature(path, signature):
			if try_dl == 3:
				print("The signature of the file is invalid for the third time.")
				print("At this point the only safe thing sync process can do is fail.")
				return False
			else:
				print("The signature of the local file is invalid.")
		else:
			return True

def tryDownloadPkg(root_remote, root_local, pkg_url, pkg_name, signature):
	print("Downloading package: " + pkg_name)

	# we'll try 3 times to get the file with the valid signature
	# if we can't get it, remove file and print error
	for try_dl in range(1,4):

		if try_dl > 1:
			print("Trying downloading again (" + str(try_dl) + ")...")

		# downloading
		remote_pkg_dir = root_remote
		local_pkg_dir = root_local + "/"

		for x in pkg_url.split("/"):
			if x != pkg_url.split("/")[-1]:
				remote_pkg_dir += x + "/"
				local_pkg_dir += x + "/"

		if not os.path.isdir(local_pkg_dir):
			os.makedirs(local_pkg_dir)

		path = getFile_rsync(remote_pkg_dir, local_pkg_dir, pkg_name)

		if not path:
			print("The package: " + pkg_name + " couldn't be downloaded.")
			continue

		# checking signature
		if not checkingSignature(path, signature):
			if try_dl == 3:
				print("The signature of the file is invalid for the third time.")
				print("At this point the only safe thing sync process can do is fail.")
				return False
			else:
				print("The signature of the local file is invalid.")
		else:
			return True
