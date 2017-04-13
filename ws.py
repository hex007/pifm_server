#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ,--(saket)--(RiPlayServer)--(27/07/16 07:49)--(【ツ】)---
# `--(~/ws.py$)-->
import json
import re
from threading import Lock

import player


__tag__ = 'ws.py'

_subscribers = list()
_subscriber_lock = Lock()


def handler(connection, data):
    """Handle WS requests"""
    if data == "status":
        ws_status(connection)

    elif data == "start":
        ws_start(connection)

    elif data == "stop":
        ws_stop(connection)

    elif data == "skip":
        ws_skip(connection)

    elif data == "collection":
        ws_collection(connection)

    elif data == "playlist":
        ws_playlist(connection)

    elif data == "clear":
        ws_clear(connection)

    elif data == "freq":
        ws_freq(connection)

    elif re.match(r"play (?:\d+|all|shuffle)", data):
        n = data.split()[1]
        ws_play(connection, n if n in ["all", "shuffle"] else int(n))

    elif re.match(r"queue \d+", data):
        n = int(data.split()[1])
        ws_queue(connection, n)

    elif re.match(r"output (?:radio|audio)", data):
        ws_output(connection, data.split()[1])

    else:
        connection.sendMessage(data)


def ws_start(connection):
    """Handle WS request to Start player"""
    # connection.sendMessage(json.dumps(dict(started=True)))
    player.start_player()


def ws_stop(connection):
    """Handle WS request to Stop player"""
    # connection.sendMessage(json.dumps(dict(stopped=True)))
    player.stop_player()


def ws_skip(connection):
    """Handle WS request to Skip song"""
    if not player.get_playlist():
        connection.sendMessage(json.dumps(dict(skipped=None)))
        return

    # connection.sendMessage(json.dumps(dict(skipped=player.get_playlist()[0])))
    player.skip()


def ws_collection(connection):
    """Handle WS request for Music Collection"""
    connection.sendMessage(player.get_collection_json())


def ws_playlist(connection):
    """Handle WS request for current Playlist"""
    connection.sendMessage(player.get_playlist_json())


def ws_status(connection):
    """Handle WS request for current status"""
    connection.sendMessage(player.get_status_json())


def ws_clear(connection):
    """Handle WS request to clear playlist"""
    # connection.sendMessage(json.dumps(dict(cleared=True)))
    player.clear()


def ws_freq(connection):
    """Handle WS request for Broadcast Frequency"""
    connection.sendMessage(json.dumps(dict(freq=player.get_freq())))


def ws_play(connection, n):
    """Handle WS request to Play Song n-> [int|"all"|"shuffle"]."""
    # connection.sendMessage(json.dumps(dict(playing=True)))
    player.play(n)


def ws_queue(connection, n):
    """Handle WS request to Add to playlist"""
    connection.sendMessage(json.dumps(dict(queued=player.get_collection().get(n))))
    player.queue(n)


def ws_subscribe(connection):
    if connection not in _subscribers:
        _subscriber_lock.acquire()
        _subscribers.append(connection)
        _subscriber_lock.release()

    _inform_subscriber(connection)


def ws_unsubscribe(connection):
    if connection in _subscribers:
        _subscriber_lock.acquire()
        _subscribers.remove(connection)
        _subscriber_lock.release()


def ws_output(connection, output):
    radio_out = (output == "radio")

    if radio_out != player.get_mode():
        connection.sendMessage(json.dumps(dict(output=output)))
        player.set_mode(radio_out)


def inform_subscribers():
    _subscriber_lock.acquire()
    for subscriber in _subscribers:
        _inform_subscriber(subscriber)
    _subscriber_lock.release()


def _inform_subscriber(subscriber):
    status = player.get_status_json()
    subscriber.sendMessage("status->%s" % status)
