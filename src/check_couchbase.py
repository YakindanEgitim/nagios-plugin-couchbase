#!/usr/bin/env python
# -*- coding: utf-8; -*-
"""
Copyright (C) 2013 - Ebru Akagündüz <ebru.akagunduz@gmail.com>

This file is part of nagios-couchbase-plugin.

nagios-couchbase-plugin is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

nagios-couchbase-plugin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

"""
from optparse import OptionParser
import requests
import json
import sys
import subprocess
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
	cbstats_cmd = ''.join([options.cbstats, ' ', options.ip, ':11210 ', '-b ', options.bucket, ' all', '|grep ', required_status])
	cmd = subprocess.Popen(cbstats_cmd, shell=True, stdout=subprocess.PIPE)
	return_code = cmd.wait()
	stdout = cmd.communicate()[0]
	if return_code != 0:
		print "WARNING - You have entered wrong value for parameters"
		return sys.exit(1)
	stdout_list = stdout.split('\n')
	stdout_list.pop()
	for status in stdout_list:
		# parse cbstat name
		splitter = re.compile(r'\d')
		status_name = splitter.split(status).pop(0)
		status_name = status_name.strip()
		status_name = status_name[:-1]
		if status_name == required_status:
			# parse cbstat value
			splitter = re.compile(r'\D')
			status_value = int(splitter.split(status).pop(-1))
			return status_value

# status level critical, warning, ok
def check_levels(message, status_value, divide):
	size_type = ""
	status = status_value
	if divide:
		# convert to gb
		if status_value >= 1000**3:
			status = status_value/(1000.0**3)
			size_type = "GB"
		# convert to mb
		elif status_value >= 1000.0**2:
			status = status_value/(1000.0**2)
			size_type = "MB"
		# convert to kb
		elif status_value >= 1000:
			status = status_value/1000.0
			size_type = "KB"

	if options.critical > options.warning:
		if status_value >= options.critical:
			print "CRITICAL - " + message, status, size_type
			return sys.exit(nagios_codes['CRITICAL'])
		elif status_value >= options.warning:
			print "WARNING - " + message, status, size_type
			return sys.exit(nagios_codes['WARNING'])
		else:
			print "OK - " + message, status, size_type
			return sys.exit(nagios_codes['OK'])
	else:
		if status_value >= options.warning:
			print "WARNING - " + message, status, size_type
			return sys.exit(nagios_codes['WARNING'])
		elif status_value >= options.critical:
			print "CRITICAL - " + message, status, size_type
			return sys.exit(nagios_codes['CRITICAL'])
		else:
			print "OK - " + message, status, size_type
			return sys.exit(nagios_codes['OK'])

def check_disk_queues(stat_name, message, divide, result):
	if result == None:
		stat_value = get_status(stat_name)
	else:
		op = result['op']
		samples = op['samples']
		stat_value = samples[stat_name].pop()
	check_levels(message, stat_value, divide)

def check_vbucket(stat_name, message, divide, result):
	if result == None:
		stat_value = get_status(stat_name)
	else:
		op = result['op']
		samples = op['samples']
		stat_value = samples[stat_name].pop()
	check_levels(message, stat_value, divide)

# number of gets operations per sec from specific bucket
def check_gets_per_sec(result):
	if result == None:
		status_value = get_status('cmd_get')
	else:
		op = result['op']
		samples = op['samples']
		status_value = samples['cmd_get'].pop()
	check_levels('CB gets per sec', status_value, True)

# size of the disk write queue from specific bucket
def check_disk_write_queue(result):
	if result == None:
		ep_queue_size = get_status('ep_queue_size')
		ep_flusher_todo = get_status('ep_flusher_todo')
	else:
		op = result['op']
		samples = op['samples']
		ep_queue_size = samples['ep_queue_size'].pop()
		ep_flusher_todo = samples['ep_flusher_todo'].pop()
	status_value = ep_queue_size + ep_flusher_todo
	check_levels('CB disk write queue', status_value, False)

# number of set operations 
def check_sets_per_sec(result):
	if result == None:
		status_value = get_status('cmd_set')
	else:
		op = result['op']
		samples = op['samples']
		status_value = samples['cmd_set'].pop()
	check_levels('CB sets per sec', status_value,  True)

