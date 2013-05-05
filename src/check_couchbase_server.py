#!/usr/bin/env python
from optparse import OptionParser
import requests
import json
import sys
import os

nagios_codes = {'OK': 0, 'WARNING': 1, 'CRITICAL': 2,}

#option required none
def option_none(option, opt, value, parser):
	if parser.rargs and not parser.rargs[0].startswith('-'):
		print "Option arg error"
		print opt, " option should be empty"
		sys.exit(2)
	setattr(parser.values, option.dest, True)

def check_item_count(result):
	basicStats = result['basicStats']
	item_count = basicStats['itemCount']
	print "Item count: ", item_count

def check_ops_per_second(result):
	# basic bucket stats  from json
	basicStats = result['basicStats']
#	print "opsPerSecc:: ",  basicStats['opsPerSec']
	opsPerSec =  basicStats['opsPerSec']
	options.warning = float(options.warning)
	options.critical = float(options.critical)
	if opsPerSec == 0.0 or opsPerSec <= options.warning:
		print "WARNING"
		print nagios_codes['WARNING']
		return sys.exit(nagios_codes['WARNING'])
	elif opsPerSec <= options.critical:
		print "CRITICAL"
		return sys.exit(nagios_codes['CRITICAL'])
	else:
		print "OK"
		return sys.exit(nagios_codes['OK'])

def check_mem_usage(result):
	basicStats = result['basicStats']
	print "memUsed: ", basicStats['memUsed']
	nodes = result['nodes']
	nodes = dict(nodes[0])
	interestingStats = nodes['interestingStats']
	print "nodes:  "
	print "memoryFree: ", nodes['memoryFree']
	print "memoryTotal: ", nodes['memoryTotal']
	print "interestingStats MemUsed: ", interestingStats['mem_used']

def check_disk_read(result):
	basicStats = result['basicStats']
	print "diskFetches:", basicStats['diskFetches']

def check_cas_per_second():
	count = 0
	cbstats = os.popen(''.join(['/opt/couchbase/bin/cbstats ', options.server, ':11210 ', '-b ', options.bucket, ' all']))
	for stat in cbstats.readlines():
		count += 1
		if count == 10:
			print stat

def check_del_per_second():
	count = 0
	cbstats = os.popen(''.join(['/opt/couchbase/bin/cbstats ', options.server, ':11210 ', '-b ', options.bucket, ' all']))
	for stat in cbstats.readlines():
		count += 1
		if count == 120:
			print stat	

parser = OptionParser()
parser.disable_interspersed_args()
arg = False

#options
parser.add_option('-I', dest='ip')
parser.add_option('-s', dest='server')
parser.add_option('-u', dest='username')
parser.add_option('-p', dest='password')
parser.add_option('-P', dest='port')
parser.add_option('-b', dest='bucket')
parser.add_option('-W', dest='warning')
parser.add_option('-C', dest='critical')
parser.add_option('--OPS', action='callback', callback=option_none, dest='operations_per_second')
parser.add_option('--mem', action='callback', callback=option_none, dest='memoryUsage')
parser.add_option('--disk-read', action='callback', callback=option_none, dest='disk_read')
parser.add_option('--item-count', action='callback', callback=option_none, dest='item_count')
parser.add_option('--CAS', action='callback', callback=option_none, dest='cas')
parser.add_option('--del-ps-check', action='callback', callback=option_none, dest='del_ps_check')
options, args = parser.parse_args()

try:
	url = ''.join(['http://', options.ip, ':', options.port, '/pools/', options.server, '/buckets/',  options.bucket])
	r = requests.get(url, auth=(options.username, options.password))
	result = r.json()
	if options.operations_per_second:
		check_ops_per_second(result)
		arg = True
	if options.cas:
		check_cas_per_second()
		arg = True
	if options.del_ps_check:
		check_del_per_second()
		arg = True
	if options.memoryUsage:
		check_mem_usage(result)
		arg = True
	if options.disk_read:
		check_disk_read(result)
		arg = True
	if options.item_count:
		check_item_count(result)
		arg = True
	if not arg:
		result = json.dumps(result)
		print result
except Exception:
    print "Invalid option combination"
    print "Try '--help' for more information "

