#!/opt/yarus/env/bin/python

import argparse
import sys

from yarus.common.app import App

parser = argparse.ArgumentParser()

parser.add_argument('--list', action='store_true')
parser.add_argument('--host', action='store' )

args = parser.parse_args()

if args.list:

	# start the app context
	app = App()

	if not app.start():
		print("{}")
		sys.exit(0)

	app.database.connect()
	result = app.database.get_all_object('yarus_client')

	hosts = ""
	if len(result) > 0:
		for client in result:
			if client != result[-1]:
				hosts += '"' + client['IP'] + '", '
			else:
				hosts += '"' + client['IP'] + '"'

	print('{ "yarus": { "hosts": [' + hosts + '] } }')

	app.database.close()

elif args.host:
	print("{}")

else:
	print("{}")
