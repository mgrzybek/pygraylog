#! /usr/bin/env python

## @package pygraylog.api
# This package is used to control a Graylog instance using its remote API thanks to pycurl.
#

import sys, json, pycurl

from StringIO import StringIO
from abc import ABCMeta, abstractmethod

## Sets some common options to a CURL object.
#
# @param curl the pycurl object to set
# @param url the remote URL to connect against
# @param auth "user:pass" string
#
def prepare_curl_object(curl, url, auth):

	curl.setopt(pycurl.URL, url)
	curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
	curl.setopt(pycurl.USERPWD, auth)

## A metaclass used to create the API classes.
#
# The methods should not be overwritten. Each class only needs to set the API URL and the allowed command keywords.
#
class MetaControl:
	__metaclass__ = ABCMeta

	## This is the abstract constructor.
	# Each child class needs to implement it to add the allowed commands.
	@abstractmethod
	def __init__(self, hostname, port, login, password, url, id, command):
		self.allowed_commands = []
		self.command = command
		self.failed_stuff = []
		self.curl = pycurl.Curl()
		self.auth = "%s:%s" % (login, password)
		self.uri = "http://%s:%i/%s/%s/%s" % (hostname, port, url, id, command)
		self.curl.setopt(pycurl.WRITEFUNCTION, self._process_json)
		self.curl.setopt(pycurl.CUSTOMREQUEST, 'POST')
		self.error_msg = ""

		prepare_curl_object(self.curl, self.uri, self.auth)

	## Loads the result into a JSON object.
	# It also updates the failed_stuff list in case of error.
	def _process_json(self, buf):
		result = json.load(StringIO(buf))
		
		if result['type'] == "ApiError":
			self.failed_stuff.append(result['message'])

	## Performs the CURL call using POST.
	def perform(self):
		if self.check_command() == False:
			self.error_msg = "Bad keyword, should be: %s" % (self.allowed_commands)
			raise

		try:
			self.curl.perform()
		except:
			self.error_msg = self.curl.errstr()
			raise

		if len(self.failed_stuff) > 0 and self.curl.getinfo(pycurl.RESPONSE_CODE) > 299:
			self.curl.close()
			return False

		self.curl.close()
		return True

	## Verifies if the given command is allowed by the class.
	def check_command(self):
		try:
			self.allowed_commands.index(self.command)
		except:
			return False
		return True

	## Appends an allowed keyword to the allowed commands' list.
	# @param keyword the command to add.
	def append_allowed_commands(self, keyword):
		try:
			self.allowed_commands.index(keyword)
		except:
			self.allowed_commands.append(keyword)
			
		return True

	## Joins the list using ',' to return a string.
	def get_failed_stuff_as_string(self):
		if len(self.failed_stuff) > 0:
			return str.join(', ', self.failed_stuff)
		return None

## This class is used to control inputs.
class InputControl(MetaControl):

	def __init__(self, hostname, port, login, password, id, command):
		super(InputControl, self).__init__(hostname, port, login, password, "system/inputs", id, command)

		self.append_allowed_commands('launch')
		self.append_allowed_commands('stop')
		self.append_allowed_commands('restart')

## This class is used to control streams.
class StreamControl(MetaControl):

	def __init__(self, hostname, port, login, password, id):
		super(InputCheck, self).__init__(hostname, port, login, password, "streams", id, command)

		self.append_allowed_commands('clone')
		self.append_allowed_commands('pause')
		self.append_allowed_commands('resume')
