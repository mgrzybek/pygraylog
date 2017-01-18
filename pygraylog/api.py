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
	def __init__(self, server):
		if server == None:
			self.error_msg = "bad server given"
			raise ValueError

		self._server = server
		self.error_msg = ""
		self._data = None
		self._response = ""

	def _handle_request_status_code(self, r):
		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code >= 400:
			self.error_msg = r.text
			raise ValueError

class MetaAdminAPI(MetaRootAPI):
	__metaclass__ = ABCMeta

	@abstractmethod
	def perform(): pass

class MetaObjectAPI(MetaRootAPI):
	__metaclass__ = ABCMeta

	## This is the main constructor of the class
	def __init__(self, server):
		super(MetaObjectAPI, self).__init__(server)

		self._response = {}

		self._validation_schema = {}
		self.error_msg = ""

	## Gets the validation schema from the server
	# @param object_name the type of resource to find (user, streams...)
	# @throw IOError HTTP code >= 500
	# @return the schema or None
	def _get_validation_schema(self, object_name):
		_url = "%s/api-docs/%s" % (self._server.url, object_name)

		r = self._server.session.get(_url)

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
		_url = "%s/%s" % (self._server.url, object_name)

		jsonschema.validate(json.dumps(details), self._validation_schema)

		r = self._server.session.post(_url, json.dumps(details), headers={'Content-Type': 'application/json'})

		# TODO: get the id from the child object, "object + _id" does no longer work with users
		if r.status_code == 201:
			self._data = details
			self._response = r.json()

			return True

		self._handle_request_status_code(r)
		self._response = r.json()

		return False

	## Removes a previously loaded object from the server.
	# self._data is cleared on success.
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	@abstractmethod
	def delete(self):
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

		_url = "%s/%s/%s" % (self._server.url, object_name, id)

		r = self._server.session.delete(_url)

		self._handle_request_status_code(r)

		if r.status_code == 204:
			self._data.clear()
			return True

		self._response = r.json()

		return False

	## Updates a previously loaded object from the server.
	# self._data is cleared on success.
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	@abstractmethod
	def update(self):
		raise ValueError

	## Updates a previously loaded object from the server.
	# self._data is cleared on success.
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def _update(self, object_name, id, details):
		_url = "%s/%s/%s" % (self._server.url, object_name, id)

		jsonschema.validate(json.dumps(details), self._validation_schema)

		r = self._server.session.put(_url, json.dumps(details), headers={'Content-Type': 'application/json'})

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 400:
			self.error_msg = r.text
			raise ValueError

		if r.status_code == 204:
			for k in details.keys():
				print "%s - %s = %s" % ( k, details[k], self._data[k] )
				if details[k] != self._data[k]:
					self._load_from_server(object_name, id)
					return True
			return False

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

		_url = "%s/%s/%s" % (self._server.url, object_name, id)

		r = self._server.session.get(_url)

		if r.status_code == 404:
			self._response = r.json()
			return False

		self._handle_request_status_code(r)

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

		_url = "%s/%s/%s" % (self._server.url, object_name, id)

		r = self._server.session.get(_url)

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return False

		self._data = r.json()
		return True

	## Loads an object from the given JSON object.
	# @param details the data to load
	# @throw ValueError the given parameters are not valid
	# @return True if found and loaded
	def load_from_json(self,details):
		if len(details) == 0:
			self.error_msg = "given details are too short."
			raise ValueError

		jsonschema.validate(json.dumps(details), self._validation_schema)

		self._data = details
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

		_url = "%s/%s" % (self._server.url, object_name)

		r = self._server.session.get(_url)

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return None

		return r.json()

#	@abstractmethod
#	def backup(self):
#		raise ValueError

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
		print "TODO"

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
		print "TODO"
