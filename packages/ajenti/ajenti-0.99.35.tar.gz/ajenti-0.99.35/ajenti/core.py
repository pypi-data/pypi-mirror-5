from __future__ import unicode_literals

import atexit
import gettext
import locale
import logging
import os
import signal
import socket
import subprocess
import syslog
import sys
import time
import tempfile

import ajenti
from ajenti.http import HttpRoot
from ajenti.routing import CentralDispatcher
from ajenti.middleware import SessionMiddleware, AuthenticationMiddleware
import ajenti.console
import ajenti.plugins
import ajenti.feedback

import gevent
from gevent import monkey
monkey.patch_all(select=False)
from socketio.server import SocketIOServer


class SSLTunnel (object):
    """
    gevent's SSL server implementation is buggy so we have to use stunnel
    """

    def start(self, host, port, certificate_path):
        self.port = self.get_free_port()
        logging.info('Starting SSL tunnel for port %i' % self.port)
        stunnel = 'stunnel'
        if subprocess.call(['which', 'stunnel4']) == 0:
            stunnel = 'stunnel4'
        cfg = tempfile.NamedTemporaryFile(delete=False)
        cfg.write("""
            cert = %s
            foreground = yes
            pid =

            [default]
            accept = %s:%i
            connect = 127.0.0.1:%i
        """ % (
            certificate_path,
            host or '0.0.0.0', port,
            self.port
        ))
        cfg.close()
        cmd = [
            stunnel,
            cfg.name,
        ]
        self.process = subprocess.Popen(cmd, stdout=None)
        self._filename = cfg.name

    def check(self):
        time.sleep(0.5)
        return self.process.poll() is None

    def stop(self):
        os.unlink(self._filename)
        self.process.terminate()
        if self.check():
            self.process.kill()

    def get_free_port(self):
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return int(port)


def run():
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        logging.warning('Couldn\'t set default locale')
    localedir = os.path.abspath(os.path.join(os.path.split(ajenti.core.__file__)[0], 'locale'))
    gettext.textdomain('ajenti')
    gettext.install('ajenti', localedir, unicode=True)

    logging.info('Ajenti %s running on platform: %s' % (ajenti.version, ajenti.platform))

    if ajenti.debug:
        ajenti.console.register()

    # Load plugins
    ajenti.plugins.manager.load_all()

    bind_spec = (ajenti.config.tree.http_binding.host, ajenti.config.tree.http_binding.port)
    if ':' in bind_spec[0]:
        addrs = socket.getaddrinfo(bind_spec[0], bind_spec[1], socket.AF_INET6, 0, socket.SOL_TCP)
        bind_spec = addrs[0][-1]

    ssl_tunnel = None
    if ajenti.config.tree.ssl.enable:
        ssl_tunnel = SSLTunnel()
        ssl_tunnel.start(bind_spec[0], bind_spec[1], ajenti.config.tree.ssl.certificate_path)
        if ssl_tunnel.check():
            logging.info('SSL tunnel running fine')
            bind_spec = ('127.0.0.1', ssl_tunnel.port)
            atexit.register(ssl_tunnel.stop)
        else:
            logging.error('SSL tunnel failed to start')

    # Fix stupid socketio bug (it tries to do *args[0][0])
    socket.socket.__getitem__ = lambda x, y: None

    logging.info('Starting server on %s' % (bind_spec, ))
    listener = socket.socket(socket.AF_INET6 if ':' in bind_spec[0] else socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(bind_spec)
    listener.listen(10)

    stack = [SessionMiddleware(), AuthenticationMiddleware(), CentralDispatcher()]
    ajenti.server = SocketIOServer(
        listener,
        log=open(os.devnull, 'w'),
        application=HttpRoot(stack).dispatch,
        policy_server=False,
        resource='ajenti:socket',
    )

    # auth.log
    try:
        syslog.openlog(
            ident=str(b'ajenti'),
            facility=syslog.LOG_AUTH,
        )
    except:
        syslog.openlog(b'ajenti')

    try:
        gevent.signal(signal.SIGTERM, lambda: sys.exit(0))
    except:
        pass

    ajenti.feedback.start()
    ajenti.server.serve_forever()

    if hasattr(ajenti.server, 'restart_marker'):
        logging.warn('Restarting by request')
        if ssl_tunnel:
            ssl_tunnel.stop()

        fd = 20  # Close all descriptors. Creepy thing
        while fd > 2:
            try:
                os.close(fd)
                logging.debug('Closed descriptor #%i' % fd)
            except:
                pass
            fd -= 1

        os.execv(sys.argv[0], sys.argv)
    else:
        logging.info('Stopped by request')
