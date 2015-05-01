#! /usr/bin/env python

## @package pygraylog.streams
# This package is manage Graylog streams using its remote API thanks to requests.
#

import sys, json, requests

from pygraylog.api import MetaAPI

class Stream(MetaObjectAPI):

	## Creates a stream using the given dict.
	# @param stream_details a dict with five required keys (description, rules, title, content-pack).
	# @throw TypeError the given variable is not a dict
	# @throw ValueError some required keys are missing in the given stream_details dict
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def create(self, stream_details):
		if type(stream_details) is not dict:
			self.error_msg = "given stream_details must be a dict."
			raise TypeError
		
		if 'description' not in stream_details or 'rules' not in stream_details or 'title' not in stream_details or 'content-pack':
			self.error_msg = "Some parameters are missing, required: description, rules, title, content-pack."
			raise ValueError

		return super(MetaObjectAPI, self).create("streams", stream_details)

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

		return super(MetaObjectAPI, self).delete("streams", self._data['id'])

	## Tells if a stream exists in the server's database.
	# @param id the stream to find
	# @throw ValueError the given stream is empty
	# @throw IOError HTTP code >= 500
	# @return True if found
	def find_by_id(self, id):
		return super(MetaObjectAPI, self).find_by_id("streams", id)
	
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
		return super(MetaObjectAPI, self).load_from_server("streams", id)

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
	def get_throughput(self):
		_url = "%s/%s/%s" % (self._url, "streams", "throughput")

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code != 200:
			self.error_msg = r.json()
			raise IOError

		return r.json()['throughput']
