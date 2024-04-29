from time import sleep
import time
from djitellopy import TelloSwarm
from voliere import VolierePosition
from voliere import Vehicle as Target
import pdb
import numpy as np

# from path_plan_w_panel import ArenaMap, Vehicle, Flow_Velocity_Calculation_0


from arena import ArenaMap
from panel_flow import Flow_Velocity_Calculation
from building import Building
from vehicle import Vehicle

# For pybullet :
import pybullet as p
from time import sleep
import pybullet_data
import pdb
import numpy as np

from utils import add_buildings

# We are using our own Logger here for convenience
# from gym_pybullet_drones.utils.Logger import Logger
from Logger import Logger

def main():
    # PyBullet Visualization
    visualize = False#True

    #---------- OpTr- ACID - -----IP------
    # ac_list = [['65', '65', '192.168.1.65'],]

    # ac_list =  [['65', '65', '192.168.1.65'],
    #             ['66', '66', '192.168.1.66'],]

    ac_list =  [['65', '65', '192.168.1.65'],
                ['66', '66', '192.168.1.66'],
                ['67', '67', '192.168.1.67'] ]

    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i,id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)


    # arena_version = 65 #102
    # vehicle_name_list =   ['V1']
    # vehicle_source_list = [0.95] # Source_strength
    # vehicle_imaginary_source_list = [1.5] # Imaginary source_strength
    # vehicle_goal_list = [([-3.5, 3, 1.4], 5, 0.00)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[1.4,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[3.5, 3, 1.4]]
    # vehicle_next_goal_list = [[3.5, 3, 1.4], [-3.5, 3, 1.4]]

    # arena_version = 65 #102
    # vehicle_name_list =   ['V1', 'V2']
    # vehicle_source_list = [0.95, 0.95] # Source_strength
    # vehicle_imaginary_source_list = [1.5, 1.5] # Imaginary source_strength
    # vehicle_goal_list = [([-3.5, 3, 1.4], 5, 0.00), ([-3.5, 3, 1.4], 5, 0.00)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[1.4,0,0,0], [1.4,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[3.5, 3, 1.4], [3.5, -3, 1.4]]
    # vehicle_next_goal_list = [[3.5, 3, 1.4], [-3.5, 3, 1.4]]

    arena_version = 65 #102
    vehicle_name_list =   ['V1', 'V2', 'V3']
    vehicle_source_list = [1., 1., 1.] # Source_strength
    vehicle_imaginary_source_list = [1.9, 1.9, 1.9] # Imaginary source_strength
    vehicle_goal_list = [([-3.5, 3, 1.4], 5, 0.00), ([-3.5, 3, 1.4], 5, 0.00), ([-3.5, 3, 1.4], 5, 0.00)]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    vehicle_goto_goal_list =[[1.4,0,0,0], [1.4,0,0,0], [1.4,0,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    vehicle_pos_list = [[3.5, 3, 1.4], [3.5, 3, 1.4], [3.5, 3, 1.4]]
    vehicle_next_goal_list = [[3.5, 3, 1.4], [-3.5, 3, 1.4]]




    # vehicle_next_goal_list = [[3., 2, 1.4], [-3., 2, 1.4], [-3., 1, 1.4], [3., 1, 1.4], [3., 0, 1.4], [-3., 0, 1.4], [-3., -1, 1.4], [3., -1, 1.4], [3., -2, 1.4],[-3., -2, 1.4],[-3., -3, 1.4],[3., -3, 1.4], [3., 2, 1.4], [-3., 2, 1.4], [-3., 1, 1.4], [3., 1, 1.4], [3., 0, 1.4], [-3., 0, 1.4], [-3., -1, 1.4], [3., -1, 1.4],  ]
    # vehicle_next_goal_list = [[3., -3, 1.4], [-3., -3, 1.4], [-3., 2, 1.4], [2., 2, 1.4],[2., -2, 1.4], [-2., -2, 1.4], [-2., 1, 1.4], [1., 1, 1.4], [1., -1, 1.4], [-1., -1, 1.4], [-1., 0, 1.4], [0., 0, 1.4] ]
    goal_index = 0


    # Arena = ArenaMap(version = arena_version)
    # Arena.Inflate(radius = 0.2)
    # Arena.Panelize(size=0.01)
    # Arena.Calculate_Coef_Matrix()
    # # Arena.Visualize2D()
    # Arena.Wind(0,0,info = 'unknown') # Not used for the moment !

    # The below vehicles should be converted to Tellos...
    # vehicle_list = [Vehicle(name,source) for name , source in zip(vehicle_name_list, vehicle_source_list)]
    vehicle_list = [Vehicle(name,source, imag_source) for name , source, imag_source in zip(vehicle_name_list, vehicle_source_list, vehicle_imaginary_source_list)]
    num_vehicles = len(id_list)
    INIT_XYZS = np.array(vehicle_pos_list)
    INIT_RPYS = np.zeros([num_vehicles,3])
    TARGET_VELS = np.zeros([num_vehicles,3])
    FLOW_VELS = np.zeros([num_vehicles,3])

    # Tello class should have these Set_Goal-Goto_Goal-Set_position functions...
    for vehicle,set_goal,goto_goal,pos in zip(vehicle_list,vehicle_goal_list,vehicle_goto_goal_list,vehicle_pos_list):
        vehicle.Set_Goal(set_goal[0],set_goal[1],set_goal[2])
        vehicle.Go_to_Goal(goto_goal[0],goto_goal[1],goto_goal[2],goto_goal[3])
        vehicle.Set_Position(pos)
        # pdb.set_trace()

    # current_vehicle_list = vehicle_list

    #### Initialize the logger #################################
    logger = Logger(logging_freq_hz=30, #int(ARGS.simulation_freq_hz/AGGR_PHY_STEPS),
                    num_drones=num_vehicles, ) #duration_sec=100 )

    print('Connecting to Tello Swarm...')
    swarm.connect()
    print('Connected to Tello Swarm...')

    ac_id_list = [[_[0], _[1]] for _ in ac_list]
    # ac_id_list_extended = 
    ac_id_list.append(['888', '888']) # Add a moving target
    target_vehicle = [Target('888')]
    all_vehicles = swarm.tellos+target_vehicle

    voliere = VolierePosition(ac_id_list, swarm.tellos+target_vehicle, freq=20)
    voliere.run()
    sleep(4)

    Arena = ArenaMap(version = None, building_hulls=voliere.get_markerset_pos())
    # Arena = ArenaMap(version = 101)
    Arena.Inflate(radius = 0.05)
    Arena.Panelize(size=0.01)
    Arena.Calculate_Coef_Matrix()
    # Arena.Visualize2D()
    # Arena.Wind(0,0,info = 'unknown') # Not used for the moment !

    vinfmag_list = [0.05, 0. , -0.05]
    dt  = 0.02
    hor = 3.0
    current_vehicle_list = vehicle_list

    for i, vehicle in enumerate(current_vehicle_list):
        vehicle.arena = Arena
        vehicle.vehicle_list = current_vehicle_list


    if visualize:
        # PyBullet Visualization ==============
        physicsClient = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        # p.setGravity(0, 0, -10)
        planeId = p.loadURDF("plane.urdf")
        textureId = p.loadTexture("checker_grid.jpg")

        vehicleStartPos = [0, 0, 0]
        vehicleStartOrientation = p.getQuaternionFromEuler([0, 0, 0])
        # Generate a list of vehicles for the pyBullet sim vizu.
        quadrotors = [p.loadURDF("tello.urdf", swarm.tellos[i].get_position_enu(), vehicleStartOrientation) for i in range(num_vehicles)]
        p.resetDebugVisualizerCamera( cameraDistance=6.5, cameraYaw=0, cameraPitch=-40, cameraTargetPosition=[0.0, 0.0, 0.0])
        
        ### Add Buildings ################################
        add_buildings(physicsClientId=physicsClient, version=arena_version)


    print("Starting Natnet3.x interface at %s" % ("1234567"))

    # Simulation starts
    sim_start_time = time.time()
    try:
        # Start up the streaming client.
        # This will run perpetually, and operate on a separate thread.
        # voliere.run()
        # sleep(3.)

        swarm.takeoff()
        
        # swarm.move_up(int(40))
        # swarm.tellos[0].move_up(int(60))
        # swarm.tellos[1].move_up(int(80))
        # swarm.tellos[2].move_up(int(100))
        nr_vehicle = len(id_list)
        # fields[0].gvf_parameter = 700./nr_vehicle

        # # Debug loop :
        heading = 0 #-np.pi-0.002
        j=0
        while 0:
            # for i, vehicle in enumerate(vehicle_list):
            #     # vehicle.position = swarm.tellos[i].get_position_enu()
            #     # vehicle.velocity = swarm.tellos[i].get_velocity_enu()
            #     vehicle.Set_Position(swarm.tellos[i].get_position_enu())
            #     vehicle.Set_Velocity(swarm.tellos[i].get_velocity_enu())
                # print(f'Vehicle position East : {vehicle.position[0]:.3f} North : {vehicle.position[1]:.3f}  Up : {vehicle.position[2]:.3f}')

            for i,id in enumerate(id_list):
                pos_desired = np.array([0.5, 3.5, 1.4])
                step =0.002

                if heading < np.pi-step:
                    heading +=step
                else:
                    heading =-heading

                print(f'Heading {heading}')
                j+=1
                swarm.tellos[i].fly_to_enu(pos_desired, heading)
            sleep(0.04)


    


        # Main loop :
        trace_count = 0
        set_vel_time = time.time()
        flight_finished=False
        starttime= time.time()
        while time.time()-sim_start_time < 180:
            if time.time()-starttime > 0.025:
                # print(f'Freq : {1/(time.time()-starttime):.3f}')
                starttime= time.time()
                # Check if vehicles reached their final position
                distance_to_destination = [vehicle.distance_to_destination for vehicle in vehicle_list]
                flight_finished = True if np.all(distance_to_destination) < 0.50 else False
                # print(distance_to_destination)
                # print(f' {vehicle_list[0].distance_to_destination:.3f}  -  {vehicle_list[1].distance_to_destination:.3f}  -  {vehicle_list[2].distance_to_destination:.3f}')
                if flight_finished: break

                # Get Target position to follow
                target_position = target_vehicle[0].position
                # print(f'Target Pos : {target_position}')

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
                    # vehicle.position = swarm.tellos[i].get_position_enu()
                    # vehicle.velocity = swarm.tellos[i].get_velocity_enu()
                    # pos = swarm.tellos[i].get_position_enu()
                    # vehicle.Set_Position(np.array([pos[0], pos[1], 0.5]))
                    # print('Vehicle Position : ',swarm.tellos[i].get_position_enu())
                    vehicle.Set_Position(swarm.tellos[i].get_position_enu())
                    vehicle.Set_Velocity(swarm.tellos[i].get_velocity_enu())
                    # print(f' {i} - Vel : {vehicle.velocity[0]:.3f}  {vehicle.velocity[1]:.3f}  {vehicle.velocity[2]:.3f}')

                use_panel_flow = 1
                if use_panel_flow :
                    flow_vels= Flow_Velocity_Calculation(vehicle_list,Arena)
                    # for i,id in enumerate(id_list):
                    for i, vehicle in enumerate(vehicle_list):
                        # swarm.tellos[i].update(swarm.tellos, )

                        # Varying speed
                        # flow_vels[i][0] = np.clip(flow_vels[i][0]/10., -0.3, 0.3)
                        # flow_vels[i][1] = np.clip(flow_vels[i][1]/10., -0.3, 0.3)
                        # print('Flow Vels : ',flow_vels)
                        FLOW_VELS[i]=flow_vels[i].copy()
                        norm = np.linalg.norm(flow_vels[i])
                        flow_vels[i] = flow_vels[i]/norm
                        # flow_vels[i][2] = 0.0
                        limited_norm = np.clip(norm,0., 1.1)
                        fixed_speed = 1.

                        # # Fixed speed trial
                        # flow_2D_norm = np.linalg.norm([flow_vels[i][0],flow_vels[i][1]])
                        # flow_vels[i][0] = flow_vels[i][0]/flow_2D_norm
                        # flow_vels[i][1] = flow_vels[i][1]/flow_2D_norm
                        # flow_vels[i][2] = 0.0
                        # fixed_speed = 0.3

                        vel_enu = flow_vels[i]*limited_norm #- swarm.tellos[i].velocity_enu
                        # print(f' {i} - Flow Velocity : {flow_vels[i]}')
                        # print(f' {i} - Flow Velocity Error : {vel_enu_err}')

                        heading = 0. # np.pi/2. # 0.

                        # if time.time()-set_vel_time > 1./200.:
                        #     print('Time diff : ',time.time()-set_vel_time)
                        #     vehicle.Set_Desired_Velocity(vel_enu)
                        #     set_vel_time = time.time()
                        
                        vehicle.Set_Desired_Velocity(vel_enu, method='direct')

                        # and update the Nest Vinf:
                        vinfmag =  0.5
                        vehicle.propagate_simple_path(vinfmag)
                        # Previously used like the below :
                        # swarm.tellos[i].send_velocity_enu(vel_enu*fixed_speed, heading)
                        # TARGET_VELS[i]=vel_enu*fixed_speed

                        swarm.tellos[i].send_velocity_enu(vehicle.velocity_desired, heading)
                        TARGET_VELS[i]=vehicle.velocity_desired

                        # swarm.tellos[i].send_velocity_enu(vehicle.velocity_desired, heading)
                        # TARGET_VELS[i]=vehicle.velocity_desired

                else:
                    # Directly fly to the point
                    for i, vehicle in enumerate(vehicle_list):
                        swarm.tellos[i].fly_to_enu(vehicle.goal, 0.)

                
                for i, vehicle in enumerate(vehicle_list):
                    if visualize:
                        p.resetBasePositionAndOrientation(quadrotors[i],
                                                    swarm.tellos[i].get_position_enu(),
                                                    swarm.tellos[i].get_quaternion(),
                                                    physicsClientId=physicsClient)
                        vehicle_colors=[[1, 0, 0], [0, 1, 0], [0, 0, 1],[1, 1, 0], [0, 1, 1], [0.5, 0.5, 1] ]
                        if trace_count > 10:
                            p.addUserDebugLine(lineFromXYZ=INIT_XYZS[i],
                                   lineToXYZ=swarm.tellos[i].get_position_enu(),
                                   lineColorRGB=vehicle_colors[i],#[1, 0, 0],
                                   lifeTime=1 * 1000,
                                   physicsClientId=physicsClient)
                            INIT_XYZS[i] = swarm.tellos[i].get_position_enu()
                            trace_count = 0
                        trace_count +=1

                # #### Log the simulation ####################################
                for i, vehicle in enumerate(id_list):
                    logger.log(drone=i,
                               timestamp=time.time()-sim_start_time,
                               state= np.hstack([swarm.tellos[i].get_position_enu(), swarm.tellos[i].get_velocity_enu(), swarm.tellos[i].get_quaternion(),  np.zeros(10)]),#obs[str(j)]["state"],
                            #    control=np.hstack([TARGET_VELS[i], FLOW_VELS[i], V_sum[i], 0., target_vehicle[0].position]),
                               control=np.hstack([TARGET_VELS[i], FLOW_VELS[i], np.zeros(2), 0., target_vehicle[0].position]),
                               sim=False
                               # control=np.hstack([TARGET_VEL[j, wp_counters[j], 0:3], np.zeros(9)])
                               )

        #### Save the simulation results ###########################
        logger.save(flight_type='fast_follow')
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        logger.save(flight_type='fast_follow')
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
