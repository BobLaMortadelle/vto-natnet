from time import sleep
import time
from djitellopy import TelloSwarm
from voliere import VolierePosition
from voliere import Vehicle
from voliere import Vehicle as Target
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
    list_of_located_positions = np.empty((0, 3))
    while True:
        # Limite the experience to 4 minutes
        if time.time()-sim_start_time > 240:
            print("Experience exceed expected time.")
            break
        if ((time.time()-starttime > 0.1)):
            # Start displaying the drone camera frames
            frame = tello.get_frame_read().frame 
            cv2.imshow("Drone Cam", frame)

            if not stream_ready.is_set():
                stream_ready.set()
                #print('Event: stream is Live')

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Operation manually terminated.")
                break

            # Detect Aruco markers
            corners, ids = aruco_detector.find_aruco_markers(frame)
            if ids is not None:
                for id in ids:
                    if id == 0 and not spotting.set():
                        #need_interaction_time = False
                        is_far_enough = True
                        #print("I see !")
                        current_position = np.array([tello.position_enu])
                        #new_position = np.array([current_position])
                        
                        for i in range (len(list_of_located_positions)):
                            if ((current_position[0][0]-list_of_located_positions[i][0] <1  and current_position[0][0]-list_of_located_positions[i][0] > -1)
                                or (current_position[0][1]-list_of_located_positions[i][1] <1  and current_position[0][1]-list_of_located_positions[i][1] > -1)):
                                is_far_enough = False
                                break
                        
                        if is_far_enough:
                            print(ids.size)             
                            list_of_located_positions = np.append(list_of_located_positions, current_position, axis=0)
                            if not spotting.is_set():
                                spotting.set()
                                print('Event: victim detected')
                            print("Human found")
                            print("Located at position: ", current_position)
                            print("list of located victims: ", list_of_located_positions)
                            #need_interaction_time = True


            starttime= time.time()
    cv2.destroyAllWindows()


def norm_ang(x):
            while x > np.pi :
                x -= 2*np.pi
            while x < -np.pi :
                x += 2*np.pi
            return x


def euclidean_distance(pos, goal):
    return math.sqrt((goal[0]-pos[0])**2 + (goal[1]-pos[1])**2 + (goal[2]-pos[2])**2)

def heading_distance(pos, goal):
    return norm_ang(norm_ang(goal)- norm_ang(pos))


def flight_routine(swarm, voliere):
    # wait for the drone to live stream before takeoff
    stream_ready.wait()

    # receive the list of waypoints from a json file
    # load the misson
    file = open('Task1_handover_voliere.json')
    command = json.load(file)
    
    lengthWPs = len(command['wayPoints'])
    wPListPos = [[0]*3] * lengthWPs
    wPListHeading = [0] * lengthWPs
    for i in range (lengthWPs):
        x = command['wayPoints'][i]['x']
        y = command['wayPoints'][i]['y']
        z = command['wayPoints'][i]['z']
        theta = command['wayPoints'][i]['theta']
        
        #v = command['velocity']
        wPListPos[i] = [x, y, z]
        wPListHeading[i] = None if theta == None else 2 * math.pi * theta / 360  # conversion from degrees to rad

    print(wPListPos)
    print(wPListHeading)

    wPCounter = 1
    epsilonDist = 0.2
    minepsilonAngle = 0.2
    maxepsilonAngle = 6.08
    interaction_time = 0
 



    # Simulation starts
    sim_start_time = time.time()
    print("Current Tello Battery ",swarm.tellos[0].get_battery())
    try:
        swarm.takeoff()
        lastPointReached = False
        starttime= time.time()
        while time.time()-sim_start_time < 240:
            if(lastPointReached == True):
                break
            # print(time.time()-sim_start_time)
            if ((time.time()-starttime > 0.025)):
                if((time.time() > interaction_time)):
                    if(lastPointReached == False):
                        swarm.tellos[0].fly_to_enu([wPListPos[wPCounter][0], wPListPos[wPCounter][1], wPListPos[wPCounter][2]], wPListHeading[wPCounter])
                        dist = euclidean_distance(swarm.tellos[0].position_enu, wPListPos[wPCounter])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[wPCounter]) #% 2 * math.pi   
                    #print("angle: ", angle)
                    
                # reach the position of the currently loaded waypoint close enough in distance and angle
                
                    if(wPCounter < lengthWPs-1):
                        if(dist <= epsilonDist and (angle %(2*math.pi)<= minepsilonAngle or angle%(2*math.pi) >= maxepsilonAngle)):
                            if((wPListPos[wPCounter] == wPListPos[wPCounter-1]) and (wPListHeading[wPCounter] == wPListHeading[wPCounter-1])):
                                interaction_time = time.time()+10
                                print("Time to wait!")
                                swarm.tellos[0].send_rc_control(0, 0, 0, 0)
                            wPCounter += 1
                            print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " way point number: ", wPCounter, " distance to goal: ", dist, " angle to goal: ", angle)
                            print("WP number: ", wPCounter)
                    else:
                        lastPointReached = True
                else:
                    swarm.tellos[0].fly_to_enu([wPListPos[wPCounter-1][0], wPListPos[wPCounter-1][1], wPListPos[wPCounter-1][2]], wPListHeading[wPCounter-1])
                starttime= time.time()
                    

        #### Save the simulation results ###########################
        # log.save(flight_type='Tello')
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        # log.save(flight_type='Tello')
        #swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        # if visualize:
        #     p.disconnect(physicsClientId=physicsClient)
        sleep(1)

    except (ValueError):
        swarm.land()
        voliere.stop()
        swarm.end()

    except OSError:
        print("Natnet connection error")
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        exit(-1)

def main():
    # Connect to the drone
    #---------- OpTr- ACID - -----IP------
    ac_list = [['244', '244', '192.168.1.244'],]

    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i,id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)

    print('Connecting to Tello Swarm...')
    swarm.connect()
    print('Connected to Tello Swarm...')

    id_dict = dict([('244','244')]) # rigidbody_ID, aircraft_ID
    vehicles = dict([(ac_id, swarm.tellos[i]) for i,ac_id in enumerate(id_dict.keys())])
    voliere = VolierePosition(id_dict, vehicles, freq=100, vel_samples=6)

    voliere.run()
    sleep(2)
    print("Starting Natnet3.x interface at %s" % ("1234567"))

    # Enable live stream of the first swarm's tello
    swarm.tellos[0].streamon()
    print('cam switched on')
    stream_thread = threading.Thread(target=stream_video, args=(swarm.tellos[0],))
    stream_thread.daemon = True
    stream_thread.start()

    flight_routine(swarm, voliere)





if __name__=="__main__":
    main()
