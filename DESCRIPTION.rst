Python module for Graylog
=========================

Overview
--------

This set of modules acts as a gateway between Python code and Graylog's HTTP
REST API.

Basically, common python modules are used, such as json, resquests, re or abc.
This is simple to install and use.

What's new
----------

For instance this is not a production-ready release.


Usage
-----
<pre>
from pygraylog.control import InputControl, StreamControl

input = InputControl('localhost', 12900, 'my user', 'my pass', '5229296d808e9f943f848cf42e377fb1', 'launch')

try:
  if not input.perform():
    print "Action failed %s", input.failed_stuff
  else:
    print "Action completed"
except:
  print "API exception: %s", input.error_msg
</pre>
