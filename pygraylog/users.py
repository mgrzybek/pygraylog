#! /usr/bin/env python

## @package pygraylog.users
# This package is used to manage Graylog users using its remote API thanks to requests.
#

import sys, json, requests

from pygraylog.api import MetaObjectAPI

## This class is used to manage the users.
class User(MetaObjectAPI):

	## Creates a user using the given dict.
	# @param user_details a dict with five required keys (username, full_name, email, password, permissions).
	# @throw TypeError the given variable is not a dict
	# @throw ValueError some required keys are missing in the given user_details dict
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def create(self, user_details):
		if type(user_details) is not dict:
			self.error_msg = "given user_details must be a dict."
			raise TypeError
		
		if 'username' not in user_details or 'full_name' not in user_details or 'email' not in user_details or 'password' not in user_details or 'permissions' not in user_details:
			self.error_msg = "Some parameters are missing, required: username, full_name, email, password, permissions."
			raise ValueError

		self._validation_schema =  super(User, self)._get_validation_schema("users")['models']['User']

		return super(User, self)._create("users", user_details)

	## Removes a previously loaded user from the server.
	# The key 'username' from self._data is used.
	# @throw TypeError the given variable is not a dict
	# @throw ValueError the key named 'username' is missing in the loaded data
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def delete(self):
		if self._data == None or 'username' not in self._data:
			self.error_msg = "The object is empty: no username available."
			raise ValueError

		return super(User, self)._delete("users", self._data['username'])

	## Tells if a username exists in the server's database.
	# @param username the user to find
	# @throw ValueError the given username is empty
	# @throw IOError HTTP code >= 500
	# @return True if found
	def find_by_id(self, username):
		return super(User, self).find_by_id("users", username)

	## Loads a username from the server's database.
	# @param username the user to find
	# @throw ValueError the given username is empty
	# @throw IOError HTTP code >= 500
	# @return True if found and loaded
	def load_from_server(self, username):
		return super(User, self)._load_from_server("users", username)

	## Flushes the user's permissions from the server's database.
	# @throw ValueError the object's data are empty
	# @throw IOError HTTP code >= 500
	# @return True if found and loaded
	def revoke_permissions(self):
		if self._data == None:
			self.error_msg = "The object is empty: no username available."
			raise ValueError

		_url = "%s/%s/%s/%s" % (self._url, "users", username, "permissions")

		r = requests.delete(_url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 204:
			self._data['permissions'].clear()
			return True

		self._response = r.json()

		return False

	## Sets the user's permissions from the server's database.
	# @throw ValueError the object's data are empty
	# @throw TypeError the given permissions must be a dict
	# @throw IOError HTTP code >= 500
	# @return True if found and loaded
	def set_permissions(self, permissions):
		if type(permissions) is not list:
			self.error_msg = "given permissions must be a list."
			raise TypeError

		_url = "%s/%s/%s/%s" % (self._url, "users", self._data['username'], "permissions")

		r = requests.put(_url, json.dumps(permissions), auth=(self._login, self._password), headers={'Content-Type': 'application/json'})

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 204:
			self._data['permissions'] = permissions
			return True

		self._response = r.json()

		return False

	## Sets the user's permissions from the server's database.
	# @throw ValueError no data previously loaded
	# @return a list containing the permissions
	def get_permissions(self):
		if self._data == None:
			self.error_msg = "The object is empty: no data available, use load_from_server first."
			raise ValueError

		return self._data['permissions']

	def backup(self):
		if self._data == None or 'username' not in self._data:
			self.error_msg = "The object is empty: no username available."
			raise ValueError

		return self._backup2("users", id)

	#def backup(self, id):
		#return self._backup2("users", id)
	
	def backup_all(self):
		return self._backup1("users")
