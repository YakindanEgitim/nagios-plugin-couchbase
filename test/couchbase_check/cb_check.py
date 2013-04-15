#!/usr/bin/env python
import sys
from optparse import OptionParser
import requests

parser = OptionParser(usage='%prog [options <arg1> <args2> <arg3>]')
parser.add_option('-H', dest='hostname')
parser.add_option('-u', dest='username')
parser.add_option('-p', dest='password')
options, args = parser.parse_args()


r = requests.get(options.hostname, auth=(options.username, options.password))
print r.status_code
