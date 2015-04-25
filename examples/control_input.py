#! /usr/bin/env python

import sys, getopt

sys.path.append('/usr/local/nagios/share')
from pygraylog.api import InputControl

hostname = ""
user = ""
password = ""
port = 0
command = ""
id = ""

options = ""

#############

try:
	options, remainder = getopt.gnu_getopt(sys.argv[1:], 'h:p:u:P:c:i:', ['host=', 'port=', 'user=', 'password=', 'command=', 'id=' ])
except getopt.GetoptError as err:
	print "UNKNOWN - %s" % str(err)
	exit(3)

if len(options) < 6:
	print "UNKOWN - args error"
	exit(3)

for opt, arg in options:
	if opt in ('-h', '--host'):
		hostname = arg
	elif opt in ('-p', '--port'):
		port = int(arg)
	elif opt in ('-u', '--user'):
		user = arg
	elif opt in ('-P', '--password'):
		password = arg
	elif opt in ('-c', '--command'):
		command = arg
	elif opt in ('-i', '--id'):
		id = arg

if port == 0:
	print "UNKOWN - bad port given"
	exit(3)

if len(user) == 0:
	print "UNKOWN - bad user given"
	exit(3)

if len(password) == 0:
	print "UNKOWN - bad password given"
	exit(3)

if len(hostname) == 0:
	print "UNKOWN - bad hostname given"
	exit(3)

if len(command) == 0:
	print "UNKOWN - bad command given"
	exit(3)

if len(id) == 0:
	print "UNKOWN - bad id given"
	exit(3)

#############

action = InputControl(hostname, port, user, password, id, command)

try:
	action.perform()
except:
	print "UNKOWN - failed to '%s' the input: %s" % ( command, action.error_msg )
	exit(3)

if len(action.failed_stuff) > 0:
	print "CRITICAL -", action.get_failed_stuff_as_string()
	exit(2)

print "OK - action %s on input %s succeded"
exit(0)
