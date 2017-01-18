#! /usr/bin/env python

import sys, getopt

sys.path.append('/usr/local/nagios/share')
from pygraylog.monitoring import InputCheck

hostname = ""
user = ""
password = ""
port = 0

options = ""

#############

try:
	options, remainder = getopt.gnu_getopt(sys.argv[1:], 'h:p:u:P:', ['host=', 'port=', 'user=', 'password=' ])
except getopt.GetoptError as err:
	print "UNKNOWN - %s" % str(err)
	exit(3)

if len(options) < 4:
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

#############

check = InputCheck(hostname, port, user, password)

try:
	check.perform()
except:
	print "UNKOWN - failed to retrieve data"
	exit(3)

if len(check.failed_stuff) > 0:
	print "CRITICAL -", check.get_failed_stuff_as_string()
	exit(2)

print "OK - all inputs opened"
exit(0)