# number of existing items updated in specific bucket
def check_disk_updates_per_sec(result):
	if result == None:
		vb_active_ops_update = get_status('vb_active_ops_update')
		vb_replica_ops_update = get_status('vb_replica_ops_update')
		vb_pending_ops_update = get_status('vb_pending_ops_update')
	else:
		op = result['op']
		samples = op['samples']
		vb_active_ops_update = samples['vb_active_ops_update'].pop()
		vb_replica_ops_update = samples['vb_replica_ops_update'].pop()
		vb_pending_ops_update = samples['vb_pending_ops_update'].pop()
	status_value = vb_active_ops_update + vb_replica_ops_update
	status_value += vb_pending_ops_update
	check_levels('CB disk updates per sec', status_value, True)

# number of new items created in specific bucket
def check_disk_creates_per_sec(result):
	if result == None:
		vb_active_ops_create = get_status('vb_active_ops_create')
		vb_replica_ops_create = get_status('vb_replica_ops_create')
		vb_pending_ops_create = get_status('vb_pending_ops_create')
	else:
		op = result['op']
		samples = op['samples']
		vb_active_ops_create = samples['vb_active_ops_create'].pop()
		vb_replica_ops_create = samples['vb_replica_ops_create'].pop()
		vb_pending_ops_create = samples['vb_pending_ops_create'].pop()
	status_value = vb_active_ops_create + vb_replica_ops_create 
	status_value += vb_pending_ops_create
	check_levels("CB disk creates per sec: ", status_value, True)

# percentage of reads per second to specific bucket which required a read from disk rather than RAM.
def check_cache_miss_ratio():
	ep_bg_fetched = get_status('ep_bg_fetched')
	cmd_get = get_status('cmd_get')
	if cmd_get == 0:
		check_levels('CB cache miss ratio', 0, False)
	else:
		status_value = ep_bg_fetched*1.0/cmd_get
		check_levels('CB cache miss ratio', status_value, False)

# number of reads per second from disk for specific bucket
def check_disk_reads_per_sec(result):
	if result == None:
		status_value = get_status('ep_bg_fetched')	
	else:
		op = result['op']
		samples = op['samples']
		status_value = samples['ep_bg_fetched'].pop()
	check_levels('CB disk read per sec', status_value, True)

# item count for specific bucket		
def check_item_count(result):
	if result == None:
		status_value = get_status('curr_items')
	else:
		op = result['op']
		samples = op['samples']
		status_value = samples['curr_items'].pop()
	check_levels('CB item count', status_value, True)

# total operations per second
def check_ops_per_second(result):
	if result == None:
		cmd_get = get_status('cmd_get')
		cmd_set = get_status('cmd_set')
		incr_misses = get_status('incr_misses')
		incr_hits = get_status('incr_hits')
		decr_misses = get_status('decr_misses')
		decr_hits = get_status('decr_hits')
		delete_misses = get_status('delete_misses')
		delete_hits = get_status('delete_hits')
	else:
		op = result['op']
		samples = op['samples']
		cmd_get = samples['cmd_get'].pop()
		cmd_set = samples['cmd_set'].pop()
		incr_misses = samples['incr_misses'].pop()
		incr_hits = samples['incr_hits'].pop()
		decr_misses = samples['decr_misses'].pop()
		decr_hits = samples['decr_hits'].pop()
		delete_misses = samples['delete_misses'].pop()
		delete_hits = samples['delete_hits'].pop()
	status_value = cmd_get + cmd_set + incr_misses + incr_hits + decr_misses
	status_value = decr_hits + delete_misses + delete_hits
	check_levels('CB ops per sec', status_value, True)
		
	
# total amount of ram used by specific bucket
def check_memory_used(result):
	if result == None:
		status_value = get_status('mem_used')
	else:
		op = result['op']
		samples = op['samples']
		status_value = samples['mem_used'].pop()
	check_levels('CB memory used', status_value, True)

# number of CAS operations per sec for data that specific bucket contains
def check_cas_per_sec(result):
	if result == None:
		status_value = get_status('cas_hits')
	else:
		op = result['op']
		samples = op['samples']
		status_value = samples['cas_hits'].pop()
	check_levels('CB cas per sec', status_value, True)
		
