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

def check_levels(message, status_value):
	# convert to mb
	status_value_mb = status_value/(1024.0**2)
	if options.critical > options.warning:
		if status_value >= options.critical:
			print "CRITICAL - " + message, status_value_mb
			return sys.exit(nagios_codes['CRITICAL'])
		elif status_value >= options.warning:
			print "WARNING - " + message, status_value_mb
			return sys.exit(nagios_codes['WARNING'])
		else:
			print "OK - " + message, status_value_mb
			return sys.exit(nagios_codes['OK'])
	else:
		if status_value >= options.warning:
			print "WARNING - " + message, status_value_mb
			return sys.exit(nagios_codes['WARNING'])
		elif status_value >= options.critical:
			print "CRITICAL - " + message, status_value_mb
			return sys.exit(nagios_codes['CRITICAL'])
		else:
			print "OK - " + message, status_value_mb
			return sys.exit(nagios_codes['OK'])

def check_vb_active_ejections():
	vb_active_eject = get_status('vb_active_eject')
	check_levels("CB active vb ejections per sec: ", vb_active_eject)

def check_vb_active_user_data_ram():
	vb_active_itm_memory = get_status('vb_active_itm_memory')
	check_levels("CB active vb user data in ram: ", vb_active_itm_memory)

def check_vb_active_meta_data_ram():
	vb_active_meta_data_memory = get_status('vb_active_meta_data_memory')
	check_levels("CB active vb metada in ram: ", vb_active_meta_data_memory)

def check_vb_active_ops_create():
	vb_active_ops_create = get_status('vb_active_ops_create')
	check_levels("CB active vbuckets ops_create: ", vb_active_ops_create)

def check_vb_active_resident():
	vb_active_perc_mem_resident = get_status('vb_active_perc_mem_resident')
	check_levels("CB active vbuckets resident: ", vb_active_perc_mem_resident)

def check_vb_active_items():
	curr_items = get_status('curr_items')
	check_levels("CB active vbuckets items: ", curr_items)

def check_vb_active_vbcount():
	vb_active_num = get_status('vb_active_num')
	check_levels("CB active vbuckets count: ", vb_active_num)

def check_get_per_second():
	cmd_get = get_status('cmd_get')
	check_levels("CB get per sec: ", cmd_get)

def check_disk_write_queue():
	ep_queue_size = get_status('ep_queue_size')
	ep_flusher_todo = get_status('ep_flusher_todo')
	disk_write_queue = ep_queue_size + ep_flusher_todo
	check_levels("CB disk write queue: ", disk_write_queue)

def check_set_per_second():
	cmd_set = get_status('cmd_set')
	check_levels("CB set per sec: ", cmd_set)

def check_update_per_sec():
	vb_active_ops_update = get_status('vb_active_ops_update')
	vb_replica_ops_update = get_status('vb_replica_ops_update')
	vb_pending_ops_update = get_status('vb_pending_ops_update')
	updates_per_sec = vb_active_ops_update + vb_replica_ops_update
	updates_per_sec += vb_pending_ops_update
	check_levels("CB disk updates per sec: ", updates_per_sec)

def check_create_per_sec():
	vb_active_ops_create = get_status('vb_active_ops_create')
	vb_replica_ops_create = get_status('vb_replica_ops_create')
	vb_pending_ops_create = get_status('vb_pending_ops_create')
	create_per_sec = vb_active_ops_create + vb_replica_ops_create 
	create_per_sec += vb_pending_ops_create
	check_levels("CB disk creates per sec: ", create_per_sec)

def check_cache_miss_ratio():
	ep_bg_fetched = get_status('ep_bg_fetched')
	cmd_get = get_status('cmd_get')
	if cmd_get == 0:
		check_levels("CB cache miss ratio: ", 0)
	else:
		cache_miss_ratio = ep_bg_fetched*1.0/cmd_get
		check_levels("CB cache miss ratio: ", cache_miss_ratio)

def check_disk_read_per_sec():
	disk_read = get_status('disk_read')
	check_levels("CB disk read per sec: ", disk_read)
		
def check_item_count():
	curr_items = get_status('curr_items')
	check_levels("CB item count: ", curr_items)

def check_ops_per_second():
	cmd_get = get_status('cmd_get')
	cmd_set = get_status('cmd_set')
	incr_misses = get_status('incr_misses')
	incr_hits = get_status('incr_hits')
	decr_misses = get_status('decr_misses')
	decr_hits = get_status('decr_hits')
	delete_misses = get_status('delete_misses')
	delete_hits = get_status('delete_hits')
	ops_per_sec = cmd_get + cmd_set + incr_misses + incr_hits + decr_misses
	ops_per_sec = decr_hits + delete_misses + delete_hits
	check_levels("CB ops per sec: ", ops_per_sec)
	
