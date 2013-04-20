from distutils.core import setup
 
setup(
	name = "Couchbase Nagios Plugin",
	version = "1.0",
	description = "A simple nagios plugin to monitor Couchbase 2.0 servers/cluster.",
	author = "Ebru Akagunduz",
	author_email = "ebru.akagunduz@gmail.com",
	packages = ['src'],
	scripts = ['src/check_couchbase_cluster.py', 'src/check_couchbase_server.py'],
)


