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
def get_status(required_status):
	count = 0
	cbstats = os.popen(''.join([options.cbstat, ' ', options.server, ':11210 ', '-b ', options.bucket, ' all']))
	for status in cbstats.readlines():
		count += 1
		if count == required_status:
			# parse status value
			splitter = re.compile(r'\D')
			status = int(splitter.split(status).pop(-2))
			return status

def check_levels(message, status_value):
	# convert to mb
	status_value_mb = status_value/(1024.0**2)
	if status_value >= options.critical:
		print "CRITICAL - " + message, status_value_mb
		return sys.exit(nagios_codes['CRITICAL'])
	elif status_value >= options.warning:
		print "WARNING - " + message, status_value_mb
		return sys.exit(nagios_codes['WARNING'])
	else:
		print "OK - " + message, status_value_mb
		return sys.exit(nagios_codes['OK'])

def check_disk_write_queue():
	ep_queue_size = get_status(135)
	ep_flusher_todo = get_status(76)
	disk_write_queue = ep_queue_size + ep_flusher_todo
	check_levels("CB disk write queue: ", disk_write_queue)

def check_set_per_sec():
	cmd_set = get_status(14)
	check_levels("CB set per sec: ", cmd_set)

def check_update_per_sec():
	vb_active_ops_update = get_status(216)
	vb_replica_ops_update = get_status(259)
	vb_pending_ops_update = get_status(238)
	updates_per_sec = vb_active_ops_update + vb_replica_ops_update
	updates_per_sec += vb_pending_ops_update
	check_levels("CB disk updates per sec: ", updates_per_sec)

def check_create_per_sec():
	vb_active_ops_create = get_status(213)
	vb_replica_ops_create = get_status(256)
	vb_pending_ops_create = get_status(235)
	create_per_sec = vb_active_ops_create + vb_replica_ops_create 
	create_per_sec += vb_pending_ops_create
	check_levels("CB disk creates per sec: ", create_per_sec)

def check_cache_miss_ratio():
	ep_bg_fetched = get_status(38)
	cmd_get = get_status(13)
	if cmd_get == 0:
		check_levels("CB cache miss ratio: ", 0)
	else:
		cache_miss_ratio = ep_bg_fetched*1.0/cmd_get
		check_levels("CB cache miss ratio: ", cache_miss_ratio)

def check_disk_read_per_sec():
	disk_read = get_status(38)
	check_levels("CB disk read per sec: ", disk_read)
		
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

def check_ops_per_second():
	cmd_get = get_status(13)
	cmd_set = get_status(14)
	incr_misses = get_status(186)
	incr_hits = get_status(187)
	decr_misses = get_status(24)
	decr_hits = get_status(25)
	delete_misses = get_status(26)
	delete_hits = get_status(27)
	ops_per_sec = cmd_get + cmd_set + incr_misses + incr_hits + decr_misses
	ops_per_sec = decr_hits + delete_misses + delete_hits
	check_levels("CB ops per sec: ", ops_per_sec)
	
def check_mem_used():
	mem_used = get_status(193)
	check_levels("CB memory used: ", mem_used)

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
	ep_mem_high_wat = get_status(109)
	check_levels("CB high watermark: ", ep_mem_high_wat)

# which argument 
def which_argument(result):
	if options.operations_per_second:
		check_ops_per_second()
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
	if options.mem_used:
		check_mem_used()
		arg = True
	if options.disk_read:
		check_disk_read_per_sec()
		arg = True
	if options.item_count:
		check_item_count()
		arg = True
	if options.cache_miss_ratio:
		check_cache_miss_ratio()
		arg = True
	if options.create_per_sec:
		check_create_per_sec()
		arg = True
	if options.update_per_sec:
		check_update_per_sec()
		arg = True
	if options.set_per_sec:
		check_set_per_sec()
		arg = True
	if options.disk_write_queue:
		check_disk_write_queue()
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
parser.add_option('--memory-used', action='callback', callback=option_none, dest='mem_used')
parser.add_option('--disk-read', action='callback', callback=option_none, dest='disk_read')
parser.add_option('--item-count', action='callback', callback=option_none, dest='item_count')
parser.add_option('--CAS', action='callback', callback=option_none, dest='cas')
parser.add_option('--del-per-second', action='callback', callback=option_none, dest='del_ps_check')
parser.add_option('--low-watermark', action='callback', callback=option_none, dest='low_watermark')
parser.add_option('--high-watermark', action='callback', callback=option_none, dest='high_watermark')
parser.add_option('--cbstat',  dest='cbstat')
parser.add_option('--cache-miss-ratio', action='callback', callback=option_none, dest='cache_miss_ratio')
parser.add_option('--create-per-sec', action='callback', callback=option_none, dest='create_per_sec')
parser.add_option('--update-per-sec', action='callback', callback=option_none, dest='update_per_sec')
parser.add_option('--set-per-sec', action='callback', callback=option_none, dest='set_per_sec')
parser.add_option('--disk-write-queue', action='callback', callback=option_none, dest='disk_write_queue')
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