# number of delete operations per second for specific bucket
def check_deletes_per_sec(result):
	if result == None:
		status_value = get_status('delete_hits')
	else:
		op = result['op']
		samples = op['samples']
		status_value  = samples['delete_hits'].pop()
	check_levels("CB delete per sec: ", status_value, True)

# low water mark for memory usage
def check_low_watermark(result):
	if result == None:
		status_value = get_status('ep_mem_low_wat')
		check_levels('CB low watermark', status_value, True)
	else:
		op = result['op']
		samples = op['samples']
		ep_mem_low_wat = samples['ep_mem_low_wat']
		status_value = ep_mem_low_wat.pop()
		check_levels('CB low watermark', status_value, True)

# high water mark for memory usage
def check_high_watermark(result):
	if result == None:
		status_value = get_status('ep_mem_high_wat')
	else:
		op = result['op']
		samples = op['samples']
		status_value = samples['ep_mem_high_wat'].pop()
	check_levels('CB high watermark', status_value, True)

def httpWarnings(returnCode):
	if r.status_code == requests.codes.created:
		print "No HTTP response body returns - 201 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.accepted:
		print "Request proccessing is not complete - 202 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.no_content:
		print "No content - 204 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.bad_request:
		print "Bad request - 400 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.unauthorized:
		print "Unauthorized - 401 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.forbidden:
		print "Forbidden - 403 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.not_found:
		print "Not found - 404 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.not_acceptable:
		print "Not acceptable - error 406 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.conflict:
		print "Conflict error- 409 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.internal_server_error:
		print "Internal server error - 500 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.not_implemented:
		print "Not Implemented - 501 error"
		return sys.exit(2)
	elif r.status_code == requests.codes.service_unavailable:
		print "Service error - 503 error"
		return sys.exit(2)		

