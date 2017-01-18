#! /usr/bin/env python

from pygraylog.server import Server
from pygraylog.users import User

import json

server = Server('dappmetlogapp1.pgs', 8080, False, False)
server.auth_by_auth_basic('', '')

users = server.get_users()

john = User(server)

user = { u'username' : u'john', u'full_name' : u'john doe', u'email' : 'john@doe.org', u'password' : u'secret', u'permissions' : [  ] }

print user

if john.find_by_id('john') == True:
	print 'john found'
	john.load_from_server('john')

	if john.update({ 'full_name' : 'John DOE' }) == True:
		print 'john updated'
	else:
		print 'john not updated'
		print john_response

	if john.delete() == True:
		print 'john deleted'
	else:
		print 'john still exists'
		print john._response
else:
	print 'john not found'
	if john.create(user) == True:
			print 'john created'
	else:
		print 'john failed'
		print john._response
