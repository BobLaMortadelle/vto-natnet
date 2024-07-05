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

    # ac_id_list = [[_[0], _[1]] for _ in ac_list]
    # ac_id_list.append(['888', '888']) # Add a moving target (helmet)
    # ac_id_list.append(['890', '890']) # Add a moving target (soft ball)
    # target = [Target('888')]
    # ball = [Target('890')]
    # all_vehicles = swarm.tellos+target_vehicle
    
    
    id_dict = dict([('69','69')]) # rigidbody_ID, aircraft_ID
    # vehicles = dict([(ac_id, Vehicle(ac_id)) for ac_id in id_dict.keys()])
    vehicles = dict([(ac_id, swarm.tellos[i]) for i,ac_id in enumerate(id_dict.keys())])
    # print(id_dict.keys(), vehicles['0'].get_ac_id())
    voliere = VolierePosition(id_dict, vehicles, freq=100, vel_samples=6)


    # voliere = VolierePosition(ac_id_list, swarm.tellos+target+ball, freq=40)
    voliere.run()
    sleep(2)
    # TODO run the voliere program first for few seconds to be sure the connection is good 
    print("Starting Natnet3.x interface at %s" % ("1234567"))

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
                    print("angle: ", angle)

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

if __name__=="__main__":
    main()
