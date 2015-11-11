#! /usr/bin/env python

from pygraylog.server import Server
from pygraylog.streams import Stream, Alert_Receiver, Rule

server = Server('localhost', 12900, False, False)
server.auth_by_auth_basic('foo', 'bar')

stream = Stream(server)
alert = Alert_Receiver(server)

foo_stream = {
'matching_type' : 'AND',
'description' : 'stream de foo',
'title' : 'FOO - bar'
}

foo_rule = {
'field' : 'message',
'type' : 2,
'inverted' : False,
'value' : '^problem$'
}

foo = Stream(server)
foo.load_from_json(foo_stream)

foo_id = stream.find_by_title(foo_stream['title'])
if foo_id != None:
	print 'foo stream found'
	foo.load_from_server(foo_id)
	try:
		if foo.delete() == True:
			print 'foo deleted'
		else:
			print 'foo not deleted'
	except:
		print foo.error_msg
else:
	print 'foo stream not found'
	try:
		if foo.create(foo_stream) == True:
			print 'foo created'
		try:
			rule = Rule(server)
			rule.attach(foo)

			if rule.create(foo_rule) == True:
				print 'rule created'
			else:
				print 'rule not created'
		except:
			if len(rule.error_msg) > 0:
				print rule.error_msg
			else:
				raise
	except:
		print foo.error_msg

