#! /usr/bin/env python

## @package pygraylog.dashboards
# This package is used to manage Graylog dashboards using its remote API thanks to requests.
#

import sys, json, requests

from pygraylog.api import MetaObjectAPI

class Dashboard(MetaObjectAPI):

	## Creates a dashboard using the given dict.
	# @param dashboard_details a dict with two required keys (description and title).
	# @throw TypeError the given variable is not a dict
	# @throw ValueError some required keys are missing in the given dashboard_details dict
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def create(self, dashboard_details):
		if type(dashboard_details) is not dict:
			self.error_msg = "given dashboard_details must be a dict."
			raise TypeError

		if 'description' not in dashboard_details or 'title' not in dashboard_details:
			self.error_msg = "Some parameters are missing, required: description, title."
			raise ValueError

		self._validation_schema =  super(Dashboard, self)._get_validation_schema("dashboards")['models']['CreateDashboardRequest']

		return super(Dashboard, self)._create("dashboards", dashboard_details)

	## Removes a previously loaded dashboard from the server.
	# The key 'id' from self._data is used.
	# @throw TypeError the given variable is not a dict
	# @throw ValueError the key named 'dashboardname' is missing in the loaded data
	# @throw IOError HTTP code >= 500
	# @return True if succeded
	def delete(self):
		if self._data == None or 'id' not in self._data:
			self.error_msg = "The object is empty: no id available."
			raise ValueError

		return super(Dashboard, self).delete("dashboards", self._data['id'])

	## Tells if a dashboardname exists in the server's database.
	# @param dashboardname the dashboard to find
	# @throw ValueError the given dashboardname is empty
	# @throw IOError HTTP code >= 500
	# @return True if found
	def find_by_id(self, id):
		return super(Dashboard, self).find_by_id("dashboards", id)

	## Tells if a dashboardname exists in the server's database.
	# @param dashboardname the dashboard to find
	# @throw ValueError the given dashboardname is empty
	# @throw IOError HTTP code >= 500
	# @return the id or None
	def find_by_title(self, title):
		if len(title) == 0:
			self.error_msg = "given title is too short."
			raise ValueError

		_url = "%s/%s" % (self._url, 'dashboards')

		r = requests.get(_url, auth=(self._login, self._password))

		if r.status_code >= 500:
			self.error_msg = r.text
			raise IOError

		if r.status_code == 404:
			self._response = r.json()
			return None

		for (i, dashboard) in enumerate(r.json()['dashboards']):
			if dashboard['title'] == title:
				return dashboard['id']

		return None

	## Loads a dashboardname from the server's database.
	# @param id the dashboard to find
	# @throw ValueError the given dashboardname is empty
	# @throw IOError HTTP code >= 500
	# @return True if found and loaded
	def load_from_server(self, id):
		return super(Dashboard, self)._load_from_server("dashboards", id)

	def backup(self, id):
		return self._backup2("dashboards", id)

	def backup_all(self):
		return self._backup1("dashboards")