# which argument 
def which_argument(result):	
	if options.operations_per_second:
		check_ops_per_second(result)
	if options.cas:
		check_cas_per_sec(result)
	if options.high_watermark:
		check_high_watermark(result)
	if options.low_watermark:
		check_low_watermark(result)
	if options.deletes_per_sec:
		check_deletes_per_sec(result)
	if options.memory_used:
		check_memory_used(result)
	if options.disk_reads_per_sec:
		check_disk_reads_per_sec(result)
	if options.item_count:
		check_item_count(result)
	if options.cache_miss_ratio:
		check_cache_miss_ratio()
	# wrong solution
	if options.disk_creates_per_sec:
		check_disk_creates_per_sec(result)
	# wrong solution
	if options.disk_updates_per_sec:
		check_disk_updates_per_sec(result)
	# wrong solution
	if options.sets_per_sec:
		check_sets_per_sec(result)
	if options.disk_write_queue:
		check_disk_write_queue(result)
	if options.gets_per_sec:
		check_gets_per_sec(result)
	
	if options.vbucket_count and options.vbucket:
		if options.active:
			check_vbucket('vb_active_num', 'CB active vBucket count', False, result)
		elif options.replica:
			check_vbucket('vb_replica_num', 'CB replica vBucket count', False, result)
		elif options.pending:
			check_vbucket('vb_pending_num', 'CB pending vBucket count', False, result)
		elif options.total:
			check_vbucket('ep_vb_total', 'CB total vBucket count', False, result)
		else:
			print "wrong options combination"
			sys.exit(2)

	if options.vbucket_items and options.vbucket:
		if options.active:
			check_vbucket('curr_items', 'CB active vBucket items', True, result)
		elif options.replica:
			check_vbucket('vb_replica_curr_items', 'CB replica vBucket items', True, result)
		elif options.pending:
			check_vbucket('vb_pending_curr_items', 'CB pending vBucket items', True, result)
		elif options.total:
			check_vbucket('curr_items_tot', 'CB total vBucket items', True, result)
		else:
			print "wrong options combination"
			sys.exit(2)

	if options.vbucket_new_items and options.vbucket:
		if options.active:
			check_vbucket('vb_active_ops_create', 'CB active vBucket new items', True, result)
		elif options.replica:
			check_vbucket('vb_replica_ops_create', 'CB replica vBucket new items', True, result)
		elif options.pending:
			check_vbucket('vb_pending_ops_create', 'CB pending vBucket new items', True, result)
		else:
			print "wrong options combination"
			sys.exit(2)

	if options.vbucket_ejections and options.vbucket:
		if options.active:
			check_vbucket('vb_active_eject', 'CB active vBucket ejections', True, result)
		elif options.replica:
			check_vbucket('vb_replica_eject', 'CB replica vBucket ejections', True, result)
		elif options.pending:
			check_vbucket('vb_pending_eject', 'CB pending vBucket ejections ', True, result)
		elif options.total:
			check_vbucket('ep_num_value_ejects', 'CB total vBucket ejections', True, result)
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_user_data_ram and options.vbucket:
		if options.active:
			check_vbucket('vb_active_itm_memory', 'CB active vBucket user data', True, result)
		elif options.replica:
			check_vbucket('vb_replica_itm_memory', 'CB replica vBucket user data', True, result)
		elif options.pending:
			check_vbucket('vb_pending_itm_memory', 'CB pending vBucket user data', True, result)
		elif options.total:
			check_vbucket('ep_kv_size', 'CB total vBucket user data', True, result)
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_meta_data_ram and options.vbucket:
		if options.active:
			check_vbucket('vb_active_meta_data_memory', 'CB active vBucket meta data', True, result)
		elif options.replica:
			check_vbucket('vb_replica_meta_data_memory', 'CB replica vBucket meta data', True, result)
		elif options.pending:
			check_vbucket('vb_pending_meta_data_memory', 'CB pending vBucket meta data', True, result)
		else:
			print "wrong options combination"
			sys.exit(2)

	if options.disk_queues_items and options.disk_queues:
		if options.active:
			check_disk_queues('vb_active_queue_size', 'CB active disk Queues items', True, result)
		elif options.replica:
			check_disk_queues('vb_replica_queue_size', 'CB replica disk Queues items', True, result)
		elif options.pending:
			check_disk_queues('vb_pending_queue_size', 'CB pending disk Queues items', True, result)
		elif options.total:
			check_disk_queues('vb_total_queue_size', 'CB total  disk Queues items', True, result)
		else:
			print "wrong options combination"
			return sys.exit(2)
	if options.disk_queues_fill_rate and options.disk_queues:
		if options.pending:
			check_disk_queues('vb_pending_queue_fill',  'CB pending disk Queues fill rate', True, result)
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.disk_queues_drain_rate and options.disk_queues:
		if options.pending:
			check_disk_queues('vb_pending_queue_drain', 'CB pending disk Queues drain rate', True, result)
		else:
			print "wrong options combination"
			sys.exit(2)
	else:
		print "wrong options combination"
		return sys.exit(2)

# option parse
parser = OptionParser()
parser.disable_interspersed_args()
arg = False

