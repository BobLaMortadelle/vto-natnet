from time import sleep
import time
from djitellopy import Tello
from aruco_detect import ArucoSquare
from Talent_lights_rt import LightsOn
import cv2
import threading

# To signal readiness of video stream
stream_ready = threading.Event()
searching = threading.Event()
spotting = threading.Event()
approaching = threading.Event()
interacting = threading.Event()


def display_approach_pattern(tello, pattern):
    print('Waiting for event to signal video readiness')
    stream_ready.wait()

    tello.send_expansion_command("led 0 0 0")
    tello.send_expansion_command("mled sc")

    if(pattern == 'searching'):
        # chase for searching
        chase = ["{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(66)+"{0:08b}".format(132),
        "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(34)+"{0:08b}".format(17),
        "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(17)+"{0:08b}".format(34),
        "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(132)+"{0:08b}".format(66)]
        start_pattern = time.time()
        tello.send_expansion_command("led br 2.5 75 75 255")
        cycleStep = 0
        while(True):
            while(cycleStep < 4):
                if(time.time() - start_pattern > 0.1):
                    tello.send_expansion_command("mled g " + chase[cycleStep].replace('1', 'b'))
                    start_pattern = time.time()
                    cycleStep += 1
            cycleStep = 0

    elif(pattern == 'spotting'):
        # morse for spotting
        morse = "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102)
        nbcycle = 0
        cycleStep = 0
        start_pattern = time.time()
        gapMorse = time.time()
        matriceOn = False
        tello.send_expansion_command("led br 2.5 255 0 0")
        while(nbcycle < 5):
            spotting.wait()
            if(time.time() - gapMorse > 1):
                while(cycleStep <5):
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
                gapMorse = time.time()
                cycleStep = 0
                nbcycle += 1
        tello.send_expansion_command("mled sc")
        tello.send_expansion_command("led 0 0 0")    

    elif(pattern == 'approaching'):        
        # onedecent for approaching
        onedecent = ["{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102),
                    "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153),
                    "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153),
                    "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)]
        start_pattern = time.time()
        tello.send_expansion_command("led br 0.15 255 100 0")
        nbcycle = 0
        cycleStep = 0
        while(nbcycle < 5):
            while(cycleStep < 4):
                if(time.time() - start_pattern > 0.1):
                    tello.send_expansion_command("mled g " + onedecent[cycleStep].replace('1', 'p'))
                    start_pattern = time.time()
                    cycleStep += 1
            cycleStep = 0
            nbcycle += 1
        tello.send_expansion_command("mled sc")
        tello.send_expansion_command("led 0 0 0")

    elif(pattern == 'interacting'):
        # solid for ready to interact
        solid = "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102)
        start_pattern = time.time()
        tello.send_expansion_command("led 0 255 0")
        tello.send_expansion_command("mled g " + solid.replace('1', 'b'))
        solidLightOn = True
        while(solidLightOn == True):
            if(time.time() - start_pattern > 5):
                tello.send_expansion_command("mled sc")
                tello.send_expansion_command("led 0 0 0")
                solidLightOn = False
    else:
        print('The following pattern does not exist: ', pattern)

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
        if ((time.time()-starttime > 0.1)):
            # Start displaying the drone camera frames
            frame = tello.get_frame_read().frame 
            cv2.imshow("Drone Cam", frame)

            if not stream_ready.set():
                stream_ready.set()
                print('Event: stream is Live')

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Operation manually terminated.")
                break

            # Detect Aruco markers
            corners, ids = aruco_detector.find_aruco_markers(frame)
            if ids is not None:
                for id in ids:
                    if id == 0:
                        if not spotting.set():
                            spotting.set()
                            print('Event: victim detected')
                        print("human found")
            starttime= time.time()
    cv2.destroyAllWindows()

def fly():
    sim_start_time = time.time()
    searching.set()
    while True:
        # Limite the experience to 4 minutes
        if time.time()-sim_start_time > 240:
            print("Experience exceed expected time.")
            break
        else:
            print('.')

def threading_routine(tello):
    stream_ready.wait()
    while True :
        if searching.set():
            searching_thread = threading.Thread(target=display_approach_pattern, args=(tello,'searching',))
            searching_thread.daemon = True
            searching_thread.start()
        if spotting.set(): #check how to disable the searching.set()
            searching_thread.stop()
            spotting_thread = threading.Thread(target=display_approach_pattern, args=(tello,'spotting',))
            spotting_thread.daemon = True
            spotting_thread.start()
        if approaching.set():
            spotting_thread.stop()
            approaching_thread = threading.Thread(target=display_approach_pattern, args=(tello,'approaching',))
            approaching_thread.daemon = True
            approaching_thread.start()
        if interacting.set():
            approaching_thread.stop()
            interacting_thread = threading.Thread(target=display_approach_pattern, args=(tello,'interacting',))
            interacting_thread.daemon = True
            interacting_thread.start()

def main():
    #connect
    tello = Tello()
    tello.connect()
    tello.streamon()
    stream_thread = threading.Thread(target=stream_video, args=(tello,))
    stream_thread.daemon = True
    # searching_thread = threading.Thread(target=display_approach_pattern, args=(tello,'searching',))
    # searching_thread.daemon = True
    # spotting_thread = threading.Thread(target=display_approach_pattern, args=(tello,'spotting',))
    # spotting_thread.daemon = True
    threading_routine_thread = threading.Thread(target=threading_routine, args=(tello,))
    threading_routine_thread.daemon = True
    stream_thread.start()
    # searching_thread.start()
    threading_routine_thread.start()
    # spotting_thread.start()
    fly()
    #tello.reboot()


if __name__=="__main__":
    main()
