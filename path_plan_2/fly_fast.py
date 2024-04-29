from time import sleep
import time
from djitellopy import TelloSwarm
from voliere import VolierePosition
from voliere import Vehicle as Target
import pdb
import numpy as np



import scipy
from numpy import linalg
import math
import pyclipper
from shapely.geometry import Point, Polygon
# from google.colab import files
from datetime import datetime
import random
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import animation
from IPython.display import HTML
from matplotlib import rc
from mpl_toolkits import mplot3d
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import os
import time
import argparse
import pdb
from itertools import compress


from path_plan_forward_propagate import ArenaMap , Cases, Flow_Velocity_Calculation, Vehicle, curvature

from Logger import Logger

# import threading

def main():
    # PyBullet Visualization
    visualize = False#True

    #---------- OpTr- ACID - -----IP------
    ac_list = [['69', '69', '192.168.1.69'],]
    # ac_list =  [['61', '61', '192.168.1.61'],]
                # ['62', '62', '192.168.1.62'],
                # ['63', '63', '192.168.1.63'] ]

    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i,id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)

        

    # Arena  = ArenaMap(61,'manual')
    # ArenaR = ArenaMap(61,'manual')
    # Arena.Inflate(radius = 0.2) #0.1
    # Arena.Panelize(size= 0.01) #0.08
    # Arena.Calculate_Coef_Matrix(method = 'Vortex')
    # Case = Cases(61,Arena,'manual')
    # vehicle_list = Case.Vehicle_list

    # Arena 6 - Case 121

    Arena  = ArenaMap(65,'manual')
    ArenaR = ArenaMap(65,'manual')

    # Arena  = ArenaMap(61,'manual')
    # ArenaR = ArenaMap(61,'manual')
    Arena.Inflate(radius = 0.2) #0.1
    Arena.Panelize(size= 0.01) #0.08
    Arena.Calculate_Coef_Matrix(method = 'Vortex')
    Case = Cases(61,Arena,'manual')
    vehicle_list = Case.Vehicle_list
    # maglist=[0.05, 0. , -0.05]
    # vinfmag_list = [0.05, 0.025, 0.01, 0. , -0.01, -0.025, -0.05]
    # vinfmag_list = [0.05, 0.025,  0. , -0.025, -0.05]
    vinfmag_list = [0.05, 0. , -0.05]
    dt  = 0.02
    hor = 3.0



    current_vehicle_list = vehicle_list

    for i, vehicle in enumerate(current_vehicle_list):
        vehicle.arena = Arena
        vehicle.vehicle_list = current_vehicle_list


   # The below vehicles should be converted to Tellos...
    # vehicle_list = [Vehicle(name,source) for name , source in zip(vehicle_name_list, vehicle_source_list)]
    # vehicle_list = [Vehicle(name,source, imag_source) for name , source, imag_source in zip(vehicle_name_list, vehicle_source_list, vehicle_imaginary_source_list)]
    num_vehicles = len(id_list)
    # INIT_XYZS = np.array(vehicle_pos_list)
    INIT_RPYS = np.zeros([num_vehicles,3])
    TARGET_VELS = np.zeros([num_vehicles,3])
    FLOW_VELS = np.zeros([num_vehicles,3])

    # Tello class should have these Set_Goal-Goto_Goal-Set_position functions...
    # for vehicle,set_goal,goto_goal,pos in zip(vehicle_list,vehicle_goal_list,vehicle_goto_goal_list,vehicle_pos_list):
    #     vehicle.Set_Goal(set_goal[0],set_goal[1],set_goal[2])
    #     vehicle.Go_to_Goal(goto_goal[0],goto_goal[1],goto_goal[2],goto_goal[3])
    #     vehicle.Set_Position(pos)
        # pdb.set_trace()

    # current_vehicle_list = vehicle_list

    #### Initialize the logger #################################
    logger = Logger(logging_freq_hz=30, #int(ARGS.simulation_freq_hz/AGGR_PHY_STEPS),
                    num_drones=num_vehicles, traj_nr=len(vinfmag_list), traj_len=int(hor/dt)-1) #duration_sec=100 )

    print('Connecting to Tello Swarm...')
    swarm.connect()
    print('Connected to Tello Swarm...')

    ac_id_list = [[_[0], _[1]] for _ in ac_list]

    ac_id_list.append(['888', '888']) # Add a moving target
    target_vehicle = [Target('888')]
    # all_vehicles = swarm.tellos+target_vehicle

    voliere = VolierePosition(ac_id_list, swarm.tellos+target_vehicle, freq=20)
    # voliere = VolierePosition(ac_id_list, swarm.tellos, freq=20)
    # pdb.set_trace()


    print("Starting Natnet3.x interface at %s" % ("1234567"))

    # Simulation starts
    sim_start_time = time.time()
    try:
        # Start up the streaming client.
        # This will run perpetually, and operate on a separate thread.
        voliere.run()
        sleep(3.)

        swarm.takeoff()   # DONT FORGET TO TAKE-OFF

        # swarm.move_up(int(40))
        # swarm.tellos[0].move_up(int(20))
        # swarm.tellos[1].move_up(int(80))
        # swarm.tellos[2].move_up(int(100))
        nr_vehicle = len(id_list)
        # fields[0].gvf_parameter = 700./nr_vehicle

        # # Debug loop :
        heading = 0 #-np.pi-0.002
        j=0


        


        # Main loop :
   
        trace_count = 0
        set_vel_time = time.time()
        flight_finished=False
        starttime= time.time()
        vinfmag = 0.
        k=19

        for i, vehicle in enumerate(vehicle_list):
            vehicle.start_propagate(dt=dt, hor=hor)
            vehicle.propagated_path=np.zeros((len(vinfmag_list), int(hor/dt)-1, 6))

        while time.time()-sim_start_time < 180:
            if time.time()-starttime > 0.05:
                # print('Step execution duration :',time.time()-starttime )
                k +=1
                # print(f'Freq : {1/(time.time()-starttime):.3f}')
                starttime= time.time()
                # Check if vehicles reached their final position
                # distance_to_destination = [vehicle.distance_to_destination for vehicle in vehicle_list]
                # flight_finished = True if np.all(distance_to_destination) < 0.50 else False
                # print(distance_to_destination)
                # print(f' {vehicle_list[0].distance_to_destination:.3f}  -  {vehicle_list[1].distance_to_destination:.3f}  -  {vehicle_list[2].distance_to_destination:.3f}')
                if flight_finished: break

                # Get Target position to follow
                target_position = target_vehicle[0].position

                for vehicle_nr, vehicle in enumerate(vehicle_list):
                    # print('Heyyo :', target_position, type(target_position))
                    vehicle.Set_Next_Goal(target_position)
                    
                    # # if vehicle.state :
                    # if vehicle.distance_to_destination<0.50:
                    #     print('Changing goal set point')
                    #     vehicle.Set_Next_Goal(vehicle_next_goal_list[goal_index])
                    #     goal_index += 1
                    #     goal_index = goal_index%len(vehicle_next_goal_list)

                
                # flow_vels = Flow_Velocity_Calculation(vehicle_list,Arena)
                for i, vehicle in enumerate(vehicle_list):
                    vehicle.Set_Position(swarm.tellos[i].get_position_enu())
                    vehicle.Set_Velocity(swarm.tellos[i].get_velocity_enu())
                    # print('Voliere position : ', swarm.tellos[i].get_position_enu())

                    # if k == 20:
                    #     future_path = vehicle.propagate_future_path(maglist=vinfmag_list, hor=1.5,  reset_position = True, set_best_state = True)
                    #     best = np.argmin([np.sum(curvature(future_path[i, 30:, 0],future_path[i, 30:, 1])) for i in range(len(vinfmag_list))])
                    #     vinfmag = vinfmag_list[best]
                    #     print('For vehicle ', str(index), 'Best V_inf is: ', str(vinfmag))
                    #     k = 0
                    # vehicle.Go_to_Goal(AoAsgn = np.sign(vinfmag), Vinfmag = np.abs(vinfmag)) 

                    # print(f' {i} - Vel : {vehicle.velocity[0]:.3f}  {vehicle.velocity[1]:.3f}  {vehicle.velocity[2]:.3f}')

                    # future_path = np.zeros((3,74,6))

                use_panel_flow = 1
                if use_panel_flow :
                    flow_vels = Flow_Velocity_Calculation(vehicle_list,Arena)
                    # for i,id in enumerate(id_list):


                    for i, vehicle in enumerate(vehicle_list):

                        FLOW_VELS[i]=flow_vels[i].copy()
                        norm = np.linalg.norm(flow_vels[i])
                        flow_vels[i] = flow_vels[i]/norm
                        # flow_vels[i][2] = 0.0
                        limited_norm = np.clip(norm,0., 1.6)
                        fixed_speed = 1.

                        vel_enu = flow_vels[i]*limited_norm

                        heading = 0.
                        
                        vehicle.Set_Desired_Velocity(vel_enu, method='None')
                        # print(f'Desired Velocity ; {vel_enu}')

                        swarm.tellos[i].send_velocity_enu(vehicle.velocity_desired, heading)
                        TARGET_VELS[i]=vehicle.velocity_desired

                        # swarm.tellos[i].send_velocity_enu(vehicle.velocity_desired, heading)
                        # TARGET_VELS[i]=vehicle.velocity_desired


                    # #### Log the simulation ####################################
                    for i, vehicle in enumerate(vehicle_list):
                        logger.log(drone=i,
                                   timestamp=time.time()-sim_start_time,
                                   state= np.hstack([swarm.tellos[i].get_position_enu(), swarm.tellos[i].get_velocity_enu(), swarm.tellos[i].get_quaternion(),  np.zeros(10)]),#obs[str(j)]["state"],
                                   control=np.hstack([TARGET_VELS[i], FLOW_VELS[i], np.zeros(6)]), # target_vehicle[0].position]),
                                   trajectory=vehicle.propagated_path, #np.hstack([path, np.zeros(2) ])
                                   sim=False
                                   # control=np.hstack([TARGET_VEL[j, wp_counters[j], 0:3], np.zeros(9)])
                                   )





        #### Save the simulation results ###########################
        logger.save(flight_type='agile')
        for i, vehicle in enumerate(vehicle_list):
            vehicle.stop_propagate()
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        plot_log(Arena, ArenaR, logger)

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        logger.save(flight_type='agile')
        for i, vehicle in enumerate(vehicle_list):
            vehicle.stop_propagate()
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        if visualize:
            p.disconnect(physicsClientId=physicsClient)
        sleep(1)
        plot_log(Arena, ArenaR, logger)

    except OSError:
        print("Natnet connection error")
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        plot_log(Arena, ArenaR, logger)
        exit(-1)

