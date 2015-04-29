#! /usr/bin/env python

## @package pygraylog.api
# This package is used to store the meta classes.
#

import sys, json, requests
from abc import ABCMeta, abstractmethod

## A metaclass used to create the other API classes.
class MetaAPI:
	__metaclass__ = ABCMeta

	## This is the abstract constructor.
	@abstractmethod
	def __init__(self, hostname, port, login, password):
		self.error_msg = ""

		self._login = login
		self._password = password
		self._url = ""

