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
from aruco_detect import ArucoSquare
import cv2
import cv2.aruco as aruco
# For pybullet :
# import pybullet as p
# import pybullet_data

# We are using our own Logger here for convenience
# from logger import Logger
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





def main():
    # PyBullet Visualization
    visualize = False#True

    # receive the list of waypoints from a json file
    # load the misson
    file = open('detect_human.json')
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
    nb_turn = 0
    lastPointReached = False
    list_of_located_positions = np.empty((0, 3))

    #---------- OpTr- ACID - -----IP------
    ac_list = [['69', '69', '192.168.1.69'],]

    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i,id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)

    #### Initialize the logger #################################
    # log = Logger(logging_freq_hz=30, #int(ARGS.simulation_freq_hz/AGGR_PHY_STEPS),
    #             num_drones=num_vehicles, ) #duration_sec=100 )

    print('Connecting to Tello Swarm...')
    swarm.connect()
    print('Connected to Tello Swarm...')
    
    
    id_dict = dict([('69','69')]) # rigidbody_ID, aircraft_ID
    # vehicles = dict([(ac_id, Vehicle(ac_id)) for ac_id in id_dict.keys()])
    vehicles = dict([(ac_id, swarm.tellos[i]) for i,ac_id in enumerate(id_dict.keys())])
    # print(id_dict.keys(), vehicles['0'].get_ac_id())
    voliere = VolierePosition(id_dict, vehicles, freq=100, vel_samples=6)



    # def marker_detected_action(corners, ids):
    #     # To notify the rescue team that a human has been found by the drone
    #     print("Human found, ID: {ids}")

    swarm.tellos[0].streamon()
    aruco_detector = ArucoSquare()


    voliere.run()
    sleep(2)
    print("Starting Natnet3.x interface at %s" % ("1234567"))


    # Simulation starts
    sim_start_time = time.time()
    starttime= time.time()


    print("Current Tello Battery ",swarm.tellos[0].get_battery())
    swarm.takeoff()        #desactivated because of buildings in flying area
    
    try:
        while True:
             # Limite the experience to 4 minutes
            if time.time()-sim_start_time > 240:
                print("Experience exceed expected time.")
                break
                
            #time.sleep(0.1)
            if ((time.time()-starttime > 0.1)):
                need_interaction_time = False
                # Start displaying the drone camera frames
                frame = swarm.tellos[0].get_frame_read().frame 
                cv2.imshow("Drone Cam", frame)

                # Exit if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Operation manually terminated.")
                    break  
                
                # Detect Aruco markers
                corners, ids = aruco_detector.find_aruco_markers(frame)
                if ids is not None:
                    need_interaction_time = False
                    is_far_enough = True
                    #print("I see !")
                    current_position = np.array([swarm.tellos[0].position_enu])
                    #new_position = np.array([current_position])
                    
                    for i in range (len(list_of_located_positions)):
                        if ((current_position[0][0]-list_of_located_positions[i][0] <1  and current_position[0][0]-list_of_located_positions[i][0] > -1)
                            or (current_position[0][1]-list_of_located_positions[i][1] <1  and current_position[0][1]-list_of_located_positions[i][1] > -1)):
                            is_far_enough = False
                            break
                    
                    if is_far_enough:
                        print(ids.size)             
                        list_of_located_positions = np.append(list_of_located_positions, current_position, axis=0)
                        print("Human found")
                        print("Located at position: ", current_position)
                        print("list of located victims: ", list_of_located_positions)
                        need_interaction_time = True
                        
                    # else:
                    #     print("New position is too close to an existing location, not adding to the list.")

                    

                    #aruco.drawDetectedMarkers(frame, corners, ids)
                    #swarm.tellos[0].send_rc_control(0, 0, 0, 0)
                    

                

            

                if((time.time() > interaction_time)):
                    if(nb_turn <= 4):
                        swarm.tellos[0].fly_to_enu([wPListPos[wPCounter][0], wPListPos[wPCounter][1], wPListPos[wPCounter][2]], wPListHeading[wPCounter])
                        dist = euclidean_distance(swarm.tellos[0].position_enu, wPListPos[wPCounter])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[wPCounter]) #% 2 * math.pi
                    else:
                        swarm.land()
                    
                # reach the position of the currently loaded waypoint close enough in distance and angle
                
                    if(wPCounter < lengthWPs-1):
                        if(dist <= epsilonDist and (angle <= minepsilonAngle or angle >= maxepsilonAngle)):
                            if(need_interaction_time):
                                interaction_time = time.time()+10
                            wPCounter += 1
                            print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " way point number: ", wPCounter, " distance to goal: ", dist, " angle to goal: ", angle)
                            print("WP number: ", wPCounter)
                    else:
                        wPCounter = 1
                        nb_turn += 1
                else:
                    swarm.tellos[0].fly_to_enu([wPListPos[wPCounter-1][0], wPListPos[wPCounter-1][1], wPListPos[wPCounter-1][2]], wPListHeading[wPCounter-1])
            starttime= time.time()
                    

        #### Save the simulation results ###########################
        # log.save(flight_type='Tello')
        #swarm.move_down(int(40))
        # swarm.land()
        # voliere.stop()
        # swarm.end()

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        # log.save(flight_type='Tello')
        #swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        # if visualize:
        #     p.disconnect(physicsClientId=physicsClient)
        # sleep(1)

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
    finally:
        cv2.destroyAllWindows()
        swarm.land()
        voliere.stop()
        swarm.end()

if __name__=="__main__":
    main()
