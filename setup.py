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

