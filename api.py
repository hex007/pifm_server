#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ,--(saket)--(RiPlayServer)--(02/07/16 20:35)--(【ツ】)---
# `--(~/api.py$)-->
import json
import re
from threading import Lock

import network
import player


__tag__ = 'api'
_subscribers = dict()
_subscriber_lock = Lock()


def handler(request):
    """Handle API requests"""
    if request.path == "/api/status":
        api_status(request)

    elif request.path == "/api/start":
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

    elif re.match(r"/api/subscribe(?:\?port=\d+)?", request.path):
        match = re.findall(r"/api/subscribe(?:\?port=(\d+))?", request.path)
        port = int(match[0]) if match else 80
        api_subscribe(request, port)

    elif re.match(r"/api/unsubscribe", request.path):
        api_unsubscribe(request)

    elif re.match(r"/api/output/(?:radio|audio)", request.path):
        match = re.findall(r"/api/output/(radio|audio)", request.path)
        api_output(request, match[0] if match else "audio")

    else:
        request.send_error(401, request.path)


def api_start(request):
    """Handle API request to Start player"""
    request.send_response(202, 'API', "Starting Player")
    request.end_headers()

    request.wfile.write(json.dumps(dict(started=True)))
    player.start_player()


def api_stop(request):
    """Handle API request to Stop player"""
    request.send_response(202, 'API', "Stopping Player")
    request.end_headers()

    request.wfile.write(json.dumps(dict(stopped=True)))
    player.stop_player()


def api_skip(request):
    """Handle API request to Skip song"""
    request.send_response(202, 'API', "Skipping Song")
    request.end_headers()

    request.wfile.write(json.dumps(dict(skipped=player.get_playlist()[0])))
    player.skip()


def api_collection(request):
    """Handle API request for Music Collection"""
    request.send_response(200, 'API', "Sending Collection")
    request.send_header('Content-Type', 'application/json')
    request.end_headers()

    request.wfile.write(player.get_collection_json())


def api_playlist(request):
    """Handle API request for current Playlist"""
    request.send_response(200, 'API', "Sending Playlist")
    request.send_header('Content-Type', 'application/json')
    request.end_headers()

    request.wfile.write(player.get_playlist_json())


def api_status(request):
    """Handle API request for current status"""
    request.send_response(200, 'API', "Sending Status")
    request.send_header('Content-Type', 'application/json')
    request.end_headers()

    request.wfile.write(player.get_status_json())


def api_clear(request):
    """Handle API request to clear playlist"""
    request.send_response(200, 'API' "Clearing playlist")
    request.send_header('Content-Type', 'application/json')
    request.end_headers()

    request.wfile.write(json.dumps(dict(cleared=True)))
    player.clear()


def api_freq(request):
    """Handle API request for Broadcast Frequency"""
    request.send_response(200, 'API', "Sending Broadcast Frequency")
    request.send_header('Content-Type', 'application/json')
    request.end_headers()

    request.wfile.write(json.dumps(dict(freq=player.get_freq())))


def api_play(request, n):
    """Handle API request to Play Song n-> [int|"all"|"shuffle"]."""
    if n not in player.get_collection() and n not in ["all", "shuffle"]:
        request.api_error(json.dumps(dict(error=True)))
        return

    request.send_response(202, 'API', "Requesting playing %r" % n)
    request.send_header('Content-Type', 'application/json')
    request.end_headers()

    request.wfile.write(json.dumps(dict(playing=True)))
    player.play(n)


def api_queue(request, n):
    """Handle API request to Add to playlist"""
    if n not in player.get_collection():
        request.api_error("%d not found in collection" % n)
        return

    request.send_response(200, 'API', "Requesting queuing %d" % n)
    request.send_header('Content-Type', 'application/json')
    request.end_headers()

    request.wfile.write(json.dumps(dict(queued=player.get_collection().get(n))))
    player.queue(n)


def api_subscribe(request, port):
    ip_address = request.client_address[0]

    if ip_address not in _subscribers:
        _subscriber_lock.acquire()
        _subscribers[ip_address] = port
        _subscriber_lock.release()

        request.send_response(200, 'API', "Requesting subscription %s:%d" % (ip_address, port))
        request.send_header('Content-Type', 'application/json')
        request.end_headers()

        request.wfile.write(json.dumps(dict(subscribed=True)))

    else:
        request.send_response(200, 'API', "User already has subscription %s:%d" % (ip_address, port))
        request.send_header('Content-Type', 'application/json')
        request.end_headers()

        request.wfile.write(json.dumps(dict(subscribed=True)))

    _inform_subscriber(ip_address)


def api_unsubscribe(request):
    ip_address = request.client_address[0]

    if ip_address in _subscribers:
        _subscriber_lock.acquire()
        _subscribers.pop(ip_address)
        _subscriber_lock.release()

        request.send_response(200, 'API', "Requesting unsubscription %s" % ip_address)
        request.end_headers()

        request.wfile.write(json.dumps(dict(subscribed=False)))

    else:
        api_error(request, json.dumps(dict(subscribed=False)))


def api_output(request, output):
    radio_out = (output == "radio")

    if radio_out == player.get_mode():
        request.send_response(200, 'API', "Output already set to %s" % output)
        request.end_headers()

        request.wfile.write("Output already set to %s\n" % output)
    else:
        request.send_response(200, 'API', "Switching output to %s" % output)
        request.end_headers()

        request.wfile.write("Switching output to %s\n" % output)
        player.set_mode(radio_out)


def api_error(request, message):
    request.send_response(400, 'API', message)
    request.end_headers()

    request.wfile.write("%s\n" % message)


def inform_subscribers():
    _subscriber_lock.acquire()
    for subscriber in _subscribers:
        _inform_subscriber(subscriber)
    _subscriber_lock.release()


def _inform_subscriber(subscriber):
    status = player.get_status_json()
    req = network.MyRequest(
            "http://%s:%d/notify/status" % (subscriber, _subscribers[subscriber]),
            data=status
    )

    if not req.get_page():
        player.log.debug("Unsubscribing %s" % subscriber)
        _subscribers.pop(subscriber)
