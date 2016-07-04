#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ,--(saket)--(RiPlayServer)--(01/07/16 09:40)--(【ツ】)---
# `--(~/main.py$)-->
import logging
import re
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

import api
import player


__author__ = 'saket'
__tag__ = 'main'
_debug = True
PORT_NUMBER = 8080

logging.basicConfig(format='[%(asctime)s]--(%(levelname)s)--> %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')


# ██████╗ ██╗██████╗ ██╗      █████╗ ██╗   ██╗ ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗
# ██╔══██╗╚═╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝ ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
# ██████╔╝██╗██████╔╝██║     ███████║ ╚████╔╝  ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝
# ██╔══██╗██║██╔═══╝ ██║     ██╔══██║  ╚██╔╝   ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗
# ██║  ██║██║██║     ███████╗██║  ██║   ██║    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
# ╚═╝  ╚═╝╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝

class MyThreadedServer(ThreadingMixIn, HTTPServer):
    pass


class MyServer(BaseHTTPRequestHandler):
    # noinspection PyPep8Naming
    def do_GET(self):
        """Handle GET requests"""

        if re.match("/api/.+?", self.path):
            api.handler(self)

        elif re.match("/.+?", self.path):
            # todo : Implement web page server
            self.send_error(501, "Web services not implemented yet")

        else:
            self.send_error(404, "Not found what you were looking for")


    def cookie_handler(self):
        """Get Cookies for authentication"""
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


# #######################################################################################
def main():
    server = MyThreadedServer(("", PORT_NUMBER), MyServer)
    try:
        print "Started http server on port ", PORT_NUMBER
        # print MarketMilitia
        server.serve_forever()

    except KeyboardInterrupt:
        player.stop_player()

    finally:
        server.socket.close()


if __name__ == "__main__":
    main()
