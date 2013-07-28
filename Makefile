## Copyright (C) 2013 - Ebru Akagündüz <ebru.akagunduz@gmail.com>
##
## This file is part of nagios-couchbase-plugin.
##
## nagios-couchbase-plugin is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## nagios-couchbase-plugin is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>


all: install

install: 
	gzip -c src/check_couchbase.1 > src/check_couchbase.1.gz
	cp src/check_couchbase.py /usr/lib/nagios/plugins/ 
	cp src/check_couchbase.1.gz /usr/share/man/man1

clean: 
	rm /usr/lib/nagios/plugins/check_couchbase.py
	rm /usr/share/man/man1/check_couchbase.1.gz

