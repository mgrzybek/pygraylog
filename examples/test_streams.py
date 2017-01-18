#! /usr/bin/env python

from pygraylog.server import Server
from pygraylog.streams import Stream, Alert_Receiver, Rule

server = Server('dappmetlogapp1.pgs', 8080, False, False)
server.auth_by_auth_basic('', '')

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
	print 'foo stream found: %s' % foo_id
	foo.load_from_server(foo_id)

	rules_id = foo.get_rules()

	for rule_id in rules_id:
		rule = Rule(server)
		rule.attach(foo_id)
		rule.load_from_server(rule_id)
		#rule.find_by_id(rule_id)

		try:
			rule.delete()
		except:
			print "rule.delete(): %s" % rule.error_msg

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
			print 'foo created: %s' % foo._data['stream_id']
	except:
		print 'exception: %s' % foo.error_msg

	rule = Rule(server)
	rule.attach(foo)

	try:
		if rule.create(foo_rule) == True:
			print 'rule created'
		else:
			print 'rule not created'
	except:
		print 'rule not created'
		print rule.error_msg
