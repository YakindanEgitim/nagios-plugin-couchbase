#!/usr/bin/env python
from optparse import OptionParser
import requests
import json

#option required none
def option_none(option, opt, value, parser):
    if  parser.rargs and not parser.rargs[0].startswith('-'):
        print "Option arg error"
        print opt, " option should be empty"
        sys.exit(2)

parser = OptionParser()
parser.disable_interspersed_args()
#options
parser.add_option('-I', dest='ip')
parser.add_option('-s', dest='server')
parser.add_option('-u', dest='username')
parser.add_option('-p', dest='password')
parser.add_option('-b', dest='bucket')
parser.add_option('--OPS', action='callback', callback=option_none)
options, args = parser.parse_args()

try:
	url = ''.join(['http://', options.ip, '/pools/', options.server, '/buckets/',  options.bucket])
	r = requests.get(url, auth=(options.username, options.password))
	result = r.json()
	result = json.dumps(result)
#	print type(result)
#	print result.split("\"opsPerSec\":")
	print result
#	result.index()

except Exception:
    print "Invalid option combination"
    print "Try '--help' for more information "

