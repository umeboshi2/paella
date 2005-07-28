#! /bin/sh
#
# skeleton	example file to build /etc/init.d/ scripts.
#		This file should be used to construct scripts for /etc/init.d.
#
# Author:	Miquel van Smoorenburg <miquels@cistron.nl>.
#		Ian Murdock <imurdock@gnu.ai.mit.edu>.
#
#		You may remove the "Author" lines above and replace them
#		with your own name if you copy and modify this script.
#
# Version:	@(#)skeleton  1.9.4  21-Mar-2004  miquels@cistron.nl
#

set -e

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/sbin/paella-init-nfsinstaller
NAME=paella-nfs-installer

# Read config file if it is present.
if [ -r /etc/default/paella-nfs-installer ] 
then
    echo 'using defaults in /etc/default/paella-debrepos'
    . /etc/default/paella-nfs-installer
fi

DESC="Paella Nfs Installer"
SLEEPTIME=10

PIDFILE=/var/run/paella-nfsinstaller.pid
SCRIPTNAME=/etc/init.d/$NAME

# Gracefully exit if the package has been removed.
test -x $DAEMON || exit 0

case "$1" in
  start)
	echo "Starting $DESC: $NAME"
	start-stop-daemon --start  --pidfile $PIDFILE --exec $DAEMON 
	echo "."
	;;
  stop)
	echo "Stopping $DESC: $NAME"
	start-stop-daemon --stop  --pidfile $PIDFILE 
	rm $PIDFILE
	echo "."
	;;
  #reload)
	#
	#	If the daemon can reload its config files on the fly
	#	for example by sending it SIGHUP, do it here.
	#
	#	If the daemon responds to changes in its config file
	#	directly anyway, make this a do-nothing entry.
	#
	# echo -n "Reloading $DESC configuration..."
	# start-stop-daemon --stop --signal 1 --quiet --pidfile \
	#	$PIDFILE --exec $DAEMON
	# echo "done."
  #;;
  restart|force-reload)
	#
	#	If the "reload" option is implemented, move the "force-reload"
	#	option to the "reload" entry above. If not, "force-reload" is
	#	just the same as "restart".
	#
	echo -n "Restarting $DESC: $NAME"
	echo "Stopping $DESC: $NAME"
	start-stop-daemon --stop  --pidfile $PIDFILE
	echo "."
	sleep $SLEEPTIME
	rm $PIDFILE
	echo "Starting $DESC: $NAME"
	start-stop-daemon --start  --pidfile $PIDFILE --exec $DAEMON
	echo "."
	echo "restarted."
	;;
  *)
	# echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
	echo "Usage: $SCRIPTNAME {start|stop|restart|force-reload}" >&2
	exit 1
	;;
esac

exit 0
