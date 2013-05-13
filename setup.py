from distutils.core import setup
import glob

setup(
	name = "Couchbase Nagios Plugin",
	version = "1.0",
	description = "A simple nagios plugin to monitor Couchbase 2.0 servers/cluster.",
	author = "Ebru Akagunduz",
	author_email = "ebru.akagunduz@gmail.com",
	packages = ['src'],
	data_files = [('/usr/lib/nagios/plugins/', glob.glob("src/*py"))]
)

