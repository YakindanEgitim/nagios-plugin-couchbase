# Nagios-CouchBase

A simple nagios plugin to monitor Couchbase 2.0 servers/cluster.

## Author
Ebru Akagündüz ebru.akagunduz@gmail.com

## Installation
<pre><code> git clone https://github.com/YakindanEgitim/nagios-plugin-couchbase.git</code></pre>

## Usage
<pre><code>
Usage: couchbase.py [options]
Options:
  -I                      Ip
  -u                      Username
  -p                      Password
  -P                      Port
  -b                      bucket name
  -W                      warning
  -C                      critical
  --OPS                   Total amount of operations per second for specific bucket
  --memory-used           memory used
  --disk-read             Number of reads per second from disk for specific bucket 
  --item-count            Number of unique active items 
  --CAS                   CAS per second for specific bucket
  --del-per-second        Number of delete operations per second for specific bucket
  --low-watermark         Low watermark
  --high-watermark        High watermark
  --cbstat                cbstats command path of couchbase (default /opt/couchbase/bin/cbstats)
  --cache-miss-ratio      Percentage of reads per second for specific bucket
  --create-per-sec        Number of new items created on disk per second for specific bucket
  --update-per-sec        Number of items updated on disk for specific bucket
  --set-per-sec           set operations per second for specific bucket
  --disk-write-queue      Number of items waiting to be written to disk in bucket
</code></pre>

## Live Demo
You can see how it works on web page. So you should visit "54.234.80.73/nagios3/" adrres using username "testuser", password "password"

##LICENSE
Nagios Plugin Couchbase is available under the [GPLv3](http://gplv3.fsf.org/)
