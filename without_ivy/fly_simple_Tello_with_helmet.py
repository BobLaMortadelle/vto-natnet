from time import sleep
import time
from djitellopy import TelloSwarm
import voliere
from voliere import VolierePosition
from voliere import Vehicle
from voliere import Vehicle as Target
import pdb
import numpy as np
import matplotlib.pyplot as plt

# For pybullet :
# import pybullet as p
# import pybullet_data

# We are using our own Logger here for convenience
# from logger import Logger

def main():
    # PyBullet Visualization
    visualize = False#True

    #---------- OpTr- ACID - -----IP------
    id = '244'
    freq = 20
    ac_list = [[id, id, '192.168.1.244'],]

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
    #ac_list.append(['888', '888']) # Add a moving target (helmet)
    # ac_id_list.append(['890', '890']) # Add a moving target (soft ball)
    # target = [Target('888')]
    # ball = [Target('890')]
    # all_vehicles = swarm.tellos+target_vehicle

    
    id_dict = dict([('244','244'), ('888','888')]) # rigidbody_ID, aircraft_ID
    #ac_id = Literal['888']
    # vehicles = dict([(ac_id, Vehicle(ac_id)) for ac_id in id_dict.keys()])
    vehicles = dict([('244', swarm.tellos[0]), ('888', Vehicle(['888']))])
    # print(id_dict.keys(), vehicles['0'].get_ac_id())
    voliere = VolierePosition(id_dict, vehicles, freq=100, vel_samples=6)




     # Initialize lists to store data
    positions = []
    timeList = []
    angular_velocities = []

    threshold = 0.15
    waypoint_test = [-2.66, -2.04, 1.]
    # voliere = VolierePosition(ac_id_list, swarm.tellos+target+ball, freq=40)
    voliere.run()
    sleep(4)

    print("Starting Natnet3.x interface at %s" % ("1234567"))

    # Simulation starts
    sim_start_time = time.time()
    print("Current Tello Battery ",swarm.tellos[0].get_battery())
    try:
        swarm.takeoff()

        starttime= time.time()
        actualize_height = time.time()
        z = voliere.vehicles['888'].position[2]
        while time.time()-sim_start_time < 240:
            if time.time()-starttime > 1/freq :
                #print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery())
                positions.append(swarm.tellos[0].position_enu)

                # # Directly fly to the point
                #for i, vehicle in enumerate(swarm.tellos):
                if time.time() - actualize_height > 3 :
                    z = voliere.vehicles['888'].position[2] - 0.1
                    if z < 0.50:
                        z = 0.50
                    actualize_height = time.time()
                swarm.tellos[0].fly_to_enu([-2.66, -2.04, z])
                #print("position of helmet", voliere.vehicles['888'].position[2])
                starttime = time.time()


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
        plt.figure(figsize=(12, 8))
        plt.plot(positions)
        plt.title('Position')
        plt.show()
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
    
