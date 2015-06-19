#! /usr/bin/env python

from pygraylog.users import User

john = User('dappsyslogapp1.pgs', 12900, 'dieux', 'admin')

#if john.find_by_username('mathieu.grzybek') == True:
	#print 'mathieu found'

#if john.find_by_username('john') == True:
	#print 'john found'
#else:
	#print 'john not found'

user = { u'username' : u'john', u'full_name' : u'john doe', u'email' : 'john@doe.net', u'password' : u'doejohn', u'permissions' : [ u'*' ] }

if john.find_by_id('john') == True:
	print 'john found'
	john._data['username'] = 'john'
	if john.delete() == True:
		print 'john deleted'
	else:
		print 'john still exists'
		print john._response
else:
	print 'john not found'
	if john.create(user) == True:
		print 'john created'
		print john._data
	else:
		print 'john failed'
		print john._response

