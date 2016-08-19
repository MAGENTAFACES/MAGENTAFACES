#!/usr/bin/env python

from flup.server.fcgi import WSGIServer
from mf_www import make_app

if __name__ == '__main__':
	application = make_app()
	WSGIServer(application, bindAddress='/tmp/mf.sock').run()
