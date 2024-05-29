from time import sleep
import time
from djitellopy import Tello
import pdb
import numpy as np
import json
import math
import cv2
import threading
from aruco_detect import ArucoSquare




# To signal readiness of video stream
stream_ready = threading.Event()
searching = threading.Event()
spotting = threading.Event()
approaching = threading.Event()
interacting =threading.Event()


def stream_video(tello):
    aruco_detector = ArucoSquare()
    # Simulation starts
    sim_start_time = time.time()
    starttime= time.time()
    while True:
        # Limite the experience to 4 minutes
        if time.time()-sim_start_time > 240:
            print("Experience exceed expected time.")
            break
        if ((time.time()-starttime > 0.05)):
            # Start displaying the drone camera frames
            frame = tello.get_frame_read().frame 
            cv2.imshow("Drone Cam", frame)
            
            if not stream_ready.is_set():
                stream_ready.set()
                searching.set()
                
                #print('Event: stream is Live')

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Operation manually terminated.")
                break

            # Detect Aruco markers
            corners, ids = aruco_detector.find_aruco_markers(frame)
            if ids is not None:
                for id in ids:
                    if id == 0 and not spotting.is_set() and not approaching.is_set() and not interacting.is_set():
                        searching.clear()
                        spotting.set()
                        print('Event: victim detected')
                        print("Human found")

            starttime= time.time()
    cv2.destroyAllWindows()


def fly(tello):
    stream_ready.wait()
    tello.turn_motor_on()
    counter = 0
    while True:
        counter += 1
        #print(".")


def display_approach_pattern(tello):
    print('Waiting for event to signal video readiness')
    stream_ready.wait()

    tello.send_expansion_command("led 0 0 0")
    tello.send_expansion_command("mled sc")


    # chase for searching
    chase = ["{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(66)+"{0:08b}".format(132),
    "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(34)+"{0:08b}".format(17),
    "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(17)+"{0:08b}".format(34),
    "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(132)+"{0:08b}".format(66)]

    # morse for spotting
    morse = "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102)

    # onedecent for approaching
    onedecent = ["{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102),
                "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153),
                "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153),
                "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)]

    # solid for ready to interact
    solid = "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102)

    start_pattern = time.time()

    cycleStep = 0

    while(True):
        if(searching.is_set()):
            #print("searching")
            #tello.send_expansion_command("led br 2.5 75 75 255")
            if(time.time() - start_pattern > 0.1):
                tello.send_expansion_command("mled g " + chase[cycleStep % 4].replace('1', 'b'))
                start_pattern = time.time()
                cycleStep += 1

        elif(spotting.is_set()):
            print("spotting")
            cycleStep = 0
            start_pattern = time.time()
            matriceOn = False
            tello.send_expansion_command("led br 2.5 255 0 0")
            while(cycleStep < 4):
                delay = time.time() - start_pattern
                if(delay > 0.1 and delay < 0.3 and matriceOn == False):
                    tello.send_expansion_command("mled g " + morse.replace('1', 'r'))
                    matriceOn = True
                elif(delay > 0.3 and delay < 0.4 and matriceOn == True):
                    tello.send_expansion_command("mled sc")
                    matriceOn = False
                elif(delay > 0.4):
                    start_pattern = time.time()
                    cycleStep += 1
            spotting.clear()
            approaching.set()
            tello.send_expansion_command("mled sc")
            tello.send_expansion_command("led 0 0 0")    

        elif(approaching.is_set()):
            print("approaching")
            cycleStep = 0      
            start_pattern = time.time()
            tello.send_expansion_command("led br 0.15 255 100 0")
            while(cycleStep < 4):
                if(time.time() - start_pattern > 0.1):
                    tello.send_expansion_command("mled g " + onedecent[cycleStep % 4].replace('1', 'p'))
                    start_pattern = time.time()
                    cycleStep += 1
            tello.send_expansion_command("mled sc")
            tello.send_expansion_command("led 0 0 0")

        elif(interacting.is_set()):
            print("interacting")
            start_pattern = time.time()
            tello.send_expansion_command("led 0 255 0")
            tello.send_expansion_command("mled g " + solid.replace('1', 'b'))
            solidLightOn = True
            while(solidLightOn == True):
                if(time.time() - start_pattern > 5):
                    tello.send_expansion_command("mled sc")
                    tello.send_expansion_command("led 0 0 0")
                    solidLightOn = False



def main():
    # Connect to the drone
    tello = Tello()
    tello.connect()
    
    #switch on camera
    tello.streamon()
    #tello.set_video_direction(1)
    print('cam switched on')
    stream_thread = threading.Thread(target=stream_video, args=(tello,))
    stream_thread.daemon = True
    stream_thread.start()
    print('stream running')

    display_thread = threading.Thread(target=display_approach_pattern, args=(tello,))
    display_thread.daemon = True
    display_thread.start()
    print('display running')
    try:
        fly(tello)
    except (KeyboardInterrupt, SystemExit):
        tello.turn_motor_off()
        tello.send_expansion_command("mled sc")
        tello.send_expansion_command("led 0 0 0")





if __name__=="__main__":
    main()