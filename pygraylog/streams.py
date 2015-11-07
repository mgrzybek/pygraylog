#! /usr/bin/env python

## @package pygraylog.streams
# This package is manage Graylog streams using its remote API thanks to requests.
#

import sys, json, requests

from pygraylog.api import MetaObjectAPI

## This class is used to manage the streams.
class Stream(MetaObjectAPI):

	## Creates a stream using the given dict.
	# @param stream_details a dict with four required keys (description, rules, title).
	# @throw TypeError the given variable is not a dict
	# @throw ValueError some required keys are missing in the given stream_details dict
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def create(self, stream_details):
		if type(stream_details) is not dict:
			self.error_msg = "given stream_details must be a dict."
			raise TypeError
		
		if 'description' not in stream_details or 'rules' not in stream_details or 'title' not in stream_details:
			self.error_msg = "Some parameters are missing, required: description, rules, title."
			raise ValueError

		self._validation_schema =  super(Stream, self)._get_validation_schema("streams")['models']['CreateStreamRequest']

		return super(Stream, self)._create("streams", stream_details)

	## Removes a previously loaded stream from the server.
	# The key 'id' from self._data is used.
	# @throw TypeError the given variable is not a dict
	# @throw ValueError the key named 'id' is missing in the loaded data
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def delete(self):
		if self._data == None or 'id' not in self._data:
			self.error_msg = "The object is empty: no id available."
			raise ValueError

		return super(Stream, self)._delete("streams", self._data['id'])

	## Tells if a stream exists in the server's database.
	# @param id the stream to find
	# @throw ValueError the given stream is empty
	# @throw IOError HTTP code >= 500
	# @return True if found
	def find_by_id(self, id):
		return super(Stream, self).find_by_id("streams", id)
	
	## Returns the stream's id if it exists in the server's database.
	# @param title the stream to find
	# @throw ValueError the given stream is empty
	# @throw IOError HTTP code >= 500
	# @return the id is found or None
	def find_by_title(self, title):
		if len(title) == 0:
			self.error_msg = "given title is too short."
			raise ValueError

		_url = "%s/%s" % (self._url, "streams")

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code != 200:
			self.error_msg = r.text
			raise IOError

		for (i, stream) in enumerate(r.json()['streams']):
			if stream['title'] == title:
				return stream['id']

		return None

	## Loads a stream from the server's database.
	# @param stream the stream to find
	# @throw ValueError the given stream is empty
	# @throw IOError HTTP code != 200
	# @return True if found and loaded
	def load_from_server(self, id):
		return super(Stream, self).load_from_server("streams", id)

	## Gets the current thoughput of the stream on this node in messages per second
	# @param stream the stream to find
	# @throw ValueError the given stream is empty
	# @throw IOError HTTP code != 200
	# @return the current value
	def get_throughput(self):
		if self._data == None or 'id' not in self._data:
			self.error_msg = "The object is empty: no id available."
			raise ValueError

		_url = "%s/%s/%s/%s" % (self._url, "streams", id, "throughput")

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code != 200:
			self.error_msg = r.json()
			raise IOError

		return r.json()['throughput']

	## Gets the current thoughputs of the streams on this node in messages per second
	# @throw ValueError the given stream is empty
	# @throw IOError HTTP code != 200
	# @return the current values as a JSON object
	def get_throughputs(self):
		_url = "%s/%s/%s" % (self._url, "streams", "throughput")

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code != 200:
			self.error_msg = r.json()
			raise IOError

		return r.json()['throughput']

	def backup(self, id):
		return self._backup2("streams", id)