def read_w_trajectory(filename):
    with np.load(filename, 'rb') as log:
        timestamp= log['timestamps']
        controls = log['controls']
        states = log['states']
        trajectories = log['trajectories']
    return timestamp, states, controls, trajectories 

def plot_log(Arena, ArenaR, logger):
    
    timestamp = logger.timestamps 
    states    = logger.states
    controls  =logger.controls
    trajectories = logger.trajectories

    fig4 = plt.figure(figsize=(5,5))
    minx = -5 # min(min(building.vertices[:,0].tolist()),minx)
    maxx = 5 # max(max(building.vertices[:,0].tolist()),maxx)
    miny = -5 # min(min(building.vertices[:,1].tolist()),miny)
    maxy = 5 # max(max(building.vertices[:,1].tolist()),maxy)
    #plt.figure(figsize=(20,10))
    plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
    for building in Arena.buildings:
        plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
        plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
    for buildingR in ArenaR.buildings:
        plt.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
        plt.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
    for _v in range(states.shape[0]):
        time = timestamp[_v]
        pos_e = states[_v,0,:]
        pos_n = states[_v,1,:]
        pos_u = states[_v,2,:]

        for i in range(trajectories.shape[1]):
            plt.plot(trajectories[_v, i,:,0, ::20],trajectories[_v, i,:,1,::20], color='g', linewidth = 0.3, alpha = 0.6)

        # plt.plot(pos_e, pos_n)
        plt.plot(pos_e, pos_n, 'o')

    plt.xlim([minx, maxx])
    plt.ylim([miny, maxy])
    plt.show()



if __name__=="__main__":
    main()
