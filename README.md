# nagios-plugin-couchbase

A simple nagios plugin to monitor Couchbase servers/cluster.<br>
Compatible with Couchbase 2.x

## Author
Ebru Akagündüz ebru.akagunduz@gmail.com

###Requirements
<pre>
# apt-get install nagios3 
# pip install requests
</pre>

## Installation
<pre><code> git clone https://github.com/YakindanEgitim/nagios-plugin-couchbase.git</code></pre>

## Usage

#### Summary Statistics

Following commands show information based on the currently selected bucket:
<pre><code>
define command{
  command_name  cb_item_count
  command_line  $USER1$/check_couchbase.py -u $USER2$ -p $USER3$ -I $HOSTADDRESS$  -P $ARG1$ -b $ARG2$ --item-count -W $ARG3$ -C $ARG4$
}

define command{
  command_name  cb_low_watermark
  command_line  $USER1$/check_couchbase.py -u $USER2$ -p $USER3$ -I $HOSTADDRESS$  -P $ARG1$ -b $ARG2$ --low-watermark -W $ARG3$ -C $ARG4$
}

define command{
  command_name  cb_mem_used
  command_line  $USER1$/check_couchbase.py -u $USER2$ -p $USER3$ -I $HOSTADDRESS$  -P $ARG1$ -b $ARG2$ --memory-used -W $ARG3$ -C $ARG4$
}
</code></pre>

#### vBucket Resources Statistics

You should '--vbucket' parameter for checking vBucket resources. vBucket resources states are pending, total, replica and active. 
For example if you want to check ejections total state of vbucket, you must specify '--vbucket --total --ejections'. 
You can see below some examples for vbucket resources checks.

<pre><code>
define command{
  command_name  cb_vb_active_new_items
  command_line  $USER1$/check_couchbase.py -u $USER2$ -p $USER3$ -I $HOSTADDRESS$  -P $ARG1$ -b $ARG2$ --vbucket --active --new-items -W $ARG3$ -C $ARG4$
}

define command{
  command_name  cb_vb_pending_new_items
  command_line  $USER1$/check_couchbase.py -u $USER2$ -p $USER3$ -I $HOSTADDRESS$  -P $ARG1$ -b $ARG2$ --vbucket --pending --new-items -W $ARG3$ -C $ARG4$
}

define command{
  command_name  cb_vb_total_new_items
  command_line  $USER1$/check_couchbase.py -u $USER2$ -p $USER3$ -I $HOSTADDRESS$  -P $ARG1$ -b $ARG2$ --vbucket --total --new_items -W $ARG3$ -C $ARG4$
}

define command{
  command_name  cb_vb_replica_new_items
  command_line  $USER1$/check_couchbase.py -u $USER2$ -p $USER3$ -I $HOSTADDRESS$  -P $ARG1$ -b $ARG2$ --vbucket --replica --new-items -W $ARG3$ -C $ARG4$
}
</code></pre>

#### Disk Queue Statistics

You should use '--disk-queues' parameter. Disk queues states are pending, total, replica and active.
<pre><code>
define command{
  command_name  cb_vb_disk_queues_pending_fill_rate
  command_line  $USER1$/check_couchbase.py -u $USER2$ -p $USER3$ -I $HOSTADDRESS$  -P $ARG1$ -b $ARG2$  --disk-queues --pending --fill-rate -W $ARG3$ -C $ARG4$
}

define command{
  command_name  cb_vb_disk_queues_pending_drain_rate
  command_line  $USER1$/check_couchbase.py -u $USER2$ -p $USER3$ -I $HOSTADDRESS$  -P $ARG1$ -b $ARG2$  --disk-queues --pending --drain-rate -W $ARG3$ -C $ARG4$
}
</code></pre>

**Note1 :** We used above commands for cluster level. If you want to query in node level for statistic, you add '--node' parameter and you can remove some parameters. 
So you can edit following:
<pre><code>
define command{
  command_name  cb_vb_disk_queues_pending_drain_rate
  command_line  $USER1$/check_couchbase.py -I $HOSTADDRESS$ -b $ARG2$  --disk-queues --pending --drain-rate --node -W $ARG3$ -C $ARG4$
}
</code></pre>

In addition, if your CouchBase 'cbstats' command path different from default (/opt/bin/couchbase/cbstats), you should add '--cbstats' option.
In this case, you must define full path for '--cbstats' parameter. 

<pre><code>
define command{
  command_name  cb_mem_used
  command_line  $USER1$/check_couchbase.py -I $HOSTADDRESS$ -b $ARG2$ --memory-used --node --cbstats /full_path/ -W $ARG3$ -C $ARG4$
}
</code></pre>

You should use '--cbstats' parameter only in node level.

**Note2 :** If you want to use more options (--disk-reads-per-sec, --high-watermark, --cache-miss-ratio .. etc.), you can see using <br />'--help' parameter.
<pre><code>
$/usr/lib/nagios/plugins/check_couchbase.py --help
</code></pre>

##License
Nagios Plugin Couchbase is available under the [GPLv3](http://gplv3.fsf.org/)

##Website
You can access project website [here](http://yakindanegitim.org/nagios-plugin-couchbase/).

