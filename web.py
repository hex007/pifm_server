#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ,--(saket)--(RiPlayServer)--(02/08/16 12:23)--(【ツ】)---
# `--(~/web.py$)--> 
from shutil import copyfileobj


__tag__ = 'web'


def handler(request):
    url = request.path
    
    if url == "/":
        request.send_response(200)
        request.send_header('Content-Type', 'text/html')
        request.end_headers()

        fav = file("webpage.html")
        copyfileobj(fav, request.wfile)
        fav.close()

    elif url == "/favicon.ico":
        request.send_response(200)
        request.send_header('Content-Type', 'image/png')
        request.end_headers()

        fav = file("favicon.png")
        copyfileobj(fav, request.wfile)
        fav.close()

    else:
        request.send_error(404, "Not found %r" % url)