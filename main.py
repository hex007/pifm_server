#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ,--(saket)--(RiPlayServer)--(01/07/16 09:40)--(【ツ】)---
# `--(~/main.py$)-->
import logging
import re
import threading
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

import api
import player
import web
import ws


__author__ = 'saket'
__tag__ = 'main'
_debug = True
HTTP_PORT_NUMBER = 8080
WEB_SOCKET_PORT_NUMBER = 8081

logging.basicConfig(format='[%(asctime)s]--(%(levelname)s)--> %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# ██████╗ ██╗██████╗ ██╗      █████╗ ██╗   ██╗ ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗
# ██╔══██╗╚═╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝ ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
# ██████╔╝██╗██████╔╝██║     ███████║ ╚████╔╝  ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝
# ██╔══██╗██║██╔═══╝ ██║     ██╔══██║  ╚██╔╝   ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗
# ██║  ██║██║██║     ███████╗██║  ██║   ██║    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
# ╚═╝  ╚═╝╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝


class MyServer(BaseHTTPRequestHandler):
    # noinspection PyPep8Naming
    def do_GET(self):
        """Handle GET requests"""

        if re.match("/api/.+?", self.path):
            api.handler(self)

        else:
            web.handler(self)


    def cookie_handler(self):
        """Get Cookies for authentication"""
        # todo : implement a new authentication method using cookies
        cookies = self.headers.getheader("Cookie")
        if cookies and re.match("username=.+?; auth_token=[0-9a-f]{32}", cookies):
            return re.findall("username=(.+?); auth_token=([0-9a-f]{32})", cookies)[0]
        else:
            return None, None


    def send_response(self, code, *log):
        """Send response code and status.

        Print log:list if provided. Overridden to prevent standard headers
        """
        if log:
            text = '\033[01;32m[%s]--' % self.client_address[0]
            for i in log:
                text += '(%s)--' % i
            text += '-\033[0;0m'
            print text

        message = self.responses[code][0] if code in self.responses else ''
        self.wfile.write("%s %d %s\r\n" % (self.protocol_version, code, message))


class WebSocketHandler(WebSocket):
    def handleMessage(self):
        ws.handler(self, self.data)


    def handleConnected(self):
        ws.ws_subscribe(self)


    def handleClose(self):
        ws.ws_unsubscribe(self)


    def sendMessage(self, data):
        super(WebSocketHandler, self).sendMessage(unicode(data))


# #######################################################################################
class HttpServer(ThreadingMixIn, HTTPServer):
    pass


class WebSocketServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = SimpleWebSocketServer("", WEB_SOCKET_PORT_NUMBER, WebSocketHandler)


    def run(self):
        log.info("Starting WebSocketServer on port %d" % WEB_SOCKET_PORT_NUMBER)
        self.server.serveforever()


def main():
    server = HttpServer(("", HTTP_PORT_NUMBER), MyServer)
    web_socket_server = WebSocketServer()

    try:
        web_socket_server.start()
        log.info("Started HttpServer on port %d" % HTTP_PORT_NUMBER)
        server.serve_forever()

    except KeyboardInterrupt:
        player.stop_player()
        api.inform_subscribers()

    finally:
        server.socket.close()
        web_socket_server.server.close()


if __name__ == "__main__":
    main()
