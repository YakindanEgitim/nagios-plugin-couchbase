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
	cbstats = os.popen(''.join([options.cbstat, ' ', options.ip, ':11210 ', '-b ', options.bucket, ' all', '|grep ', required_status]))
	for status in cbstats.readlines():
		# parse cbstat name
		splitter = re.compile(r'\d')
		status_name = splitter.split(status).pop(0)
		status_name = status_name.strip()
		status_name = status_name[:-1]
		if status_name == required_status:
			# parse cbstat value
			splitter = re.compile(r'\D')
			status_value = int(splitter.split(status).pop(-2))
			return status_value

def check_levels(message, status_value, divide):
	size_type = ""
	status = status_value
	if divide:
		# convert to gb
		if status_value >= 1024**3:
			status = status_value/(1024.0**3)
			size_type = "GB"
		# convert to mb
		elif status_value >= 1024.0**2:
			status = status_value/(1024.0**2)
			size_type = "MB"
		# convert to kb
		elif status_value >= 1024:
			status = status_value/1024.0
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

def check_vbucket(stat_name, message, divide):
	stat_value = get_status(stat_name)
	check_levels(message, stat_value, divide)

def check_gets_per_sec():
	status_value = get_status('cmd_get')
	check_levels('CB gets per sec', status_value, True)

def check_disk_write_queue():
	ep_queue_size = get_status('ep_queue_size')
	ep_flusher_todo = get_status('ep_flusher_todo')
	status_value = ep_queue_size + ep_flusher_todo
	check_levels('CB disk write queue', status_value, False)

def check_sets_per_sec():
	status_value = get_status('cmd_set')
	check_levels('CB sets per sec', status_value,  True)

def check_disk_updates_per_sec():
	vb_active_ops_update = get_status('vb_active_ops_update')
	vb_replica_ops_update = get_status('vb_replica_ops_update')
	vb_pending_ops_update = get_status('vb_pending_ops_update')
	status_value = vb_active_ops_update + vb_replica_ops_update
	status_value += vb_pending_ops_update
	check_levels('CB disk updates per sec', status_value, True)

def check_disk_creates_per_sec():
	vb_active_ops_create = get_status('vb_active_ops_create')
	vb_replica_ops_create = get_status('vb_replica_ops_create')
	vb_pending_ops_create = get_status('vb_pending_ops_create')
	status_value = vb_active_ops_create + vb_replica_ops_create 
	status_value += vb_pending_ops_create
	check_levels("CB disk creates per sec: ", status_value, True)

def check_cache_miss_ratio():
	ep_bg_fetched = get_status('ep_bg_fetched')
	cmd_get = get_status('cmd_get')
	if cmd_get == 0:
		check_levels('CB cache miss ratio', 0, False)
	else:
		status_value = ep_bg_fetched*1.0/cmd_get
		check_levels('CB cache miss ratio', status_value, False)

def check_disk_reads_per_sec():
	status_value = get_status('ep_bg_fetched')
	check_levels('CB disk read per sec', status_value, True)
		
def check_item_count():
	status_value = get_status('curr_items')
	check_levels('CB item count', status_value, True)

def check_ops_per_second():
	cmd_get = get_status('cmd_get')
	cmd_set = get_status('cmd_set')
	incr_misses = get_status('incr_misses')
	incr_hits = get_status('incr_hits')
	decr_misses = get_status('decr_misses')
	decr_hits = get_status('decr_hits')
	delete_misses = get_status('delete_misses')
	delete_hits = get_status('delete_hits')
	status_value = cmd_get + cmd_set + incr_misses + incr_hits + decr_misses
	status_value = decr_hits + delete_misses + delete_hits
	check_levels('CB ops per sec', status_value, True)
	
def check_memory_used():
	status_value = get_status('mem_used')
	check_levels('CB memory used', status_value, True)

def check_cas_per_sec():
	status_value = get_status('cas_hits')
	check_levels('CB cas per sec', status_value, True)
		
def check_deletes_per_sec():
	status_value = get_status('delete_hits')
	check_levels("CB delete per sec: ", status_value, True)

def check_low_watermark():
	status_value = get_status('ep_mem_low_wat')
	check_levels('CB low watermark', status_value, True)

def check_high_watermark():
	status_value = get_status('ep_mem_high_wat')
	check_levels('CB high watermark', status_value, True)

