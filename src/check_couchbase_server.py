#!/usr/bin/env python
from optparse import OptionParser
import requests
import json
import sys

ops = False
#option required none
def option_none(option, opt, value, parser):
	if parser.rargs and not parser.rargs[0].startswith('-'):
		print "Option arg error"
		print opt, " option should be empty"
		sys.exit(2)
	global ops
	ops = True
		
def check_ops_per_second(result):
	# basic bucket stats  from json
	basicStats = result['basicStats']
	print "opsPerSec:",  basicStats['opsPerSec']

parser = OptionParser()
parser.disable_interspersed_args()
#options
parser.add_option('-I', dest='ip')
parser.add_option('-s', dest='server')
parser.add_option('-u', dest='username')
parser.add_option('-p', dest='password')
parser.add_option('-b', dest='bucket')
parser.add_option('--OPS', action='callback', callback=option_none, dest='operations_per_second', default="abc")
options, args = parser.parse_args()

try:
	url = ''.join(['http://', options.ip, '/pools/', options.server, '/buckets/',  options.bucket])
	r = requests.get(url, auth=(options.username, options.password))
	result = r.json()
	if ops:
		check_ops_per_second(result)
	else:
		result = json.dumps(result)
		print result


except Exception:
    print "Invalid option combination"
    print "Try '--help' for more information "

