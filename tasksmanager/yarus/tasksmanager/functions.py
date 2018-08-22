
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

def getDir_rsync(app, url, local):
	try:
		new_url = url.replace('http://', 'rsync://')

		rsync_cmd = "rsync -zvrtL " + new_url + " " + local
		
		# if proxy set in the config file
		if app.config.px_host != "":
			env = {'RSYNC_PROXY': app.config.px_host + ":" + str(app.config.px_port)}
		else:
			env = None

		# execute the command
		process = subprocess.Popen(rsync_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env, bufsize=1, universal_newlines=True)

		# log the output
		for line in process.stdout:
			app.log.logtask(line.strip("\n"))

		# get the final result of rsync
		result = process.wait()

		# check rsync result
		if result != 0:
			app.log.logtask("Command executed: " + rsync_cmd)
			app.log.logtask("Return status: " + str(result))
			output, error = process.communicate()
			app.log.logtask("Error: " + str(error))
			app.log.logtask("RSYNC Output: " + str(output))
			return False
		return True

	except Exception as exception:
		print("Can't get dir: " + url)
		print(exception)
		return None

def getFile_rsync(app, url, local, file):
	try:
		new_url = url.replace('http://', 'rsync://')

		rsync_cmd = "rsync -zvrtL " + new_url + file + " " + local
		
		# if proxy set in the config file
		if app.config.px_host != "":
			env = {'RSYNC_PROXY': app.config.px_host + ":" + str(app.config.px_port)}
		else:
			env = None
			
		# execute the command
		process = subprocess.Popen(rsync_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env, bufsize=1, universal_newlines=True)

		# get the final result of rsync
		result = process.wait()

		# check rsync result
		if result != 0:
			output, error = process.communicate()
			app.log.logtask("Command executed: " + rsync_cmd)
			app.log.logtask("Error: " + str(error))
			return False
		return local + file

	except Exception as exception:
		return None

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

def getSigFile(file):
	sha256_hash = hashlib.sha256()

	# open the local file
	try:
		f = open(file, 'rb')
	except Exception as error:
		return False

	# read data and calculate hash
	while True:
		data = f.read(65536)
		if not data:
			break
		sha256_hash.update(data)

	return sha256_hash.hexdigest()

def check256(path, signature):
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

def tryDownloadFile(app, remote, local, file, algo, signature):
	# downloading the file
	app.log.logtask("Downloading: " + file)

	# we'll try 3 times to get the file with the valid signature
	# if we can't get it, we remove the file and print a mistake
	for try_dl in range(1,4):

		if try_dl > 1:
			app.log.logtask("Trying to download again (" + str(try_dl) + ")...")

		# downloading
		path = getFile_rsync(app, remote, local, file)

		if not path:
			app.log.logtask("The file: " + file + " couldn't be downloaded.")
			continue

		if algo == 'sha256':
			if not check256(path, signature):
				if try_dl == 3:
					app.log.logtask("The signature of the file is invalid for the third time.")
					# TODO: remove file
					return False
				else:
					app.log.logtask("The signature of the local file is invalid.")
			else:
				return True
