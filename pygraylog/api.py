#! /usr/bin/env python

## @package pygraylog.api
# This package is used to store the meta classes.
#

import sys, json, requests
from abc import ABCMeta, abstractmethod

## A metaclass used to create the other API classes.
class MetaRootAPI:
	__metaclass__ = ABCMeta

	## This is the abstract constructor.
	@abstractmethod
	def __init__(self, hostname, port, login, password):
		self.error_msg = ""

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

		self.error_msg = ""

	## Creates an object using the given dict.
	# @param details a dict with required keys
	# @throw TypeError the given variable is not a dict
	# @throw ValueError some required keys are missing in the given details dict
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	@abstractmethod
	def create(self, object_name, details):
		_url = "%s/%s" % (self._url, object_name)

		r = requests.post(_url, json.dumps(details), auth=(self._login, self._password), headers={'Content-Type': 'application/json'})

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError
		
		if r.status_code == 201:
			self._data = details
			return True

		self._response = r.json()

		return False

	## Removes a previously loaded object from the server.
	# @param object_name the type of resource to find (user, streams...)
	# @param id the id to find (username, id...)
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	@abstractmethod
	def delete(self, object_name, id):
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
	@abstractmethod
	def load_from_server(self, object_name, id):
		if len(object_name) == 0:
			self.error_msg = "given object_name is too short."
			raise ValueError

		if len(id) == 0:
			self.error_msg = "given id is too short."
			raise ValueError

		_url = "%s/%s/%s" % (self._url, object_name, username)

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return False

		self._data = r.json()
		return True
