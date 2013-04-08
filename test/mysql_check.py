#!/usr/bin/env python
import sys
from optparse import OptionParser
import MySQLdb as nagiosdb
import getpass

parser = OptionParser(usage='%prog [options <arg1> <args2> <arg3>]')
parser.add_option('-H', dest='hostname')
parser.add_option('-u', dest='username')
parser.add_option('-p', dest='password')
options, args = parser.parse_args()


for option in ('hostname', 'username', 'password'):
	if not getattr(options, option):
		break
 	if option == 'password' and options.password == None:
		options.password = getpass.getpass("Enter password\n")

con = nagiosdb.connect (host=options.hostname, user=options.username, passwd=options.password)

