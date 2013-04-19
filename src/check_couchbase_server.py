#!/usr/bin/env python
from optparse import OptionParser
import requests
import json

parser = OptionParser()
#options
parser.add_option('-I', dest='ip')
parser.add_option('-s', dest='server')
parser.add_option('-u', dest='username')
parser.add_option('-p', dest='password')
parser.add_option('-b', dest='bucket')
options, args = parser.parse_args()

try:
    url = ''.join(['http://', options.ip, '/pools/', options.server, '/buckets/',  options.bucket])
    r = requests.get(url, auth=(options.username, options.password))
    result = r.json()
    for key, values in result.items():
        print key,": ", values
except Exception:
    print "Invalid option combination"
    print "Try '--help' for more information "