# which argument 
def which_argument():
	if options.operations_per_second:
		check_ops_per_second()
	if options.cas:
		check_cas_per_sec()
	if options.high_watermark:
		check_high_watermark()
	if options.low_watermark:
		check_low_watermark()
	if options.deletes_per_sec:
		check_deletes_per_sec()
	if options.memory_used:
		check_memory_used()
	if options.disk_reads_per_sec:
		check_disk_reads_per_sec()
	if options.item_count:
		check_item_count()
	if options.cache_miss_ratio:
		check_cache_miss_ratio()
	# wrong solution
	if options.disk_creates_per_sec:
		check_disk_creates_per_sec()
	# wrong solution
	if options.disk_updates_per_sec:
		check_disk_updates_per_sec()
	# wrong solution
	if options.sets_per_sec:
		check_sets_per_sec()
	if options.disk_write_queue:
		check_disk_write_queue()
	if options.gets_per_sec:
		check_gets_per_sec()

	if options.vbucket_count and options.vbucket:
		if options.active:
			check_vbucket('vb_active_num', 'CB active vBucket count', False)
		elif options.replica:
			check_vbucket('vb_replica_num', 'CB replica vBucket count', False)
		elif options.pending:
			check_vbucket('vb_pending_num', 'CB pending vBucket count', False)
		elif options.total:
			check_vbucket('ep_vb_total', 'CB total vBucket count', False)
		else:
			print "wrong options combination"
			sys.exit(2)

	if options.vbucket_items and options.vbucket:
		if options.active:
			check_vbucket('curr_items', 'CB active vBucket items', True)
		elif options.replica:
			check_vbucket('vb_replica_curr_items', 'CB replica vBucket items', True)
		elif options.pending:
			check_vbucket('vb_pending_curr_items', 'CB pending vBucket items', True)
		elif options.total:
			check_vbucket('curr_items_tot', 'CB total vBucket items', True)
		else:
			print "wrong options combination"
			sys.exit(2)

	if options.vbucket_new_items and options.vbucket:
		if options.active:
			check_vbucket('vb_active_ops_create', 'CB active vBucket new items', True)
		elif options.replica:
			check_vbucket('vb_replica_ops_create', 'CB replica vBucket new items', True)
		elif options.pending:
			check_vbucket('vb_pending_ops_create', 'CB pending vBucket new items', True)
		else:
			print "wrong options combination"
			sys.exit(2)

	if options.vbucket_ejections and options.vbucket:
		if options.active:
			check_vbucket('vb_active_eject', 'CB active vBucket ejections', True)
		elif options.replica:
			check_vbucket('vb_replica_eject', 'CB replica vBucket ejections', True)
		elif options.pending:
			check_vbucket('vb_pending_eject', 'CB pending vBucket ejections ', True)
		elif options.total:
			check_vbucket('ep_num_value_ejects', 'CB total vBucket ejections', True)
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_user_data_ram and options.vbucket:
		if options.active:
			check_vbucket('vb_active_itm_memory', 'CB active vBucket user data', True)
		elif options.replica:
			check_vbucket('vb_replica_itm_memory', 'CB replica vBucket user data', True)
		elif options.pending:
			check_vbucket('vb_pending_itm_memory', 'CB pending vBucket user data', True)
		elif options.total:
			check_vbucket('ep_kv_size', 'CB total vBucket user data', True)
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_meta_data_ram and options.vbucket:
		if options.active:
			check_vbucket('vb_active_meta_data_memory', 'CB active vBucket meta data', True )
		elif options.replica:
			check_vbucket('vb_replica_meta_data_memory', 'CB replica vBucket meta data', True)
		elif options.pending:
			check_vbucket('vb_pending_meta_data_memory', 'CB pending vBucket meta data', True)
		else:
			print "wrong options combination"
			sys.exit(2)
	else:
		print "wrong options combination"
		sys.exit(2)

# option parse
parser = OptionParser()
parser.disable_interspersed_args()
arg = False

#option define
parser.add_option('-I', dest='ip')
parser.add_option('-u', dest='username')
parser.add_option('-p', dest='password')
parser.add_option('-P', dest='port')
parser.add_option('-b', dest='bucket')
parser.add_option('-W', type='int', dest='warning')
parser.add_option('-C', type='int', dest='critical')
parser.add_option('--operations-per-sec', action='callback', callback=option_none, dest='operations_per_second')
parser.add_option('--memory-used', action='callback', callback=option_none, dest='memory_used')
parser.add_option('--disk-reads-per-sec', action='callback', callback=option_none, dest='disk_reads_per_sec')
parser.add_option('--item-count', action='callback', callback=option_none, dest='item_count')
parser.add_option('--CAS', action='callback', callback=option_none, dest='cas')
parser.add_option('--deletes-per-sec', action='callback', callback=option_none, dest='deletes_per_sec')
parser.add_option('--low-watermark', action='callback', callback=option_none, dest='low_watermark')
parser.add_option('--high-watermark', action='callback', callback=option_none, dest='high_watermark')
parser.add_option('--cbstat', default='/opt/couchbase/bin/cbstats', dest='cbstat')
parser.add_option('--cache-miss-ratio', action='callback', callback=option_none, dest='cache_miss_ratio')
parser.add_option('--disk-creates-per-sec', action='callback', callback=option_none, dest='disk_creates_per_sec')
parser.add_option('--disk-updates-per-sec', action='callback', callback=option_none, dest='disk_updates_per_sec')
parser.add_option('--sets-per-sec', action='callback', callback=option_none, dest='sets_per_sec')
parser.add_option('--gets-per-sec', action='callback', callback=option_none, dest='gets_per_sec')
parser.add_option('--disk-write-queue', action='callback', callback=option_none, dest='disk_write_queue')
parser.add_option('--vbucket-count', action='callback', callback=option_none, dest='vbucket_count')
parser.add_option('--vbucket', action='callback', callback=option_none, dest='vbucket')
parser.add_option('--active', action='callback', callback=option_none, dest='active')
parser.add_option('--replica', action='callback', callback=option_none, dest='replica')
parser.add_option('--pending', action='callback', callback=option_none, dest='pending')
parser.add_option('--total', action='callback', callback=option_none, dest='total')
parser.add_option('--items', action='callback', callback=option_none, dest='vbucket_items')
parser.add_option('--resident', action='callback', callback=option_none, dest='vbucket_resident')
parser.add_option('--new-items', action='callback', callback=option_none, dest='vbucket_new_items')
parser.add_option('--ejections', action='callback', callback=option_none, dest='vbucket_ejections')
parser.add_option('--user-data-ram', action='callback', callback=option_none, dest='vbucket_user_data_ram')
parser.add_option('--meta-data-ram', action='callback', callback=option_none, dest='vbucket_meta_data_ram')
options, args = parser.parse_args()

try:
	which_argument()
except Exception:
    print "Invalid option combination"
    print "Try '--help' for more information "