def check_mem_used():
	mem_used = get_status('mem_used')
	check_levels("CB memory used: ", mem_used)

def check_cas_per_second():
	cas_hits = get_status('cas_hits')
	check_levels("CB cas per sec: ", cas_hits)
		
def check_del_per_second():
	delete_hits = get_status('delete_hits')
	check_levels("CB delete per sec: ", delete_hits)

def check_low_watermark():
	ep_mem_low_wat = get_status('ep_mem_low_wat')
	check_levels("CB low watermark: ", ep_mem_low_wat)

def check_high_watermark():
	ep_mem_high_wat = get_status('ep_mem_high_wat')
	check_levels("CB high watermark: ", ep_mem_high_wat)

# which argument 
def which_argument():
	if options.operations_per_second:
		check_ops_per_second()
	if options.cas:
		check_cas_per_second()
	if options.high_watermark:
		check_high_watermark()
	if options.low_watermark:
		check_low_watermark()
	if options.del_ps_check:
		check_del_per_second()
	if options.mem_used:
		check_mem_used()
	if options.disk_read:
		check_disk_read_per_sec()
	if options.item_count:
		check_item_count()
	if options.cache_miss_ratio:
		check_cache_miss_ratio()
	if options.create_per_sec:
		check_create_per_sec()
	if options.update_per_sec:
		check_update_per_sec()
	if options.set_per_sec:
		check_set_per_second()
	if options.disk_write_queue:
		check_disk_write_queue()
	if options.get_per_sec:
		check_get_per_second()
	if options.vbucket_count and options.vbucket:
		if options.active:
			check_vb_active_vbcount()
		elif options.replica:
			check_vb_replica_vbcount()
		elif options.pending:
			check_vb_pending_vbcount()
		elif options.total:
			check_vb_total_vbcount()
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_items and options.vbucket:
		if options.active:
			check_vb_active_items()
		elif options.replica:
			check_vb_replica_items()
		elif options.pending:
			check_vb_pending_items()
		elif options.total:
			check_vb_total_items()
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_resident and options.vbucket:
		if options.active:
			check_vb_active_resident()
		elif options.replica:
			check_vb_replica_resident()
		elif options.pending:
			check_vb_pending_resident()
		elif options.total:
			check_vb_total_resident()
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_new_items and options.vbucket:
		if options.active:
			check_vb_active_ops_create()
		elif options.replica:
			check_vb_replica_ops_create()
		elif options.pending:
			check_vb_pending_ops_create()
		elif options.total:
			check_vb_total_ops_create()
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_ejections and options.vbucket:
		if options.active:
			check_vb_active_ejections()
		elif options.replica:
			check_vb_replica_ejections()
		elif options.pending:
			check_vb_pending_ejections()
		elif options.total:
			check_vb_total_ejections()
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_user_data_ram and options.vbucket:
		if options.active:
			check_vb_active_user_data_ram()
		elif options.replica:
			check_vb_replica_user_data_ram()
		elif options.pending:
			check_vb_pending_user_data_ram()
		elif options.total:
			check_vb_total_user_data_ram()
		else:
			print "wrong options combination"
			sys.exit(2)
	if options.vbucket_meta_data_ram and options.vbucket:
		if options.active:
			check_vb_active_meta_data_ram()
		elif options.replica:
			check_vb_replica_meta_data_ram()
		elif options.pending:
			check_vb_pending_meta_data_ram()
		elif options.total:
			check_vb_total_meta_data_ram()
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
parser.add_option('--OPS', action='callback', callback=option_none, dest='operations_per_second')
parser.add_option('--memory-used', action='callback', callback=option_none, dest='mem_used')
parser.add_option('--disk-read', action='callback', callback=option_none, dest='disk_read')
parser.add_option('--item-count', action='callback', callback=option_none, dest='item_count')
parser.add_option('--CAS', action='callback', callback=option_none, dest='cas')
parser.add_option('--del-per-second', action='callback', callback=option_none, dest='del_ps_check')
parser.add_option('--low-watermark', action='callback', callback=option_none, dest='low_watermark')
parser.add_option('--high-watermark', action='callback', callback=option_none, dest='high_watermark')
parser.add_option('--cbstat', default='/opt/couchbase/bin/cbstats', dest='cbstat')
parser.add_option('--cache-miss-ratio', action='callback', callback=option_none, dest='cache_miss_ratio')
parser.add_option('--create-per-sec', action='callback', callback=option_none, dest='create_per_sec')
parser.add_option('--update-per-sec', action='callback', callback=option_none, dest='update_per_sec')
parser.add_option('--set-per-sec', action='callback', callback=option_none, dest='set_per_sec')
parser.add_option('--get-per-sec', action='callback', callback=option_none, dest='get_per_sec')
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

