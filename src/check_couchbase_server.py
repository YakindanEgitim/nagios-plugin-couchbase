#!/usr/bin/env python
from optparse import OptionParser
import requests
import json
import sys
import os
import re

nagios_codes = {'OK': 0, 'WARNING': 1, 'CRITICAL': 2, 'UNKNOWN':3, 'DEPENDENT':4,}

#option required none
def option_none(option, opt, value, parser):
	if parser.rargs and not parser.rargs[0].startswith('-'):
		print "Option arg error"
		print opt, " option should be empty"
		sys.exit(2)
	setattr(parser.values, option.dest, True)
	
# get specific status using cbstat
def get_status(required_status, message):
	count = 0
	cbstats = os.popen(''.join([options.cbstat, ' ', options.server, ':11210 ', '-b ', options.bucket, ' all']))
	for status in cbstats.readlines():
		count += 1
		if count == required_status:
			# parse status value
			splitter = re.compile(r'\D')
			status = int(splitter.split(status).pop(-2))
			# convert to mb
			status_mb = status/(1024.0**2)
			if status >= options.critical:
				print "CRITICAL - " + message, status_mb
				return sys.exit(nagios_codes['CRITICAL'])
			elif status >= options.warning:
				print "WARNING - " + message, status_mb
			else:
				print "OK - " + message, status_mb

def check_disk_read_per_sec():
	get_status(38, "CB disk read per sec: ")
		
def check_item_count():
	count = 0
	cbstats = os.popen(''.join([options.cbstat, ' ', options.server, ':11210 ', '-b ', options.bucket, ' all']))
	for stat in cbstats.readlines():
		count += 1
		if count == 20:
			# parse item count from string
			splitter = re.compile(r'\D')
			item_count = int(splitter.split(stat).pop(-2))
			# convert byte to mb
			item_count_mb = item_count/(1024.0**2)
			if item_count >= options.critical:
				print "CB item count CRITICAL ", item_count_mb, " MB"
				return sys.exit(nagios_codes['CRITICAL'])
			elif item_count >= options.warning:
				print "CB item count WARNING ", item_count_mb, " MB"
				return sys.exit(nagios_codes['WARNING'])
			else:
				print "CB item count OK ", item_count_mb, " MB"
				sys.exit(nagios_codes['OK'])

def check_ops_per_second(result):
	# basic bucket stats  from json
	basicStats = result['basicStats']
	opsPerSec =  basicStats['opsPerSec']
	if opsPerSec >= options.critical:
		print "CB operation per second CRITICAL ", opsPerSec
		return sys.exit(nagios_codes['CRITICAL'])
	elif opsPerSec >= options.warning:
		print "CB operation per second WARNING ", opsPerSec
		return sys.exit(nagios_codes['WARNING'])
	else:
		print "CB operation per second OK ", opsPerSec
		return sys.exit(nagios_codes['OK'])

def check_mem_usage(result):
	basicStats = result['basicStats']
	nodes = result['nodes']
	nodes = dict(nodes[0])
	mem_used = basicStats['memUsed']
	# convert mb
	mem_used_mb = basicStats['memUsed']/(1024.0**2)
	if mem_used >= options.critical:
		print "CB memory used CRITICAL ", mem_used_mb, " MB"
		return sys.exit(nagios_codes['CRITICAL'])
	elif mem_used >= options.warning:
		print "CB memory used  WARNING ", mem_used_mb, " MB"
		return sys.exit(nagios_codes['WARNING'])
	else:
		print "CB memory used  OK ", mem_used_mb, " MB"
		return sys.exit(nagios_codes['OK'])

def check_cas_per_second():
	count = 0
	cbstats = os.popen(''.join([options.cbstat, ' ', options.server, ':11210 ', '-b ', options.bucket, ' all']))
	for stat in cbstats.readlines():
		count += 1
		if count == 10:
			# parse cas
			splitter = re.compile(r'\D')
			cas = int(splitter.split(stat).pop(-2))
			if cas >= options.critical:
				print "CB CAS  CRITICAL ", cas
				return sys.exit(nagios_codes['CRITICAL'])
			elif cas >= options.warning:
				print "CB CAS  WARNING ", cas
				return sys.exit(nagios_codes['WARNING'])
			else:
				print "CouchBase CAS  OK ", cas
				return sys.exit(nagios_codes['OK'])
		
def check_del_per_second():
	count = 0
	cbstats = os.popen(''.join([options.cbstat, ' ', options.server, ':11210 ', '-b ', options.bucket, ' all']))
	for stat in cbstats.readlines():
		count += 1
		if count == 120:
			# parse delete per second 
			splitter = re.compile(r'\D')
			del_per_sec = int(splitter.split(stat).pop(-2))
			if del_per_sec >= options.critical:
				print "CB deletes per second  CRITICAL ", del_per_sec
				return sys.exit(nagios_codes['CRITICAL'])
			elif del_per_sec >= options.warning:
				print "CB deletes per second  WARNING ", del_per_sec
				return sys.exit(nagios_codes['WARNING'])
			else:
				print "CB deletes per second OK ", del_per_sec
				return sys.exit(nagios_codes['OK'])

