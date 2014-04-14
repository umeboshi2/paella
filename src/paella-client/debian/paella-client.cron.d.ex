#
# Regular cron jobs for the paella-client package
#
0 4	* * *	root	[ -x /usr/bin/paella-client_maintenance ] && /usr/bin/paella-client_maintenance
