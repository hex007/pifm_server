#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ,--(saket)--(RiPlayServer)--(01/07/16 09:40)--(【ツ】)---
# `--(~/player.py$)-->

import json
import logging
import subprocess
import threading
from random import shuffle


__author__ = 'saket'
__tag__ = 'main'

player = None
radio = None

_player_thread = None
_stop_requested = False
_collection = None
_playlist = []
_volume = 5
_freq = 100.1

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def _start_player():
    """Play all items found on Playlist sequentially on Radio.

    Starts player and radio process. Waits for the processes to end.
    Returns if _stop_requested or playlist is empty
    """
    global player, radio, _stop_requested

    # avconv -i "$1" -f s16le -ar 22.05k -ac 1 - | sudo ./pifm - "$2"
    while _playlist:
        log.info("Playing : %s" % _playlist[0])
        player = subprocess.Popen(
                ["avconv", "-i", "Music/%s" % _playlist[0], "-f", "s16le", "-ar", "44100", "-ac", "2", "-loglevel",
                 "panic", "-"],
                stdout=subprocess.PIPE)
        radio = subprocess.Popen(["./pifm", "-", "%.1f" % _freq, "44100", "stereo", str(_volume)], stdin=player.stdout)
        player.stdout.close()

        log.debug("radio.wait() :)")
        radio.wait()
        log.debug("Radio terminated :)")
        log.debug("player.wait() :)")
        player.wait()
        log.debug("Player terminated :)")

        if _stop_requested:
            _stop_requested = False
            break

        _playlist.pop(0)

    player = None
    radio = None
    log.info("Thread terminated :)")


def _stop_player_process():
    """Stop both Radio and Player processes.

    Does not remove current playing song from playlist. User assumes responsibility of managing playlist.
    Acts like pressing STOP on any media player.
    """
    if radio and radio.poll() is None:
        radio.terminate()
        log.debug("Terminating radio process :)")

    if player and player.poll() is None:
        # For some reason terminate doesnt work and stop has to be called twice.
        # Popen.kill() solves this problem
        player.terminate()
        log.debug("Terminating player process :)")


def start_player(force=False):
    """Start playing music from playlist.

    Creates a thread to act as Player thread to play from playlist.
    Returns if playlist is empty or player is running and not forced.

    :type force:bool Should forcefully stop player
    """
    if not _playlist:
        return

    global _player_thread
    if _player_thread and _player_thread.isAlive():
        if force:
            # Player needs to be restarted
            stop_player()
        else:
            # Player is already running
            return

    _player_thread = threading.Thread(target=_start_player)
    _player_thread.daemon = True
    _player_thread.start()


def stop_player():
    """Stops player without removing currently playing song"""
    global _stop_requested
    _stop_requested = True
    _stop_player_process()


def skip():
    """Skip currently playing music. Stops player which removes currently playing song"""
    _stop_player_process()


def get_collection():
    """
    Read files available and return list of multimedia files available
    :return: dict of files
    :rtype dict
    """
    global _collection
    if _collection:
        return _collection

    process = subprocess.Popen(["ls", "Music/"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    if out:
        # List of Music Files (Assuming only Multimedia files available)
        files = out[:-1].split('\n')

        # todo: Output as JSON?
        _collection = {i + 1: x for i, x in enumerate(files)}
        return _collection

    elif err:
        log.error(err)

    return {}


def get_collection_json():
    """Get complete Collection(dict) as JSON object"""
    return json.dumps(get_collection())


def get_playlist():
    """Get current playlist as list"""
    return _playlist


def clear():
    """Clear current playlist"""
    global _playlist
    if _player_thread and _player_thread.isAlive():
        del _playlist[1:]
    else:
        _playlist = []


def get_playlist_json():
    """Get current playlist as JSON object"""
    return json.dumps(get_playlist())


def play(position):
    """Play item at position in collection as new playlist"""
    global _playlist
    collection = get_collection()
    if position == "all":
        _playlist = [collection[k] for k in collection]
    elif position == "shuffle":
        _playlist = [collection[k] for k in collection]
        shuffle(_playlist)
    elif position in collection:
        _playlist = [collection[position]]
    else:
        log.error("Play requested for %r" % position)

    start_player(True)


def queue(position):
    """Add item at position in collection to playlist"""
    global _playlist
    collection = get_collection()
    _playlist.append(collection[position])
    log.info("Adding : %s" % collection[position])
    start_player()


def get_freq():
    """Return current broadcast frequency"""
    return _freq