def check_low_watermark():
	count = 0
	cbstats = os.popen(''.join([options.cbstat, ' ', options.server, ':11210 ', '-b ', options.bucket, ' all']))
	for stat in cbstats.readlines():
		count += 1
		if count == 110:
			# parse low warermark from string
			splitter = re.compile(r'\D')
			low_watermark = int(splitter.split(stat).pop(-2))
			# convert to mb
			low_watermark_mb = low_watermark/(1024.0**2)
			if low_watermark >= options.critical:
				print "CB low water mark  CRITICAL ", low_watermark_mb, " MB"
				return sys.exit(nagios_codes['CRITICAL'])
			elif low_watermark >= options.warning:
				print "CB low water mark  WARNING ", low_watermark_mb, " MB"
				return sys.exit(nagios_codes['WARNING'])
			else:
				print "CB low water mark  OK ", low_watermark_mb, " MB"
				return sys.exit(nagios_codes['OK'])

def check_high_watermark():
	count = 0
	cbstats = os.popen(''.join([options.cbstat, ' ', options.server, ':11210 ', '-b ', options.bucket, ' all']))
	for stat in cbstats.readlines():
		count += 1
		if count == 109:
			# parse high watermark from string
			splitter = re.compile(r'\D')
			high_watermark = int(splitter.split(stat).pop(-2))
			# convert to mb
			high_watermark_mb = stat/(1024.0**2)
			if high_watermark >= options.critical:
				print "CouchBase high water mark  CRITICAL ", high_watermark_mb, " MB"
				return sys.exit(nagios_codes['CRITICAL'])
			elif high_watermark >= options.warning:
				print "CouchBase high water mark  WARNING ", high_watermark_mb, " MB"
				return sys.exit(nagios_codes['WARNING'])
			else:
				print "CouchBase high water mark  OK ", high_watermark_mb, " MB"
				return sys.exit(nagios_codes['OK'])
# which argument 
def which_argument(result):
	if options.operations_per_second:
		check_ops_per_second(result)
		arg = True
	if options.cas:
		check_cas_per_second()
		arg = True
	if options.high_watermark:
		check_high_watermark()
		arg = True
	if options.low_watermark:
		check_low_watermark()
		arg = True
	if options.del_ps_check:
		check_del_per_second()
		arg = True
	if options.memoryUsage:
		check_mem_usage(result)
		arg = True
	if options.disk_read:
		check_disk_read_per_sec()
		arg = True
	if options.item_count:
		check_item_count()
		arg = True
	if not arg:
		result = json.dumps(result)
		print result


# option parse
parser = OptionParser()
parser.disable_interspersed_args()
arg = False

#option define
parser.add_option('-I', dest='ip')
parser.add_option('-s', dest='server')
parser.add_option('-u', dest='username')
parser.add_option('-p', dest='password')
parser.add_option('-P', dest='port')
parser.add_option('-b', dest='bucket')
parser.add_option('-W', type='int', dest='warning')
parser.add_option('-C', type='int', dest='critical')
parser.add_option('--OPS', action='callback', callback=option_none, dest='operations_per_second')
parser.add_option('--mem', action='callback', callback=option_none, dest='memoryUsage')
parser.add_option('--disk-read', action='callback', callback=option_none, dest='disk_read')
parser.add_option('--item-count', action='callback', callback=option_none, dest='item_count')
parser.add_option('--CAS', action='callback', callback=option_none, dest='cas')
parser.add_option('--del-per-second', action='callback', callback=option_none, dest='del_ps_check')
parser.add_option('--low-watermark', action='callback', callback=option_none, dest='low_watermark')
parser.add_option('--high-watermark', action='callback', callback=option_none, dest='high_watermark')
parser.add_option('--cbstat',  dest='cbstat')
options, args = parser.parse_args()

try:
	url = ''.join(['http://', options.ip, ':', options.port, '/pools/', options.server, '/buckets/',  options.bucket])
	r = requests.get(url, auth=(options.username, options.password))
	if r.status_code == 200:
		result = r.json()
		which_argument(result)
	elif r.status_code == 201:
		print "201 Created\n Request to create a new resource is successful, but no HTTP response body returns. "
		print "Request to create a new resource is successful, but no HTTP response body returns."
	elif r.status_code == 202:
		print "202 Accepted"
		print "The request is accepted for processing, but processing is not complete."
	elif r.status_code == 204:
		print "204 No Content"
		print "The server fulfilled the request, but does not need to return a response body."
	elif r.status_code == 400:
		print "400 Bad Request"
		print "The request could not be processed because it contains missing or invalid information"
	elif r.status_code == 401:
		print "401 Unauthorized"
		print "The credentials provided with this request are missing or invalid."
	elif r.status_code == 403:
		print "403 Forbidden"
		print "The server recognized the given credentials, but you do not possess proper access to perform this request."
	elif r.status_code == 404:
		print "404 Not Found"
		print "URI you provided in a request does not exist."
	elif r.status_code == 405:
		print "405 Method Not Allowed"
	elif r.status_code == 406:
		print "406 Not Acceptable"		
	elif r.status_code == 409:
		print "409 Conflict"
	elif r.status_code == 500:
		print "500 Internal Server Error"
	elif r.status_code == 501:
		print "501 Not Implemented"
	elif r.status_code == 503:
		print "503 Service Unavailable"
except Exception:
    print "Invalid option combination"
    print "Try '--help' for more information "

