#! /usr/bin/env python

## @package pygraylog.control
# This package is used to control a Graylog instance using its remote API thanks to requests.
#

import sys, json, requests
from abc import ABCMeta, abstractmethod

from pygraylog.api import MetaAPI

## A metaclass used to create the control API classes.
#
# The methods should not be overwritten. Each class only needs to set the API URL and the allowed command keywords.
#
class MetaControl(MetaAPI):
	__metaclass__ = ABCMeta

	## This is the abstract constructor.
	# Each child class needs to implement it to add the allowed commands.
	@abstractmethod
	def __init__(self, hostname, port, login, password, url, id, command):
		super(MetaControl, self).__init__(hostname, port, login, password)

		self._allowed_commands = []
		self.command = command
		self.failed_stuff = []

		self._url = "http://%s:%i/%s/%s/%s" % (hostname, port, url, id, command)

	## Performs the POST calls using requests
	def perform(self):
		if self.check_command() == False:
			self.error_msg = "Bad keyword, should be: %s" % (self._allowed_commands)
			raise

		r = requests.post(self._url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code > 299:
			self.error_msg = r.json()
			self.failed_stuff = r.json()['message']
			return False

		return True

	## Verifies if the given command is allowed by the class.
	def check_command(self):
		try:
			self._allowed_commands.index(self.command)
		except:
			return False
		return True

	## Appends an allowed keyword to the allowed commands' list.
	# @param keyword the command to add.
	def _append_allowed_commands(self, keyword):
		try:
			self._allowed_commands.index(keyword)
		except:
			self._allowed_commands.append(keyword)
			
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

		self._append_allowed_commands('launch')
		self._append_allowed_commands('stop')
		self._append_allowed_commands('restart')

## This class is used to control streams.
class StreamControl(MetaControl):
	def __init__(self, hostname, port, login, password, id):
		super(InputCheck, self).__init__(hostname, port, login, password, "streams", id, command)

		self._append_allowed_commands('clone')
		self._append_allowed_commands('pause')
		self._append_allowed_commands('resume')
