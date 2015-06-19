#! /usr/bin/env python

## @package pygraylog.api
# This package is used to store the meta classes.
#

import sys, json, requests, re
import jsonschema
from abc import ABCMeta, abstractmethod

## A metaclass used to create the other API classes.
class MetaRootAPI:
	__metaclass__ = ABCMeta

	## This is the abstract constructor.
	@abstractmethod
	def __init__(self, hostname, port, login, password):
		self.error_msg = ""

		self._hostname = hostname
		self._login = login
		self._password = password
		self._url = ""

class MetaAdminAPI(MetaRootAPI):
	__metaclass__ = ABCMeta

	## This is the abstract constructor.
	@abstractmethod
	def __init__(self, hostname, port, login, password):
		super(MetaAdminAPI, self).__init__(hostname, port, login, password)

	@abstractmethod
	def perform(): pass

class MetaObjectAPI(MetaRootAPI):
	__metaclass__ = ABCMeta

	## This is the main constructor of the class
	def __init__(self, hostname, port, login, password):
		super(MetaObjectAPI, self).__init__(hostname, port, login, password)

		self._data = {}
		self._response = {}
		self._url = "http://%s:%i" % (hostname, port)

		self._validation_schema = {}
		self.error_msg = ""

	## Gets the validation schema from the server
	# @param object_name the type of resource to find (user, streams...)
	# @throw IOError HTTP code >= 500
	# @return the schema or None
	def _get_validation_schema(self, object_name):
		_url = "%s/api-docs/%s" % (self._url, object_name)

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return None

		return r.json()

	## Creates an object using the given dict.
	# @param details a dict with required keys
	# @throw TypeError the given variable is not a dict
	# @throw ValueError some required keys are missing in the given details dict
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	@abstractmethod
	def create(self, details):
		raise ValueError

	## Creates an object using the given dict.
	# @param object_name the type of resource to find (user, streams...)
	# @param details a dict with required keys
	# @throw TypeError the given variable is not a dict
	# @throw ValueError some required keys are missing in the given details dict
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def _create(self, object_name, details):
		_url = "%s/%s" % (self._url, object_name)

		jsonschema.validate(json.dumps(details), self._validation_schema)

		r = requests.post(_url, json.dumps(details), auth=(self._login, self._password), headers={'Content-Type': 'application/json'})

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 400:
			self.error_msg = r.text
			raise ValueError

		if r.status_code == 201:
			key = "%s_id" % ( re.sub('s$', '', object_name ) )

			self._data = details
			self._data['id'] = r.json()[key]

			return True

		self._response = r.json()

		return False

	## Removes a previously loaded object from the server.
	# self._data is cleared on success.
	# @param id the id to find (username, id...)
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	@abstractmethod
	def delete(self, object_name, id):
		raise ValueError

	## Removes a previously loaded object from the server.
	# self._data is cleared on success.
	# @param object_name the type of resource to find (user, streams...)
	# @param id the id to find (username, id...)
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def _delete(self, object_name, id):
		if len(object_name) == 0:
			self.error_msg = "given object_name is too short."
			raise ValueError

		if len(id) == 0:
			self.error_msg = "given id is too short."
			raise ValueError

		_url = "%s/%s/%s" % (self._url, object_name, id)

		r = requests.delete(_url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 204:
			self._data.clear()
			return True

		self._response = r.json()

		return False

	## Tells if an object exists in the server's database.
	# @param object_name the type of resource to find (user, streams...)
	# @param id the id to find (username, id...)
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return True if found
	@abstractmethod
	def find_by_id(self, object_name, id):
		if len(object_name) == 0:
			self.error_msg = "given object_name is too short."
			raise ValueError

		if len(id) == 0:
			self.error_msg = "given id is too short."
			raise ValueError

		_url = "%s/%s/%s" % (self._url, object_name, id)

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return False

		return True

	## Loads an object from the server's database.
	# @param object_name the type of resource to find (user, streams...)
	# @param id the id to find (username, id...)
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return True if found and loaded
	def _load_from_server(self, object_name, id):
		if len(object_name) == 0:
			self.error_msg = "given object_name is too short."
			raise ValueError

		if len(id) == 0:
			self.error_msg = "given id is too short."
			raise ValueError

		_url = "%s/%s/%s" % (self._url, object_name, id)

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return False

		self._data = r.json()
		return True

	## Exports the specified object from the server's database.
	# @param object_name the type of resource to find (user, streams...)
	# @param id the id to find (username, id...) or None to backup everything
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return the JSON object or None
	def _backup2(self, object_name, id):
		if len(object_name) == 0:
			self.error_msg = "given object_name is too short."
			raise ValueError

		if len(id) == 0:
			self.error_msg = "given id is too short."
			raise ValueError

		if self._load_from_server(object_name, id) == False:
			return None

		return self._data

	## Exports the loaded object from the server's database.
	# @param object_name the type of resource to find (user, streams...)
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return the JSON object or None
	def _backup1(self, object_name):
		if len(object_name) == 0:
			self.error_msg = "given object_name is too short."
			raise ValueError

		_url = "%s/%s" % (self._url, object_name)

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return None

		return r.json()

	@abstractmethod
	def backup(self):
		raise ValueError

## A class used to backup and restore the content of Graylog's database
class Backup(MetaRootAPI):
	def __init__(self, hostname, port, login, password):
		super(MetaAdminAPI, self).__init__(hostname, port, login, password)

		self._hostname = hostname
		self._port = port

	## Exports the whole configuration.
	def backup():
		print "TODO"

	## Exports alarms
	def backup_alarms():
		print "TODO"

	## Exports alerts
	def backup_alerts():
		print "TODO"

	## Exports dashboards
	def backup_dashboards():
		print "TODO"

	## Exports extractors
	def backup_extractors():
		print "TODO"

	## Exports filters
	def backup_filters():
		print "TODO"

	## Exports outputs
	def backup_outputs():
		print "TODO"

	## Exports stream rules
	def backup_stream_rules():
		print "TODO"

	## Exports streams
	def backup_streams():
		return pygraylog.streams.Stream(self._hostname, self._port, self._login, self._password).backup()

	## Exports bundles
	def backup_bundles():
		print "TODO"

	## Exports grok
	def backup_grok():
		print "TODO"

	## Exports inputs
	def backup_inputs():
		print "TODO"

	## Exports jobs
	def backup_jobs():
		print "TODO"

	## Exports LDAP
	def backup_ldap():
		print "TODO"

	## Exports users
	def backup_users():
		return pygraylog.users.User(self._hostname, self._port, self._login, self._password).backup()
