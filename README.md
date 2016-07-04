**RiPlay -> RaspberryPi Radio Interface Player**

Since Python has an easily modifiable server, this was a necessity

Tested with RPi Zero

**Install instruction (on RPi a.k.a. Server):**

    git clone REPO_LINK
    g++ -O3 -o pifm pifm.c
    mkdir Music
    # copy music to Music/

    # start server
    sudo python main.py

**API Documentation**

1. Get Music Collection from Client : returns JSONobject

        curl http://raspberrypi.local:8080/api/collection

        # For formatted Collection ->
        curl http://raspberrypi.local:8080/api/collection | sed "s|\", \"|\"\\n\"|g"

2. Get playlist : returns JSONarray

        curl http://raspberrypi.local:8080/api/playlist

3. Get Broadcast Frequency

        curl http://raspberrypi.local:8080/api/freq

4. Play X = [N|all|shuffled] from Collection

        curl http://raspberrypi.local:8080/api/play/X

5. Queue X = [N|all|shuffled] from Collection

        curl http://raspberrypi.local:8080/api/queue/X

6. Stop player, leave queue as playlist

        curl http://raspberrypi.local:8080/api/stop

7. Start player, continue with playlist

        curl http://raspberrypi.local:8080/api/start

8. Skip song in playlist

        curl http://raspberrypi.local:8080/api/skip

9. Clear playlist; keeps current song if playing

        curl http://raspberrypi.local:8080/api/clear