#option define
parser.add_option('-I', dest='ip', help='Ip adress')
parser.add_option('-u', dest='username', help='User name for CouchBase')
parser.add_option('-p', dest='password', help='password for CouchBase authorization')
parser.add_option('-P', '--port', dest='port', help='Port for CouchBase')
parser.add_option('-b', '--bucket', dest='bucket', help='A bucket name on CouchBase')
parser.add_option('-W', type='int', dest='warning', help='Warning treshold for statistic on CouchBase')
parser.add_option('-C', type='int', dest='critical', help='Critical treshold for statistic on CouchBase')
parser.add_option('--OPS', '--operations-per-sec', action='callback', callback=option_none, dest='operations_per_second', help='Operations per second for specific bucket on Couchbase')
parser.add_option('--memory-used', action='callback', callback=option_none, dest='memory_used', help='Memory used for specific bucket on Couchbase')
parser.add_option('--disk-reads-per-sec', action='callback', callback=option_none, dest='disk_reads_per_sec', help='Disk reads per second for specific bucket on Couchbase')
parser.add_option('--item-count', action='callback', callback=option_none, dest='item_count', help='Item counts for specific bucket on Couchbase')
parser.add_option('--CAS', action='callback', callback=option_none, dest='cas', help='Check and set operations on CouchBase')
parser.add_option('--deletes-per-sec', action='callback', callback=option_none, dest='deletes_per_sec', help='Deletes per second for specific bucket on Couchbase')
parser.add_option('--low-watermark', action='callback', callback=option_none, dest='low_watermark', help='Low watermark for specific bucket on Couchbase')
parser.add_option('--high-watermark', action='callback', callback=option_none, dest='high_watermark', help='High watermark for specific bucket on Couchbase')
parser.add_option('--cbstats', default='/opt/couchbase/bin/cbstats', dest='cbstats', help='cbstats command full path for nagios plugin couchbase')
parser.add_option('--cache-miss-ratio', action='callback', callback=option_none, dest='cache_miss_ratio', help='Percentage of reads per second from specific bucket')
parser.add_option('--disk-creates-per-sec', action='callback', callback=option_none, dest='disk_creates_per_sec', help='Disk creates per second check for Couchbase statistic')
parser.add_option('--disk-updates-per-sec', action='callback', callback=option_none, dest='disk_updates_per_sec', help='Disk updates per second')
parser.add_option('--sets-per-sec', action='callback', callback=option_none, dest='sets_per_sec', help='Number of set/update operations per second for specific bucket')
parser.add_option('--gets-per-sec', action='callback', callback=option_none, dest='gets_per_sec', help='Number of get operations serviced by specific bucket')
parser.add_option('--disk-write-queue', action='callback', callback=option_none, dest='disk_write_queue', help='Size of the disk write queue for specific bucket')
parser.add_option('--vbucket-count', action='callback', callback=option_none, dest='vbucket_count', help='The number of vBuckets within the specified state')
parser.add_option('--vbucket', action='callback', callback=option_none, dest='vbucket', help='Any of vBuckets resources checks')
parser.add_option('--active', action='callback', callback=option_none, dest='active', help='active state for vBuckets')
parser.add_option('--replica', action='callback', callback=option_none, dest='replica', help='replica state for vBuckets')
parser.add_option('--pending', action='callback', callback=option_none, dest='pending', help='pending state for vBuckets')
parser.add_option('--total', action='callback', callback=option_none, dest='total', help='total state for vBuckets')
parser.add_option('--items', action='callback', callback=option_none, dest='vbucket_items', help='Number of items within the vBucket of the specified state')
parser.add_option('--resident', action='callback', callback=option_none, dest='vbucket_resident', help='Percentage of items within the vBuckets of the specified state that are resident (in RAM)')
parser.add_option('--new-items', action='callback', callback=option_none, dest='vbucket_new_items', help='Number of new items created in vBuckets')
parser.add_option('--ejections', action='callback', callback=option_none, dest='vbucket_ejections', help='Number of items ejected per second within the vBuckets of the specified state')
parser.add_option('--user-data-ram', action='callback', callback=option_none, dest='vbucket_user_data_ram', help='Size of user data within vBuckets of the specified state that are resident in RAM')
parser.add_option('--meta-data-ram', action='callback', callback=option_none, dest='vbucket_meta_data_ram', help='Size of item metadata within the vBuckets of the specified state that are resident in RAM')
parser.add_option('--disk-queues', action='callback', callback=option_none, dest='disk_queues', help='displays the information for data being placed into the disk queue')
parser.add_option('--disk-items', action='callback', callback=option_none, dest='disk_queues_items', help='The number of items waiting to be written to disk for this bucket for this state')
parser.add_option('--fill-rate', action='callback', callback=option_none, dest='disk_queues_fill_rate', help='The number of items per second being added to the disk queue for the corresponding state')
parser.add_option('--drain-rate', action='callback', callback=option_none, dest='disk_queues_drain_rate', help='Number of items actually written to disk from the disk queue for the corresponding state')
parser.add_option('--node', action='callback', callback=option_none, dest='node', help='get couchbase statistics at node level')
options, args = parser.parse_args()

try:
	if options.node:
		which_argument(None)
	else:
		url = ''.join(['http://', options.ip, ':', options.port, '/pools/default/buckets/', options.bucket, '/stats/'])
		r = requests.get(url, auth=(options.username, options.password))
		httpWarnings(r.status_code)
		result = r.json()
		which_argument(result)
		
except Exception:
    print "Invalid option combination"
    print "Try '--help' for more information "

