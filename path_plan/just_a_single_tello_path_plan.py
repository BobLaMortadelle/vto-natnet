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
    visualize = False#True

    #---------- OpTr- ACID - -----IP------
    ac_list = [['69', '69', '192.168.1.69'],]

    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i,id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)


    # declaration of the path to follow
    vehicle_name =   ['69']
    vehicle_source = [0.]
    vehicle_goal = [([1, -3, 0.5], 5, 0.0001),  ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    vehicle_goto_goal =[[0.5,-np.pi/4,0,0], ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    vehicle_pos= [[0.1, 2.1, 0.5],]

    vehicle = Vehicle(vehicle_name,vehicle_source)
    num_vehicles = 1
    INIT_XYZS = np.array(vehicle_pos)
    INIT_RPYS = np.zeros([num_vehicles,3])
    TARGET_VELS = np.zeros([num_vehicles,3])
    FLOW_VELS = np.zeros([num_vehicles,3])

    # Set object vehicle with values of the path to follow
    vehicle.Set_Goal(vehicle_goal[0],vehicle_goal[1],vehicle_goal[2])
    vehicle.Go_to_Goal(vehicle_goto_goal[0],vehicle_goto_goal[1],vehicle_goto_goal[2],vehicle_goto_goal[3])
    vehicle.Set_Position(vehicle_pos)

    #### Initialize the logger #################################
    logger = Logger(logging_freq_hz=30, #int(ARGS.simulation_freq_hz/AGGR_PHY_STEPS),
                    num_drones=num_vehicles, ) #duration_sec=100 )
    
    print('Connecting to Tello Swarm...')
    swarm.connect()
    print('Connected to Tello Swarm...')

    ac_id_list = [[_[0], _[1]] for _ in ac_list]
    voliere = VolierePosition(ac_id_list, swarm.tellos, freq=40)

    # voliere = VolierePosition(ac_id_list, swarm.tellos+target+ball, freq=40)
    voliere.run()
    sleep(4)

    sim_start_time = time.time()
    print("Current Tello Battery ",swarm.tellos[0].get_battery())
    try:
        #swarm.takeoff()
        starttime= time.time()
        while time.time()-sim_start_time < 65:
            # print(time.time()-sim_start_time)
            if time.time()-starttime > 0.025:
                # pass
                # print(voliere.vehicles['66'].position)
                print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery())

                # for i, vehicle in enumerate(voliere.vehicles):
                    # swarm.tellos[i].set_position_enu(voliere.vehicles['66'].position)
                    # swarm.tellos[i].set_heading(voliere.vehicles['66'].heading)
                #     vehicle.Set_Position(swarm.tellos[i].get_position_enu())
                #     vehicle.Set_Velocity(swarm.tellos[i].get_velocity_enu())
                # print(swarm.tellos[0].position_enu)
                # # Directly fly to the point
                # for i, vehicle in enumerate(swarm.tellos):
                #     swarm.tellos[i].fly_to_enu([0., 0., 2.])
                vehicle.position = swarm.tellos[0].get_position_enu()
                vehicle.velocity = swarm.tellos[0].get_velocity_enu()
            


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
