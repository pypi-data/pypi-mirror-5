#!/usr/bin/env python

import argparse
import lockfile
import os
import pkgutil
import signal
import sys
from daemon.pidfile import TimeoutPIDLockFile
from geventdaemon import GeventDaemonContext


def read_pidfile(path):
    try:
        with open(path, 'r') as f:
            return int(f.read())
    except Exception, e:
        raise ValueError(e.message)


def terminate_server(sig, frame):
    from maildump import stop

    if sig == signal.SIGINT and os.isatty(sys.stdout.fileno()):
        # Terminate the line containing ^C
        print
    stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smtp-ip', default='127.0.0.1')
    parser.add_argument('--smtp-port', default=1025, type=int)
    parser.add_argument('--http-ip', default='127.0.0.1')
    parser.add_argument('--http-port', default=1080, type=int)
    parser.add_argument('--db', help='SQLite database - in-memory if missing')
    parser.add_argument('-f', '--foreground', help='Run in the foreground', action='store_true')
    parser.add_argument('-d', '--debug', help='Run the web app in debug mode', action='store_true')
    parser.add_argument('-a', '--autobuild-assets', help='Automatically rebuild assets if necessary',
                        action='store_true')
    parser.add_argument('-p', '--pidfile', help='Create a PID file')
    parser.add_argument('--stop', help='Sends SIGTERM to the running daemon (needs --pidfile)', action='store_true')
    args = parser.parse_args()

    # Do we just want to stop a runnign daemon?
    if args.stop:
        if not args.pidfile or not os.path.exists(args.pidfile):
            print 'PID file not specified or not found'
            sys.exit(1)
        try:
            pid = read_pidfile(args.pidfile)
        except ValueError, e:
            print 'Could not read PID file: {}'.format(e)
            sys.exit(1)
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError, e:
            print 'Could not send SIGTERM: {}'.format(e)
            sys.exit(1)
        sys.exit(0)

    # Check if the static folder is writable
    asset_folder = os.path.join(pkgutil.get_loader('maildump').filename, 'static')
    if args.autobuild_assets and not os.access(asset_folder, os.W_OK):
        print 'Autobuilding assets requires write access to {}'.format(asset_folder)
        sys.exit(1)

    daemon_kw = {'monkey_greenlet_report': False,
                 'signal_map': {signal.SIGTERM: terminate_server,
                                signal.SIGINT: terminate_server}}

    if args.foreground:
        # Do not detach and keep std streams open
        daemon_kw.update({'detach_process': False,
                          'stdin': sys.stdin,
                          'stdout': sys.stdout,
                          'stderr': sys.stderr})

    pidfile = None
    if args.pidfile:
        pidfile = os.path.abspath(args.pidfile) if not os.path.isabs(args.pidfile) else args.pidfile
        if os.path.exists(pidfile):
            pid = read_pidfile(pidfile)
            if not os.path.exists(os.path.join('/proc', str(pid))):
                print 'Deleting obsolete PID file (process %d does not exist)'.format(pid)
                os.unlink(pidfile)
        daemon_kw['pidfile'] = TimeoutPIDLockFile(pidfile, 5)

    # Unload threading module to avoid error on exit (it's loaded by lockfile)
    if 'threading' in sys.modules:
        del sys.modules['threading']

    context = GeventDaemonContext(**daemon_kw)
    try:
        context.open()
    except lockfile.LockTimeout:
        print 'Could not acquire lock on pid file {}'.format(pidfile)
        print 'Check if the daemon is already running.'
        sys.exit(1)
    except KeyboardInterrupt:
        print
        sys.exit(1)

    with context:
        # Imports are here to avoid importing anything before monkeypatching
        from maildump import app, start
        from maildump.web import assets

        assets.debug = app.debug = args.debug
        assets.auto_build = args.autobuild_assets
        start(args.http_ip, args.http_port, args.smtp_ip, args.smtp_port, args.db)


if __name__ == '__main__':
    main()