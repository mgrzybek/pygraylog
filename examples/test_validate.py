#! /usr/bin/env python

import sys, json, requests
from jsonschema import validate

schema = {
u'id': u'urn:jsonschema:org:graylog2:rest:resources:users:responses:User',
u'properties': {u'read_only': {u'type': u'boolean'},
u'username': {u'type': u'string'},
u'session_timeout_ms': {u'type': u'integer'},
u'email': {u'type': u'string'},
u'startpage': {u'additional_properties': {u'type': u'string'}, u'type': u'object'},
u'external': {u'type': u'boolean'},
u'full_name': {u'type': u'string'},
u'timezone': {u'type': u'string'},
u'permissions': {u'items': {u'type': u'string'}, u'type': u'array'}, u'id': {u'type': u'string'}, u'preferences': {u'additional_properties': {u'type': u'any'}, u'type': u'object'}}
	  }

user = { u'email' : 'tdmarmerie.fr', u'password' : u'prout', u'permissions' : [ u'*' ] }

validate(user, schema)

