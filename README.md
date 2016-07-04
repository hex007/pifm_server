**RiPlay -> RaspberryPi Radio Interface Player**

A simple API handling server for PiFM to control Raspberry Pi fm transmission. Can be easily extended to serve web pages or to be controlled using buttons connected to GPIO pins for standalone function. 

Since Python has an easily modifiable server, this was easy. 


Tested with RPi 1 and Zero. For others just update the pifm binary with a working one and change command line for pifm in player.py

    radio = subprocess.Popen(["./pifm_binary_name", parameters...], stdin=player.stdout)
    
To test pifm try:

    avconv -i MUSIC_FILE s16le -ar 22.05k -ac 1 - | sudo ./pifm - FREQ

**Install instruction (on RPi a.k.a. Server):**

    # Install avconv 
    sudo apt-get update
    sudo apt-get install libav-tools
    
    git clone https://github.com/hex007/pifm_server
    cd pifm_server
    g++ -O3 -o pifm pifm.c
    mkdir Music
    # copy music to Music/

    # start server
    sudo python main.py


**API Documentation**

Using a client to send requests to Server

1. Get Music Collection : returns JSONobject

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
