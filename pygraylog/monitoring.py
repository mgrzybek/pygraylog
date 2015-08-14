#! /usr/bin/env python

## @package pygraylog.monitoring
# This package is used to monitor a Graylog instance using its remote API thanks to pycurl.
#

import sys, json, requests

from abc import ABCMeta, abstractmethod
from pygraylog.api import MetaRootAPI

## A metaclass used to create the monitoring classes.
#
# Only one method needs to be overwritten by the children classes.
#
class MetaCheck(MetaRootAPI):
	__metaclass__ = ABCMeta

	## This is the abstract constructor.
	# Each child class needs to implement it using the right parameters.
	@abstractmethod
	def __init__(self, hostname, port, login, password, url):
		super(MetaCheck, self).__init__(hostname, port, login, password)

		self.failed_stuff = []
		self._url = "http://%s:%i/%s" % (hostname, port, url)

	## Updates the failed_stuff list in case of error.
	# @param buf the binary result from a CURL call.
	@abstractmethod
	def _process_json(self, buf): pass

	## Performs the GET calls using requestss
	def perform(self):
		r = requests.get(self._url, auth=(self._login, self._password))

		if r.status_code == 401:
			self.error_msg = 'Not authorized (HTTP 401)'
			raise IOError

		self._process_json(r.json())

		if len(self.failed_stuff) > 0:
			return False
		return True

	## Joins the list using ',' to return a string.
	def get_failed_stuff_as_string(self):
		if len(self.failed_stuff) > 0:
			return str.join(', ', self.failed_stuff)
		return None

## This class is used to monitor inputs.
# It alerts if some inputs are not running.
class InputCheck(MetaCheck):

	def __init__(self, hostname, port, login, password):
		super(InputCheck, self).__init__(hostname, port, login, password, "system/inputs")

	## Checks if some inputs are not running.
	def _process_json(self, buf):
		for (i, input) in enumerate(buf["inputs"]):
			if input["state"] != "RUNNING":
				self.failed_stuff.append(input["message_input"]["title"])

## This class is used to monitor streams.
# It alerts if some streams are disabled.
class StreamCheck(MetaCheck):

	def __init__(self, hostname, port, login, password):
		super(StreamCheck, self).__init__(hostname, port, login, password, "streams")

	## Checks if some streams are disabled.
	def _process_json(self, buf):
		for (i, stream) in enumerate(buf["streams"]):
			if stream["disabled"] != False:
				self.failed_stuff.append(stream["title"])
