from time import sleep
import time
from djitellopy import TelloSwarm
import voliere
from voliere import VolierePosition
from voliere import Vehicle
from voliere import Vehicle as Target
import pdb
import numpy as np

def main():
    # PyBullet Visualization
    visualize = False#True

    #---------- OpTr- ACID - -----IP------
    id = '244'
    freq = 20
    ac_list = [[id, id, '192.168.1.'+id],] 
    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i,id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)

    print('Connecting to Tello Swarm...')
    swarm.connect()
    print('Connected to Tello Swarm...')

    
    id_dict = dict([(id,id)]) # rigidbody_ID, aircraft_ID
    vehicles = dict([(ac_id, swarm.tellos[i]) for i,ac_id in enumerate(id_dict.keys())])
    # print(id_dict.keys(), vehicles['0'].get_ac_id())
    voliere = VolierePosition(id_dict, vehicles, freq=100, vel_samples=6)

     # Initialize lists to store data
    positions = []
    timeList = []
    angular_velocities = []



    # voliere = VolierePosition(ac_id_list, swarm.tellos+target+ball, freq=40)
    voliere.run()

    #countdown loop with printout
    for i in range(3,0,-1):
        print(i)
        time.sleep(1)

    print("Starting Natnet3.x interface at %s" % ("1234567"))

    # Simulation starts
    sim_start_time = time.time()
    print("Current Tello Battery ",swarm.tellos[0].get_battery())
    try:
        #Ground Run
        # swarm.turn_motor_off()
        # print("motor on !")
        print("POSITIONING !")
        swarm.takeoff()
        while time.time() - sim_start_time < 240:
            loop_start_time = time.time()

            # Perform operations at 10 Hz
            print("position: ", swarm.tellos[0].position_enu, " battery: ", swarm.tellos[0].get_battery())
            positions.append(swarm.tellos[0].position_enu)
            for i, vehicle in enumerate(swarm.tellos):
                swarm.tellos[i].fly_to_enu([-2.66, -2.04, 1.])

            # Calculate elapsed time and sleep for the remaining time to maintain 10 Hz frequency
            elapsed_time = time.time() - loop_start_time
            sleep_time = max(0, (1/freq) - elapsed_time)
            time.sleep(sleep_time)

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
    