class Alert_Receiver(MetaObjectAPI):

	## Attaches a group of alert receivers to a stream using the given dict.
	# @param ar_details a list of dicts with three required keys (streamId, entity, type).
	# @throw TypeError the given variable is not a dict
	# @throw ValueError some required keys are missing in the given stream_details dict
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def create(self, ar_details):
		if type(ar_details) is not list:
			self.error_msg = "given stream_details must be a list of dicts."
			raise TypeError

		for ar in enumerate(ar_details):
			if self.add(ar) == False:
				return False

		return True

	## Attaches an alert receiver to a stream using the given dict.
	# @param ar_details a dict with three required keys (streamId, entityn type).
	# @throw TypeError the given variable is not a dict
	# @throw ValueError some required keys are missing in the given stream_details dict
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def add(self, ar_details):
		if type(ar_details_details) is not dict:
			self.error_msg = "given stream_details must be a dict."
			raise TypeError
		
		if 'streamId' not in ar_details or 'entity' not in ar_details or 'type' not in ar_details:
			self.error_msg = "Some parameters are missing, required: streamId, entity, type."
			raise ValueError
		
		if pygraylog.streams.Stream(self._hostname, self._login, self._password).find_by_id(ar_details['streamId']) == False:
			self.error_msg = "Bad given streamId."
			raise ValueError

		# TODO: find the right definition in the API's doc
		#self._validation_schema =  super(Stream, self)._get_validation_schema("users")['models']['StreamListResponse']['streams']

		_url = "/streams/%s/%alerts/receivers" % ( ar_details['streamId'] )

		return super(Alert_Receiver, self).create(_url, ar_details)

	## Removes a previously loaded alert receiver from all the streams.
	# self._data is used and cleared on success.
	# @throw TypeError the given variable is not a dict
	# @throw ValueError the key named 'id' is missing in the loaded data
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def erase(self):
		if self._data == None or 'type' not in self._data or 'entity' not in self._data:
			self.error_msg = "The object is empty: no type or entity available."
			raise ValueError

		r = requests.get("/streams", auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return False

		for (i, stream) in enumerate(r.json()['streams']):
			if 'alert_receivers' in stream:
				_url = "/streams/%s/%alerts/receivers" % ( stream['id'] )
				_payload = {}

				if self._data['entity'] in stream['alert_receivers']['emails']:
					_payload = { 'streamId': stream['id'], 'entity': self._data['entity'], 'type': 'emails' }
				else:
					_payload = { 'streamId': stream['id'], 'entity': self._data['entity'], 'type': 'users' }

				r = requests.delete(_url, auth=(self._login, self._password), params=_payload)

				if r.status_code >= 500:
					self.error_msg = r.text
					raise IOError

		self._data.clear()

		return True

	## Removes a previously loaded alert receiver from a stream.
	# self._data is used.
	# @throw TypeError the given variable is not a dict
	# @throw ValueError the key named 'id' is missing in the loaded data
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def delete(self):
		if self._data == None or 'type' not in self._data or 'entity' not in self._data:
			self.error_msg = "The object is empty: no type or entity available."
			raise ValueError

		_url = "/streams/%s/%alerts/receivers" % ( ar_details['streamId'] )

		r = requests.delete(_url, auth=(self._login, self._password), params=self._data)

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 204:
			self._data.clear()
			return True

		self._response = r.json()

		return False

	## Tells if an alert receiver exists somewhere in one of the stored streams.
	# @param id email or username to find
	# @throw ValueError the given stream is empty
	# @throw IOError HTTP code >= 500
	# @return True if found
	def find_by_id(self, id):
		if len(id) == 0:
			self.error_msg = "given id is too short."
			raise ValueError

		_url = "%s/%s" % (self._url, 'streams')

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return False

		for (i, stream) in enumerate(r.json()['streams']):
			if 'alert_receivers' in stream:
				if id in stream['alert_receivers']['emails'] or id in stream['alert_receivers']['users']:
					return True

		return False

	## Loads an object from the server's database.
	# @param id email or username to find
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return True if found and loaded
	def load_from_server(self, id):
		objec_name = 'streams'

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
		
		for (i, stream) in enumerate(r.json()['streams']):
			if 'alert_receivers' in stream:
				if id in stream['alert_receivers']['emails']:
					self._data[stream['id']] = { 'emails': [ id ] }
				elif id in stream['alert_receivers']['users']:
					self._data[stream['id']] = { 'users': [ id ] }

		return True

	## Exports the specified objects from the server's database.
	# It overrides the parent method.
	# @param object_name the type of resource to find (user, streams...)
	# @throw ValueError the given parameters are not valid
	# @throw IOError HTTP code >= 500
	# @return the JSON object or None
	def backup(self, object_name):
		if len(object_name) == 0:
			self.error_msg = "given object_name is too short."
			raise ValueError

		_result = {}
		_buf = self.super(Alert_Receiver, self).backup('streams')

		for stream in enumerate(_buf):
			if 'alert_receivers' in stream:
				_result[stream['id']] = stream['alert_receivers']

		return _result
