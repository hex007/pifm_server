#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ,--(saket)--(RiPlayServer)--(02/07/16 20:35)--(【ツ】)---
# `--(~/api.py$)-->
import re

import player


__tag__ = 'api'


def handler(request):
    """Handle API requests"""
    if request.path == "/api/start":
        api_start(request)

    elif request.path == "/api/stop":
        api_stop(request)

    elif request.path == "/api/skip":
        api_skip(request)

    elif request.path == "/api/collection":
        api_collection(request)

    elif request.path == "/api/playlist":
        api_playlist(request)

    elif request.path == "/api/clear":
        api_clear(request)

    elif request.path == "/api/freq":
        api_freq(request)

    elif re.match(r"/api/play/(?:\d+|all|shuffle)", request.path):
        n = re.findall(r"/api/play/(.*)", request.path)[0]
        api_play(request, n if n in ["all", "shuffle"] else int(n))

    elif re.match(r"/api/queue/\d+", request.path):
        n = int(re.findall(r"/api/queue/(.*)", request.path)[0])
        api_queue(request, n)

    else:
        request.send_error(401, request.path)


def api_start(request):
    """Handle API request to Start player"""
    request.send_response(202, 'API', "Starting Player")
    request.end_headers()

    request.wfile.write("Started\n")
    player.start_player()


def api_stop(request):
    """Handle API request to Stop player"""
    request.send_response(202, 'API', "Stopping Player")
    request.end_headers()

    request.wfile.write("Stopped\n")
    player.stop_player()


def api_skip(request):
    """Handle API request to Skip song"""
    request.send_response(202, 'API', "Skipping Song")
    request.end_headers()

    request.wfile.write("Skipped: %s\n" % player.get_playlist()[0])
    player.skip()


def api_collection(request):
    """Handle API request for Music Collection"""
    request.send_response(200, 'API', "Sending Collection")
    request.send_header('Content-Type', 'application/json')
    request.end_headers()

    request.wfile.write("%s\n" % player.get_collection_json())


def api_playlist(request):
    """Handle API request for current Playlist"""
    request.send_response(200, 'API', "Sending Playlist")
    request.send_header('Content-Type', 'application/json')
    request.end_headers()

    request.wfile.write("%s\n" % player.get_playlist_json())


def api_clear(request):
    """Handle API request to clear playlist"""
    request.send_response(200, 'API' "Clearing playlist")
    request.end_headers()

    request.wfile.write("Cleared\n")
    player.clear()


def api_freq(request):
    """Handle API request for Broadcast Frequency"""
    request.send_response(200, 'API', "Sending Broadcast Frequency")
    request.end_headers()

    request.wfile.write("%d\n" % player.get_freq())


def api_play(request, n):
    """Handle API request to Play Song n-> [int|"all"|"shuffle"]."""
    if n not in player.get_collection() and n not in ["all", "shuffle"]:
        request.api_error("%r not found in collection" % n)
        return

    request.send_response(202, 'API', "Requesting playing %r" % n)
    request.end_headers()

    request.wfile.write("Playing: %s\n" % (player.get_collection()[n] if n in player.get_collection() else n))
    player.play(n)


def api_queue(request, n):
    """Handle API request to Add to playlist"""
    if n not in player.get_collection():
        request.api_error("%d not found in collection" % n)
        return

    request.send_response(200, 'API', "Requesting queuing %d" % n)
    request.end_headers()

    request.wfile.write("Queued: %s\n" % player.get_collection()[n])
    player.queue(n)


def api_error(request, message):
    request.send_response(400, 'API', message)
    request.end_headers()

    request.wfile.write("%s\n" % message)
