#! /usr/bin/env python

## @package pygraylog.server
# This package is used to manage Graylog servers using its remote API thanks to requests.
#

import requests
import pygraylog
#from pygraylog.users import User

## The class used to connect against a Grafana instance
class Server:
	## This is the constructor.
	def __init__(self, hostname, port=12900, ssl=False, ssl_verify=True):
		self.error_msg = ""
		self._auth_configured = False

		self._data = None

		if ssl == True:
			proto = 'https'
		else:
			proto = 'http'

		self.url = "%s://%s:%s" % ( proto, hostname, port )

		self.session = requests.Session()

		if ssl == True and ssl_verify == True:
			self.session.verify = True
		else:
			self.session.verify = False

	def get_users(self):
		_url = "%s/users" % (self.url)

		r = self.session.get(_url)

		self._handle_request_status_code(r)

		if r.status_code == 200:
			_result = []
			for json_user in r.json()['users']:
				user = pygraylog.users.User(self)
				try:
					user.load_from_json(json_user)
				except:
					print user.error_msg
					return None
				_result.append(user)

			return _result

		self.error_msg = "Bad status code: %s" % (r.status_code)
		raise IOError

#	def auth_by_token(self, token):
#		if self._auth_configured == False:
#			self.session.headers.update({ 'Accept' : 'application/json', 'Content-Type' : 'application/json', 'Authorization' : "Bearer %s" % token })
#			self._auth_configured = True
#		else:
#			self.error_msg = "Authentication already configured."
#			raise ValueError

	def auth_by_auth_basic(self, user, password):
		if self._auth_configured == False:
			self.session.headers.update({ 'Accept' : 'application/json', 'Content-Type' : 'application/json'})
			self.session.auth = (user, password)
			self._auth_configured = True
		else:
			self.error_msg = "Authentication already configured."
			raise ValueError

	def _handle_request_status_code(self, r):
		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code >= 400:
			self.error_msg = r.text
			raise ValueError
