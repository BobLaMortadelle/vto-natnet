from time import sleep
import time
from djitellopy import TelloSwarm
from voliere import VolierePosition
import pdb
import numpy as np

# from path_plan_w_panel import ArenaMap, Vehicle, Flow_Velocity_Calculation_0

from path_plan_w_panel import ArenaMap, Flow_Velocity_Calculation #Vehicle
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
    visualize = True

    #---------- OpTr- ACID - -----IP------
    ac_list = [['69', '69', '192.168.1.69'],]
    # ac_list = [['60', '60', '192.168.1.60'],]
    # ac_list =  [['61', '61', '192.168.1.61'],
    #             ['62', '62', '192.168.1.62'],
    #             ['63', '63', '192.168.1.63'] ]

    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i,id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)



    arena_version = 2
    Arena = ArenaMap(version = arena_version)
    Arena.Inflate(radius = 0.2)
    Arena.Panelize(size=0.01)
    Arena.Calculate_Coef_Matrix()
    # Arena.Visualize2D()
    Arena.Wind(0,0,info = 'unknown') # Not used for the moment !


    # vehicle_name_list = ['V1']
    # vehicle_source_list = [0.]
    # vehicle_goal_list = [([3, 2, 0.5], 5, 0.0) ]
    # vehicle_goto_goal_list =[[0.5,0,0,0], ] #altitude,AoA,t_start,Vinf
    # vehicle_pos_list = [[-2, 2, 0.5],   ]


    # vehicle_name_list = ['V1', 'V2', 'V3']
    # vehicle_source_list = [0., 0., 0.]
    # vehicle_goal_list = [([3, 2, 0.5], 5, 0.0), ([3, 3, 0.7], 5, 0.0), ([-3, 0, 0.9], 5, 0.0) ]
    # vehicle_goto_goal_list =[[0.5,0,0,0],[0.7,0,0,0], [0.9,0,0,0] ]
    # vehicle_pos_list = [[-2.5, 2, 0.5],[-3, -3, 0.7], [2, 0.1, 0.9]]

    # NEW CASES 
    # Case 1 : 3 Vehicles with and without source. No collision in both
    vehicle_name_list =   ['69']
    # vehicle_source_list = [0., 0., 0.]
    # vehicle_source_list = [0.3, 0.3, 0.3]
    # vehicle_goal_list = [([1, -3, 0.5], 5, 0.0001), ([-2.5, -2.5, 0.5], 5, 0.0002), ([-1.5, 2, 0.2], 5, 0.0) ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[0.5,-np.pi/4,0,0],[0.5,np.pi,0,0], [0.5,np.pi/2,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[0.1, 2.1, 0.5],[2., 1.5, 0.5], [0, -3, 0.5]]

    # # Single vehicle version of the above case :
    # vehicle_name_list =   ['V1']
    vehicle_source_list = [0.]
    vehicle_goal_list = [([1, -3, 0.5], 5, 0.0001),  ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    vehicle_goto_goal_list =[[0.5,-np.pi/4,0,0], ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    vehicle_pos_list = [[0.1, 2.1, 0.5],]

    # vehicle_name_list =   ['V1', 'V2', ]
    # # vehicle_source_list = [0., 0., 0.]
    # vehicle_source_list = [0.45, 0.,]
    # vehicle_goal_list = [([1, -3, 0.5], 5, 0.0001), ([-2.5, -2.5, 0.5], 5, 0.0002), ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[0.5,-np.pi/4,0,0],[0.5,np.pi,0,0],] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[0.1, 2.1, 0.5],[2., 1.5, 0.5],]

    # vehicle_name_list =   ['V1', 'V3']
    # # vehicle_source_list = [0., 0., 0.]
    # vehicle_source_list = [0.45, 0.3]
    # vehicle_goal_list = [([1, -3, 0.5], 5, 0.0001),  ([-1.5, 2, 0.2], 5, 0.0) ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[0.5,-np.pi/4,0,0], [0.5,np.pi/2,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[0.1, 2.1, 0.5], [0, -3, 0.5]]

    # The below vehicles should be converted to Tellos...
    vehicle_list = [Vehicle(name,source) for name , source in zip(vehicle_name_list, vehicle_source_list)]
    num_vehicles = len(vehicle_list)
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
    voliere = VolierePosition(ac_id_list, swarm.tellos, freq=40)


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
        voliere.run()
        #swarm.takeoff()            #switch to comment before trying programm for the first time
        nr_vehicle = len(id_list)
        # fields[0].gvf_parameter = 700./nr_vehicle

        # # Debug loop :
        # while 1:
        #     for i, vehicle in enumerate(vehicle_list):
        #         vehicle.position = swarm.tellos[i].get_position_enu()
        #         vehicle.velocity = swarm.tellos[i].get_velocity_enu()
        #         # print(f'Vehicle position East : {vehicle.position[0]:.3f} North : {vehicle.position[1]:.3f}  Up : {vehicle.position[2]:.3f}')

        #     for i,id in enumerate(id_list):
        #     # for i, vehicle in enumerate(vehicle_list):
        #         pos_desired = np.array([0., 0., 0.5])
        #         # pos_error = pos_desired - vehicle.position
        #         # vel = pos_error*1 # just a proportional gain to generate reference velocity
        #         # print(f'Vehicle Velocity East : {vel[0]:.3f} North : {vel[1]:.3f}  Up : {vel[2]:.3f}')
        #         # heading = 0.
        #         # vel = np.array([0.3, 0.0, 0.])
        #         # swarm.tellos[i].send_velocity_enu(vel, heading)
        #         swarm.tellos[i].fly_to_enu(pos_desired)
        #     sleep(0.2)



        # Main loop :
        trace_count = 0
        while time.time()-sim_start_time < 65:
            starttime= time.time()
            # flow_vels = Flow_Velocity_Calculation(vehicle_list,Arena)
            for i, vehicle in enumerate(vehicle_list):
                vehicle.position = swarm.tellos[i].get_position_enu()
                vehicle.velocity = swarm.tellos[i].get_velocity_enu()
                # print(f' {i} - Vel : {vehicle.velocity[0]:.3f}  {vehicle.velocity[1]:.3f}  {vehicle.velocity[2]:.3f}')

                # This has to be fixed correctly
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
                # print(f'Vehicle Position : {vehicle.position}')

            flow_vels = Flow_Velocity_Calculation(vehicle_list,Arena)
            # for i,id in enumerate(id_list):
            for i, vehicle in enumerate(vehicle_list):
                # swarm.tellos[i].update(swarm.tellos, )

                # Varying speed
                # flow_vels[i][0] = np.clip(flow_vels[i][0]/10., -0.3, 0.3)
                # flow_vels[i][1] = np.clip(flow_vels[i][1]/10., -0.3, 0.3)
                FLOW_VELS[i]=flow_vels[i]
                norm = np.linalg.norm(flow_vels[i])
                flow_vels[i] = flow_vels[i]/norm
                flow_vels[i][2] = 0.0
                limited_norm = np.clip(norm,0., 0.4)
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

                heading = 0.
                swarm.tellos[i].send_velocity_enu(vel_enu*fixed_speed, heading)
                TARGET_VELS[i]=vel_enu*fixed_speed

            

            # #### Log the simulation ####################################
            for i, vehicle in enumerate(vehicle_list):
                logger.log(drone=i,
                           timestamp=time.time()-sim_start_time,
                           state= np.hstack([vehicle.position, vehicle.velocity, np.zeros(14)]),#obs[str(j)]["state"],
                           control=np.hstack([TARGET_VELS[i], FLOW_VELS[i], np.zeros(6)]),
                           sim=False
                           # control=np.hstack([TARGET_VEL[j, wp_counters[j], 0:3], np.zeros(9)])
                           )
            # print(f'Step time = {time.time()-starttime}')
            # sleep(0.01)

        # while 0:
        #     for i,id in enumerate(id_list):
        #         pos = swarm.tellos[i].get_position_enu()
        #         vel_enu = fields[i].get_vector_field_circle(pos)
        #         heading = 0.
        #         swarm.tellos[i].send_velocity_enu(vel_enu, heading)
        #         sleep(0.09)

        # while 0: # This was working !
        #     for i,id in enumerate(id_list):
                # swarm.tellos[i].update(swarm.tellos, attractors, obstacles, wall_points, heights)
        #         vel_enu_err = swarm.tellos[i].velocity_setpoint - swarm.tellos[i].velocity_enu
        #         # pos = swarm.tellos[i].get_position_enu()
        #         # vel_enu = fields[i].get_vector_field_circle(pos)
        #         heading = 0.
        #         swarm.tellos[i].send_velocity_enu(vel_enu_err, heading)
        #         sleep(0.01)

        #### Save the simulation results ###########################
        logger.save(flight_type='voliere')

        swarm.land()
        voliere.stop()
        swarm.end()

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        logger.save(flight_type='voliere')
        swarm.land()
        voliere.stop()
        swarm.end()
        if visualize:
            p.disconnect(physicsClientId=physicsClient)
        sleep(1)

    except OSError:
        print("Natnet connection error")
        swarm.land()
        voliere.stop()
        swarm.end()
        exit(-1)

if __name__=="__main__":
    main()
