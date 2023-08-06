#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


PY3 = sys.version > '3'
if PY3:
    import http.server as httpserver
    import socketserver
else:
    import SimpleHTTPServer as httpserver
    import SocketServer as socketserver
    

def serve_static_site(output_dir, port=9090):
    """ Serve the output/ directory on port 9090. """
    os.chdir(output_dir)
    Handler = httpserver.SimpleHTTPRequestHandler

    # See http://stackoverflow.com/questions/16433522/socketserver-getting-rid-of-errno-98-address-already-in-use
    socketserver.TCPServer.allow_reuse_address = True

    httpd = socketserver.TCPServer(("", port), Handler)
    print("serving at port", port)

    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down...")
        httpd.shutdown()
        httpd.socket.close()
        sys.exit()
