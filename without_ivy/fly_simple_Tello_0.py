from time import sleep
import time
from djitellopy import TelloSwarm
from voliere import VolierePosition
from voliere import Vehicle
from voliere import Vehicle as Target
# from gflow.source import Source
import pdb
import numpy as np

# from path_plan_w_panel import ArenaMap, Vehicle, Flow_Velocity_Calculation_0

# from gflow.arena import ArenaMap
# from gflow.panel_flow import Flow_Velocity_Calculation
# # from gflow.building import Building
# from gflow.vehicle import Vehicle
# from gflow.cases import Cases

# from source import Source

# For pybullet :
import pybullet as p
from time import sleep
import pybullet_data
import pdb
import numpy as np

# from utils import add_buildings

# We are using our own Logger here for convenience
# from logger import Logger

def main():
    # PyBullet Visualization
    visualize = False#True

    #---------- OpTr- ACID - -----IP------
    ac_list = [['66', '66', '192.168.1.66'],]

    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i,id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)

    # case = Cases.get_case(filename='cases.json', casename='ERF23_case_1v')
    # case = Cases.get_case(filename='cases.json', casename='ERF23_case_2v')
    # case = Cases.get_case(filename='cases.json', casename='ERF23_case_3v')
    # vehicles_next_goal_list = [[ [0, 2.5,0.8], [2.5,0,0.8] , [0,-2.5,0.8], [-2.0,0,0.8]], # V0
    #                            [ [0, 2.5,0.8], [-2, 0,0.8] , [0,-2.5,0.8], [ 2.5,0,0.8]], # V1
    #                            [ [-2, 0 ,0.8], [0,2.5,0.8] , [0,-2.5,0.8], [ 2.5,0,0.8]], # V2
    #                            [ [0, 2.5,0.8], [0,-2.5,0.8], [-2, 0 ,0.8], [ 2.5,0,0.8]],]# V3
    

    # case = Cases.get_case(filename='cases.json', casename='DASC23_case_2T')
    # vehicles_next_goal_list = [[ [0,0,0.5] , [2,2,0.5] , [3.,3.,0.5]], # Case2
    #                            [ [-3.5, -3.5 , 1.5] ]] # Intruder



    # vehicle_next_goal_list = [ [1.5,0,0.5] , [1.5,-2,0.5] , [1.5,-3.5,0.5]] #Case3

    # vehicle_next_goal_list = [ [2,0,0.5] , [1,-1,0.5] , [-2,-1,0.5]  , [-3,0,0.5]  , [-3,2,0.5] , [-3,3.5,0.5]] #Case5a

    # vehicle_next_goal_list = [[3., 2, 1.4], [-3., 2, 1.4], [-3., 1, 1.4], [3., 1, 1.4], [3., 0, 1.4], [-3., 0, 1.4], [-3., -1, 1.4], [3., -1, 1.4], [3., -2, 1.4],[-3., -2, 1.4],[-3., -3, 1.4],[3., -3, 1.4], [3., 2, 1.4], [-3., 2, 1.4], [-3., 1, 1.4], [3., 1, 1.4], [3., 0, 1.4], [-3., 0, 1.4], [-3., -1, 1.4], [3., -1, 1.4],  ]
    goal_index = 0


    # arena_version = 65 #102
    # vehicle_name_list =   ['V1']
    # vehicle_source_list = [0.95] # Source_strength
    # vehicle_imaginary_source_list = [1.5] # Imaginary source_strength
    # vehicle_goal_list = [([-3.5, 3, 1.4], 5, 0.00)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[1.4,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[3.5, 3, 1.4]]
    # vehicle_next_goal_list = [[3.5, 3, 1.4], [-3.5, 3, 1.4]]

    

    num_vehicles = len(id_list)
    # INIT_XYZS = np.array([vehicle.position for vehicle in case.vehicle_list])
    # # INIT_RPYS = np.zeros([num_vehicles,3])
    # TARGET_VELS = np.zeros([num_vehicles,3])
    # FLOW_VELS = np.zeros([num_vehicles,3])


    #### Initialize the logger #################################
    # log = Logger(logging_freq_hz=30, #int(ARGS.simulation_freq_hz/AGGR_PHY_STEPS),
    #             num_drones=num_vehicles, ) #duration_sec=100 )

    print('Connecting to Tello Swarm...')
    # swarm.connect()
    print('Connected to Tello Swarm...')

    # ac_id_list = [[_[0], _[1]] for _ in ac_list]
    # ac_id_list.append(['888', '888']) # Add a moving target (helmet)
    # ac_id_list.append(['890', '890']) # Add a moving target (soft ball)
    # target = [Target('888')]
    # ball = [Target('890')]
    # all_vehicles = swarm.tellos+target_vehicle

    
    id_dict = dict([('66','66'),('69','69')]) # rigidbody_ID, aircraft_ID
    vehicles = dict([(ac_id, Vehicle(ac_id)) for ac_id in id_dict.keys()])
    # print(id_dict.keys(), vehicles['0'].get_ac_id())
    voliere = VolierePosition(id_dict, vehicles, freq=200, vel_samples=6)


    # voliere = VolierePosition(ac_id_list, swarm.tellos+target+ball, freq=40)
    voliere.run()
    sleep(4)

    # building_hulls=voliere.get_markerset_pos()
    # log.set_building_hulls(building_hulls)

    # Generating an example Source for population
    # population = [Source(ID=0, source_strength=0.3, position=np.array([4., 4., 0.4]))]
    # population = None

    # Arena = ArenaMap(building_hulls=building_hulls)
    # Arena.Inflate(radius = 0.17)
    # Arena.Panelize(size=0.01)
    # Arena.Calculate_Coef_Matrix()
    # Arena.Visualize2D()
    # Arena.Wind(0,0,info = 'unknown') # Not used for the moment !

    # vinfmag_list = [0.05, 0. , -0.05]
    # dt  = 0.02
    # hor = 3.0
    
    # vehicle_list = case.vehicle_list
    # Arena = case.arena
    # log.set_buildings(Arena.buildings)

    # for i, vehicle in enumerate(vehicle_list):
    #     vehicle.arena = Arena
    #     vehicle.vehicle_list = vehicle_list

    print("Starting Natnet3.x interface at %s" % ("1234567"))

    # Simulation starts
    sim_start_time = time.time()
    try:
        # swarm.takeoff()

        starttime= time.time()
        while time.time()-sim_start_time < 1800:
            if time.time()-starttime > 0.025:
                print("---")
                print(voliere.vehicles['66'].position)

        # swarm.tellos[1].move_up(int(70))
        # starttime= time.time()
        # while time.time()-starttime < 9:
        #     for i,id in enumerate(id_list):
        #             # pos_desired = case.vehicles.np.array([0.5, 3.5, 1.4])
        #             # step =0.002

        #             # if heading < np.pi-step:
        #             #     heading +=step
        #             # else:
        #             #     heading =-heading

        #             # print(f'Heading {heading}')
        #             # j+=1
        #             swarm.tellos[i].fly_to_enu(INIT_XYZS[i], heading=0)

        # print('Finished moving !!!!!') #Finished 
        # # Main loop :
        # trace_count = 0
        # set_vel_time = time.time()
        # flight_finished=False
        # starttime= time.time()
        # while time.time()-sim_start_time < 1800:
        #     if time.time()-starttime > 0.025:
        #         # print(f'Freq : {1/(time.time()-starttime):.3f}')
        #         starttime= time.time()
        #         # Check if vehicles reached their final position
        #         distance_to_destination = [vehicle.distance_to_destination for vehicle in vehicle_list]
        #         flight_finished = True if np.all(distance_to_destination) < 0.50 else False
        #         # print(distance_to_destination)
        #         # print(f' {vehicle_list[0].distance_to_destination:.3f}  -  {vehicle_list[1].distance_to_destination:.3f}  -  {vehicle_list[2].distance_to_destination:.3f}')
        #         if flight_finished: break

        #         # Get Source position to avoid
        #         source_position = ball[0].position
        #         # Get Sink position to follow if needed
        #         sink_position = target[0].position
        #         # Update it on the population list
        #         population[0].position = source_position
        #         # print(f'Source Pos : {source_position}')

        #         # For dynamic sink with Helmet :
        #         # for vehicle_nr, vehicle in enumerate(vehicle_list):
        #         #     vehicle.Set_Next_Goal(sink_position+np.array([0.,0.,-0.2]), dynamic_sigma=True)


        #         for vehicle_nr, vehicle in enumerate(vehicle_list):
        #             # print('Heyyo :', target_position, type(target_position))
        #             # vehicle.Set_Next_Goal(vehicle_next_goal_list[], dynamic_sigma=True)
                    
        #             # if vehicle.state :
        #             if vehicle.distance_to_destination<0.50:# and vehicle_nr==1:
        #                 print('Changing goal set point')
        #                 vehicle.Set_Next_Goal(vehicles_next_goal_list[vehicle_nr][vehicle._sink_index])
        #                 vehicle._sink_index += 1
        #                 # print(f'Vehicle : {vehicle_nr} -- sink ind:{vehicle._sink_index}')
        #                 # The below is to have a finite waypoint
        #                 # vehicle._sink_index = np.clip(vehicle._sink_index, 0,len(vehicles_next_goal_list[vehicle_nr])-1)
        #                 # This one is to have an infinite loop of waypoints
        #                 vehicle._sink_index = vehicle._sink_index%len(vehicles_next_goal_list[vehicle_nr])
        #                 # print(f'Vehicle : {vehicle_nr} -- clipped :{vehicle._sink_index}')
        #                 # goal_index = goal_index%len(vehicle_next_goal_list)
                
        #         # COMMUNICATION 
        #         # for index,vehicle in enumerate(vehicle_list):
        #         #     # Update only self position
                    
        #         #     vehicle.vehicle_list[index].position = vehicle.position
        #         #     if index in [1,2,3]: # FIXME : This has to be replaced with a flag in vehicle!
        #         #         for list_index in range(len(vehicle.vehicle_list)):
        #         #             vehicle.vehicle_list[list_index].position = vehicle_list[list_index].position # calling case.Vehicle is not nice here... 1 unneccessary element update


        #         # flow_vels = Flow_Velocity_Calculation(vehicle_list,Arena)
        #         for i, vehicle in enumerate(vehicle_list):
        #             vehicle.Set_Position(swarm.tellos[i].get_position_enu())
        #             vehicle.Set_Velocity(swarm.tellos[i].get_velocity_enu())
        #             # print(vehicle.position)
        #             # print(f' {i} - Vel : {vehicle.velocity[0]:.3f}  {vehicle.velocity[1]:.3f}  {vehicle.velocity[2]:.3f}')
        #             # if i == 0 :
        #             # vehicle.Go_to_Goal(Vinfmag=1.0) # FIXME this is only for waypoint guidance

        #         use_panel_flow = 1
        #         if use_panel_flow :
        #             flow_vels= Flow_Velocity_Calculation(vehicle_list, Arena, external_sources=population)
                    
        #             # for i,id in enumerate(id_list):
        #             for i, vehicle in enumerate(vehicle_list):
        #                 V_des = flow_vels[i] #vehicle.run_flow_calc_alone()
        #                 mag = np.linalg.norm(V_des)
        #                 V_des_unit = V_des/mag
        #                 # V_des_unit[2] = 0.
        #                 mag = np.clip(mag, 0., 0.6)
        #                 vel_enu = V_des_unit*mag
        #                 vel_enu[2] = V_des[2]
        #                 print('Vel enu : ',vel_enu)
        #                 # swarm.tellos[i].update(swarm.tellos, )

        #                 # vel_enu = flow_vels[i]*limited_norm #- swarm.tellos[i].velocity_enu
        #                 # print(f' {i} - Flow Velocity : {flow_vels[i]}')
        #                 # print(f' {i} - Flow Velocity Error : {vel_enu_err}')
        #                 # if i==0:
        #                     # print(f' Velicle {i} -- Flow Vels : {vel_enu}')
        #                 heading = 0.
        #                 # Look towards where you go
        #                 # heading = np.arctan2(vel_enu[1],vel_enu[0])
                        
        #                 # vehicle.Set_Desired_Velocity(vel_enu, correction_method='None')

        #                 # and update the Nest Vinf:
        #                 # vinfmag = 0.5
        #                 # vehicle.propagate_simple_path(vinfmag, V_des=vel_enu)

        #                 # swarm.tellos[i].send_velocity_enu(vehicle.velocity_desired, heading)
        #                 swarm.tellos[i].send_velocity_enu(vel_enu, heading)
        #                 TARGET_VELS[i]=vehicle.velocity_desired

        #                 # swarm.tellos[i].send_velocity_enu(vehicle.velocity_desired, heading)
        #                 # TARGET_VELS[i]=vehicle.velocity_desired

        #         else:
        #             # Directly fly to the point
        #             for i, vehicle in enumerate(vehicle_list):
        #                 swarm.tellos[i].fly_to_enu(vehicle.goal, 0.)

                
        #         for i, vehicle in enumerate(vehicle_list):
        #             if visualize:
        #                 p.resetBasePositionAndOrientation(quadrotors[i],
        #                                             swarm.tellos[i].get_position_enu(),
        #                                             swarm.tellos[i].get_quaternion(),
        #                                             physicsClientId=physicsClient)
        #                 vehicle_colors=[[1, 0, 0], [0, 1, 0], [0, 0, 1],[1, 1, 0], [0, 1, 1], [0.5, 0.5, 1] ]
        #                 if trace_count > 10:
        #                     p.addUserDebugLine(lineFromXYZ=INIT_XYZS[i],
        #                            lineToXYZ=swarm.tellos[i].get_position_enu(),
        #                            lineColorRGB=vehicle_colors[i],#[1, 0, 0],
        #                            lifeTime=1 * 1000,
        #                            physicsClientId=physicsClient)
        #                     INIT_XYZS[i] = swarm.tellos[i].get_position_enu()
        #                     trace_count = 0
        #                 trace_count +=1

        #         # #### Log the simulation ####################################
        #         for i, vehicle in enumerate(id_list):
        #             log.log(drone=i,
        #                        timestamp=time.time()-sim_start_time,
        #                        state= np.hstack([swarm.tellos[i].get_position_enu(), swarm.tellos[i].get_velocity_enu(), swarm.tellos[i].get_quaternion(),  np.zeros(10)]),#obs[str(j)]["state"],
        #                     #    control=np.hstack([TARGET_VELS[i], FLOW_VELS[i], V_sum[i], 0., target_vehicle[0].position]),
        #                        control=np.hstack([TARGET_VELS[i], FLOW_VELS[i], population[0].position, sink_position]),
        #                        sim=False
        #                        # control=np.hstack([TARGET_VEL[j, wp_counters[j], 0:3], np.zeros(9)])
        #                        )

        #### Save the simulation results ###########################
        # log.save(flight_type='Tello')
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        # log.save(flight_type='Tello')
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        if visualize:
            p.disconnect(physicsClientId=physicsClient)
        sleep(1)

    except OSError:
        print("Natnet connection error")
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        exit(-1)

if __name__=="__main__":
    main()
