"""Script demonstrating the joint use of velocity input.

The simulation is run by a `VelocityAviary` environment.

Example
-------
In a terminal, run as:

    $ python velocity.py

Notes
-----
The drones use interal PID control to track a target velocity.

"""
import os
import time
import argparse
from datetime import datetime
import pdb
import math
import random
import numpy as np
import pybullet as p
import matplotlib.pyplot as plt

from gym_pybullet_drones.envs.BaseAviary import DroneModel, Physics
from gym_pybullet_drones.envs.CtrlAviary import CtrlAviary
from gym_pybullet_drones.envs.VisionAviary import VisionAviary
from gym_pybullet_drones.control.DSLPIDControl import DSLPIDControl
from gym_pybullet_drones.control.SimplePIDControl import SimplePIDControl

from gym_pybullet_drones.utils.utils import sync, str2bool

from gym_pybullet_drones.envs.VelocityAviary import VelocityAviary

# We are using our own Logger here for convenience
# from gym_pybullet_drones.utils.Logger import Logger
from Logger import Logger

# from boids import Boid, magnitude

from path_plan_w_panel import ArenaMap, Vehicle, Flow_Velocity_Calculation

from utils import add_buildings

######=====================================================
class Controller:
    def __init__(self,L=1e-1,beta=1e-2,k1=1e-3,k2=1e-3,k3=1e-3,ktheta=0.5,s=0.5):
        self.L    = L
        self.beta = beta
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.ktheta = ktheta
        self.s = s


class ParametricTrajectory:
    def __init__(self, XYZ_off=np.array([0.,0.,2.]), XYZ_center=np.array([1.1, 1.1, -0.2]),
                 XYZ_delta=np.array([0., np.pi/2, 0.]), XYZ_w=np.array([1,1,1]), alpha=np.pi/4, controller=Controller()):
        self.XYZ_off = XYZ_off
        self.XYZ_center = XYZ_center
        self.XYZ_delta = XYZ_delta
        self.XYZ_w = XYZ_w
        self.alpha = alpha
        self.ctr = controller

    def get_vector_field(self,x,y,z,w):
        cx,cy,cz = self.XYZ_center
        wx,wy,wz = self.XYZ_w
        deltax,deltay,deltaz = self.XYZ_delta
        xo,yo,zo = self.XYZ_off
        alpha = self.alpha

        wb = w*self.ctr.beta
        L = self.ctr.L
        beta = self.ctr.beta
        k1 = self.ctr.k1
        k2 = self.ctr.k2
        k3 = self.ctr.k3
        s = self.ctr.s

        #f
        nrf1 = cx*np.cos(wx*wb + deltax)
        nrf2 = cy*np.cos(wy*wb + deltay)
        f3 = cz*np.cos(wz*wb + deltaz) + zo

        nrf1d = -wx*cx*np.sin(wx*wb + deltax)
        nrf2d = -wy*cy*np.sin(wy*wb + deltay)
        f3d = -wz*cz*np.sin(wz*wb + deltaz)

        nrf1dd = -wx*wx*cx*np.cos(wx*wb + deltax)
        nrf2dd = -wy*wy*cy*np.cos(wy*wb + deltay)
        f3dd = -wz*wz*cz*np.cos(wz*wb + deltaz)

        f1 = np.cos(alpha)*nrf1 - np.sin(alpha)*nrf2 + xo
        f2 = np.sin(alpha)*nrf1 + np.cos(alpha)*nrf2 + yo

        f1d = np.cos(alpha)*nrf1d - np.sin(alpha)*nrf2d
        f2d = np.sin(alpha)*nrf1d + np.cos(alpha)*nrf2d

        f1dd = np.cos(alpha)*nrf1dd - np.sin(alpha)*nrf2dd
        f2dd = np.sin(alpha)*nrf1dd + np.cos(alpha)*nrf2dd

        #phi
        phi1 = L*(x - f1)
        phi2 = L*(y - f2)
        phi3 = L*(z - f3)
        # print(f'Phi 1: {phi1:.4f}, Phi 2:{phi2:.4f}, Phi 3:{phi3:.4f}')

        #Chi, J
        Chi = L*np.array([[-f1d*L*L*beta -k1*phi1],
                          [-f2d*L*L*beta -k2*phi2],
                          [-f3d*L*L*beta -k3*phi3],
                          [-L*L + beta*(k1*phi1*f1d + k2*phi2*f2d + k3*phi3*f3d)]])

        # j44 = beta*beta*(k1*(phi1*f1dd-L*f1d*f1d) + k2*(phi2*f2dd-L*f2d*f2d) + k3*(phi3*f3dd-L*f3d*f3d))
        # J = L*np.array([[-k1*L,        0,      0, -(beta*L)*(beta*L*f1dd-k1*f1d)],
                       # [     0,    -k2*L,      0, -(beta*L)*(beta*L*f2dd-k2*f2d)],
                       # [     0,      0,    -k3*L, -(beta*L)*(beta*L*f3dd-k3*f3d)],
                       # [beta*L*k1*f1d, beta*L*k2*f2d, beta*L*k3*f3d,         j44]])

        #G, Fp, Gp
        # G = np.array([[1,0,0,0],
                      # [0,1,0,0],
                      # [0,0,0,0],
                      # [0,0,0,0]])

        # Fp = np.array([[0, -1, 0, 0],
                       # [1,  0, 0, 0]])

        # Gp = np.array([[0, -1, 0, 0],
                       # [1,  0, 0, 0],
                       # [0,  0, 0, 0],
                       # [0,  0, 0, 0]])

    #     h = np.array([[np.cos(theta)],[np.sin(theta)]])
    #     ht = h.transpose()

        # Chit = Chi.transpose()
        # Chinorm = np.sqrt(Chi.transpose().dot(Chi))[0][0]
        # Chih = Chi / Chinorm

    #     u_theta = (-(1/(Chit.dot(G).dot(Chi))*Chit.dot(Gp).dot(np.eye(4) - Chih.dot(Chih.transpose())).dot(J).dot(X_dot)) - ktheta*ht.dot(Fp).dot(Chi) / np.sqrt(Chit.dot(G).dot(Chi)))[0][0]

        u_x = Chi[0][0]*s / np.sqrt(Chi[0][0]*Chi[0][0] + Chi[1][0]*Chi[1][0])
        u_y = Chi[1][0]*s / np.sqrt(Chi[0][0]*Chi[0][0] + Chi[1][0]*Chi[1][0])
        u_z = Chi[2][0]*s / np.sqrt(Chi[0][0]*Chi[0][0] + Chi[1][0]*Chi[1][0])
        u_w = Chi[3][0]*s / np.sqrt(Chi[0][0]*Chi[0][0] + Chi[1][0]*Chi[1][0])
        
        return np.array([u_x, u_y, u_z]), np.array([u_w])
######=====================================================

class Field():
    def __init__(self, ac_id, controller=None, trajectory=None):
        self.ac_id = ac_id
        self.gvf_parameter = 0.0
        self.ctr = controller if controller != None else Controller(L=1e-1,beta=1e-2,k1=1e-3,k2=1e-3,k3=1e-3,ktheta=0.5,s=1.0)
        self.traj = trajectory if trajectory != None else ParametricTrajectory(XYZ_off=np.array([0.,0.,1.5]),
                                                XYZ_center=np.array([1.5, 1.5, -0.6]),
                                                XYZ_delta=np.array([0., np.pi/2, 0.]),
                                                XYZ_w=np.array([1,1,1]),
                                                alpha=0.,
                                                controller=self.ctr)
    def get_vector_field_circle(self,pos):
        V_des_increment,uw = self.traj.get_vector_field(pos[0], pos[1], pos[2], self.gvf_parameter)
            # import pdb
            # pdb.set_trace()
            # print(f'Shape of V_des : {V_des_increment.shape}')
            # print(f'dt : {0.1}, parameter : {self.gvf_parameter} ')
            # V_des += V_des_increment 
        self.gvf_parameter += -uw[0]*1/48 #dt
            # self.send_acceleration(V_des, A_3D=True)
        return V_des_increment

######=====================================================


class Attractor:

    def __init__(self, position=np.zeros(3), magnitude=15.0):
        self.position = position
        self.magnitude = magnitude



def main_path_plan():
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Velocity control example using VelocityAviary')
    parser.add_argument('--drone',              default=['tello'],     type=str,    help='Drone model (default: CF2X)', metavar='', choices=DroneModel)
    parser.add_argument('--gui',                default=False,        type=str2bool,      help='Whether to use PyBullet GUI (default: True)', metavar='')
    parser.add_argument('--record_video',       default=False,       type=str2bool,      help='Whether to record a video (default: False)', metavar='')
    parser.add_argument('--plot',               default=True,        type=str2bool,      help='Whether to plot the simulation results (default: True)', metavar='')
    parser.add_argument('--user_debug_gui',     default=False,       type=str2bool,      help='Whether to add debug lines and parameters to the GUI (default: False)', metavar='')
    parser.add_argument('--aggregate',          default=True,        type=str2bool,      help='Whether to aggregate physics steps (default: False)', metavar='')
    parser.add_argument('--obstacles',          default=False,       type=str2bool,      help='Whether to add obstacles to the environment (default: True)', metavar='')
    parser.add_argument('--simulation_freq_hz', default=240,         type=int,           help='Simulation frequency in Hz (default: 240)', metavar='')
    parser.add_argument('--control_freq_hz',    default=48,          type=int,           help='Control frequency in Hz (default: 48)', metavar='')
    parser.add_argument('--flow_calc_freq_hz',  default=24,          type=int,           help='Vector field calculation frequency in Hz (default: 5)', metavar='')
    parser.add_argument('--duration_sec',       default=50,         type=int,           help='Duration of the simulation in seconds (default: 5)', metavar='')
    # parser.add_argument('--duration_sec',       default=90,         type=int,           help='Duration of the simulation in seconds (default: 5)', metavar='')
    ARGS = parser.parse_args()

    AGGR_PHY_STEPS = int(ARGS.simulation_freq_hz/ARGS.control_freq_hz) if ARGS.aggregate else 1
    PHY = Physics.PYB

    #### Initialize the simulation #############################
    arena_version = 2
    Arena = ArenaMap(version = arena_version)
    Arena.Inflate(radius = 0.2)
    Arena.Panelize(size=0.01)
    Arena.Calculate_Coef_Matrix()
    # Arena.Visualize2D()
    Arena.Wind(0,0,info = 'unknown') # Not used for the moment !

    # vehicle_name_list = ['V1']
    # vehicle_goal_list = [([1, 1, 1.3], 30) ]
    # vehicle_goto_goal_list =[[1.3,0,0,0.1] ]
    # vehicle_pos_list = [[-2, 2, 1.3] ]

    # vehicle_name_list = ['V1']
    # vehicle_goal_list = [([1., 1, 1.5], 30., 10.)  ]
    # vehicle_goto_goal_list =[[0.5,0,0,0.1], ] #altitude,AoA,t_start,Vinf
    # vehicle_pos_list = [[-2, 2, 0.5],   ]

    # vehicle_name_list = ['V1','V2']
    # vehicle_goal_list = [([-1, 0, 1.3], 15) , ([1, 0, 1.3], 15) ]
    # vehicle_goto_goal_list =[[1.3,0,0,0.1], [1.3,np.pi,0,0.1] ] #altitude,AoA,t_start,Vinf
    # vehicle_pos_list = [[1, 0, 1.30], [-1, 0, 1.30]  ]

    # vehicle_name_list = ['V1', 'V2', 'V3']
    # vehicle_goal_list = [([1, 1, 0.7],30., 1.), ([-3,-1, 0.7], 15., 1.), ([-1,-3, 0.7], 30., 1.) ]
    # vehicle_goto_goal_list =[[0.5,0,0,0.1],[0.5,np.pi,0,2], [0.5,-np.pi/2,0,1] ]
    # vehicle_pos_list = [[-2, 2, 0.50],[3, -3, 0.50], [1, 3, 0.50] ]


    # Streamlines Case Right-Left-Cross
    # vehicle_name_list = ['V1', 'V2', 'V3']
    # vehicle_source_list = [0., 0., 0.]
    # vehicle_goal_list = [([3, 2, 0.5], 5, 0.0), ([3, 3, 0.7], 5, 0.0), ([-3, 0, 0.9], 5, 0.0) ]
    # vehicle_goto_goal_list =[[0.5,0,0,0],[0.7,0,0,0], [0.9,0,0,0] ]
    # vehicle_pos_list = [[-2.5, 2, 0.5],[-3, -3, 0.7], [2, 0.1, 0.9]]

    # # NEW CASES 
    # # Case 1 : 3 Vehicles with and without source. No collision in both
    # vehicle_name_list =   ['V1', 'V2', 'V3']
    # vehicle_source_list = [0., 0., 0.]
    # # vehicle_source_list = [0.45, 0., 0.3]
    # vehicle_goal_list = [([1, -3, 0.5], 5, 0.0001), ([-2.5, -2.5, 0.5], 5, 0.0002), ([-1.5, 2, 0.2], 5, 0.0) ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    # vehicle_goto_goal_list =[[0.5,-np.pi/4,0,0],[0.5,np.pi,0,0], [0.5,np.pi/2,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    # vehicle_pos_list = [[0.1, 2.1, 0.5],[2., 1.5, 0.5], [0, -3, 0.5]]

    # Case 4 : 3 Vehicles Green has priority
    vehicle_name_list =   ['V1', 'V2', 'V3']
    vehicle_source_list = [0., 0.3, 2.] # Source_strength
    vehicle_goal_list = [([1.5, -1.5, 0.5], 5, 0.00), ([-2.5, -3 , 0.50], 5, 0.00), ([-2, 2, 0.5], 5, 0.00) ]# goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
    vehicle_goto_goal_list =[[0.5,-np.pi/4,0,0],[0.5,np.pi,0,0], [0.5,np.pi/2,0,0] ] # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
    vehicle_pos_list = [[0.1, 2.1, 0.5],[-2, 2, 0.5], [-2.5, -3, 0.5]]



    vehicle_list = [Vehicle(name,source) for name , source in zip(vehicle_name_list, vehicle_source_list)]
    num_vehicles = len(vehicle_list)
    INIT_XYZS = np.array(vehicle_pos_list)
    INIT_RPYS = np.zeros([num_vehicles,3])
    TARGET_VELS = np.zeros([num_vehicles,3])
    FLOW_VELS = np.zeros([num_vehicles,3])

    for vehicle,set_goal,goto_goal,pos in zip(vehicle_list,vehicle_goal_list,vehicle_goto_goal_list,vehicle_pos_list):
        vehicle.Set_Goal(set_goal[0],set_goal[1],set_goal[2])
        vehicle.Go_to_Goal(goto_goal[0],goto_goal[1],goto_goal[2],goto_goal[3])
        vehicle.Set_Position(pos)
        # pdb.set_trace()

    current_vehicle_list = vehicle_list

    #### Create the environment ################################
    env = VelocityAviary(drone_model=num_vehicles*ARGS.drone,
                         num_drones=num_vehicles,
                         initial_xyzs=INIT_XYZS,
                         initial_rpys=INIT_RPYS,
                         physics=Physics.PYB,
                         neighbourhood_radius=10,
                         freq=ARGS.simulation_freq_hz,
                         aggregate_phy_steps=AGGR_PHY_STEPS,
                         gui=ARGS.gui,
                         record=ARGS.record_video,
                         obstacles=ARGS.obstacles,
                         user_debug_gui=ARGS.user_debug_gui
                         )
    #### Obtain the PyBullet Client ID from the environment ####
    PYB_CLIENT = env.getPyBulletClient()
    DRONE_IDS = env.getDroneIds()


    #### Initialize the logger #################################
    logger = Logger(logging_freq_hz=int(ARGS.simulation_freq_hz/AGGR_PHY_STEPS),
                    num_drones=num_vehicles )

    ### Add ground plane
    PLANE_ID = p.loadURDF("plane.urdf", physicsClientId=PYB_CLIENT)

    ### Add Buildings ################################
    add_buildings(physicsClientId=PYB_CLIENT, version=arena_version)


    #### Compute number of control steps in the simlation ######
    PERIOD = ARGS.duration_sec
    NUM_WP = ARGS.control_freq_hz*PERIOD


    #### Run the simulation ####################################
    CTRL_EVERY_N_STEPS = int(np.floor(env.SIM_FREQ/ARGS.control_freq_hz))
    CALC_FLOW_EVERY_N_STEPS = int(np.floor(env.SIM_FREQ/ARGS.flow_calc_freq_hz))
    action = {str(i): np.array([0.0,0.0,0.0,0.0]) for i in range(num_vehicles)}
    START = time.time()
    for i in range(0, int(ARGS.duration_sec*env.SIM_FREQ), AGGR_PHY_STEPS):

        ############################################################

        #### Step the simulation ###################################
        obs, reward, done, info = env.step(action)

        #### Calculate the vector field ############################
        if i%CALC_FLOW_EVERY_N_STEPS == 0:
            flow_vels = Flow_Velocity_Calculation(vehicle_list,Arena)

        #### Compute control at the desired frequency ##############
        if i%CTRL_EVERY_N_STEPS == 0:
            # print('obs : ',obs['0']['state'][0:3])
            # write the current position and velocity observation into vehicles
            for vehicle_nr, vehicle in enumerate(vehicle_list):

                vehicle.position = obs[str(vehicle_nr)]['state'][0:3]
                vehicle.velocity = obs[str(vehicle_nr)]['state'][10:13]
                # Below is only for a trial of erorous pos and vel effect... ERASE THIS FIX ME
                # pos = obs[str(vehicle_nr)]['state'][0:3]
                # vel = obs[str(vehicle_nr)]['state'][10:13]
                # vehicle.position = np.array([pos[1],pos[0],pos[2]])
                # vehicle.velocity = np.array([vel[1],vel[0],vel[2]])

            for vehicle_nr, vehicle in enumerate(vehicle_list):
                V_des = flow_vels[vehicle_nr] #- vehicle.velocity # FIXME Check this out !!!
                mag = np.linalg.norm(V_des)
                V_des_unit = V_des/mag
                V_des_unit[2] = 0. 
                mag = np.clip(mag, 0., 0.5)
                mag_converted = mag/8.3 # This is Tellos max speed 30Km/h

                # print(f' X : {V_err[0]:.3f} , Y : {V_err[1]:.3f} , Z : {V_err[2]:.3f} Mag : {mag}')
                action[str(vehicle_nr)] = np.array([V_des_unit[0],V_des_unit[1],V_des_unit[2], mag_converted]) # This is not incremental ! It is direct desired action.
                FLOW_VELS[vehicle_nr] = flow_vels[vehicle_nr]
                TARGET_VELS[vehicle_nr] = np.array([V_des_unit*mag_converted])

        # #### Log the simulation ####################################
        for j in range(num_vehicles):
            logger.log(drone=j,
                       timestamp=i/env.SIM_FREQ,
                       state= obs[str(j)]["state"],
                       control=np.hstack([TARGET_VELS[j], FLOW_VELS[j], np.zeros(6)])
                       )

        #### Vehicle Trace #################################
        if i%4 == 0:
            vehicle_colors=[[1, 0, 0], [0, 1, 0], [0, 0, 1],[1, 1, 0], [0, 1, 1], [0.5, 0.5, 1] ]
            for vehicle_nr, vehicle in enumerate(vehicle_list):
                vehicle.position = obs[str(vehicle_nr)]['state'][0:3]
                
                p.addUserDebugLine(lineFromXYZ=INIT_XYZS[vehicle_nr],
                           lineToXYZ=vehicle.position,
                           lineColorRGB=vehicle_colors[vehicle_nr],
                           lifeTime=1 * 1000,
                           physicsClientId=PYB_CLIENT)
                INIT_XYZS[vehicle_nr] = vehicle.position

        #### Printout ##############################################
        if i%env.SIM_FREQ == 0:
            env.render()

        #### Sync the simulation ###################################
        if ARGS.gui:
            sync(i, START, env.TIMESTEP)

    #### Close the environment #################################
    env.close()

    #### Save the simulation results ###########################
    logger.save()




# def main_indoor():
#     """## Indoor Arena 1:"""

#     Arena = ArenaMap(version = 1 )

#     Arena.Inflate(radius = 0.1)

#     Arena.Panelize(size=0.07)

#     Arena.Calculate_Coef_Matrix()
#     # Arena.Visualize2D()

#     Arena.Wind(0,0,info = 'unknown')


#     Vehicle1 = Vehicle("V1",0)  # Vehicle ID, Source_strength
#     Vehicle2 = Vehicle("V2",0)
#     Vehicle3 = Vehicle("V3",0)
#     Vehicle_list = [Vehicle1] #, Vehicle2, Vehicle3]

#     Vehicle1.Set_Goal([1, 1, 0.5], 30)       # goal,goal_strength 30
#     Vehicle2.Set_Goal([-3,-1, 0.5], 15)
#     Vehicle3.Set_Goal([-1,-3, 0.5], 30)

#     Vehicle1.Go_to_Goal(0.5,0,0,0.1)         # altitude,AoA,t_start,Vinf=0.1-2-1
#     Vehicle2.Go_to_Goal(0.5,np.pi,0,2)
#     Vehicle3.Go_to_Goal(0.5,-np.pi/2,0,1)

#     Vehicle1.Set_Position([-2, 2, 0.50])
#     Vehicle2.Set_Position([3, -3, 0.50])
#     Vehicle3.Set_Position([1, 3, 0.50])

#     #starttime = datetime.now()
#     #print( " start: "  + str( starttime ) )
#     current_vehicle_list = Vehicle_list
#     for i in range (50):
#         #cycletime = datetime.now()
#         #print( " Cycle " + str(i) + " start: "  + str(cycletime - starttime ) )
#         Flow_Vels = Flow_Velocity_Calculation(Vehicle_list,Arena)
#         #currennttime = datetime.now()
#         #print( " Cycle flow rate complete" + str(i) + " : "  + str(currennttime - starttime ) )
#         for index,vehicle in enumerate(current_vehicle_list):
#             #currennttime = datetime.now()
#             #print( " Calculations for vehicle" + str(index) + " start: "  + str(currennttime - starttime ) )
#             vehicle.Update_Velocity(Flow_Vels[index])
#             print(f'Flow velocity : {Flow_Vels[index]}')


def main_vector_field():
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Velocity control example using VelocityAviary')
    parser.add_argument('--drone',              default="tello",     type=DroneModel,    help='Drone model (default: CF2X)', metavar='', choices=DroneModel)
    parser.add_argument('--gui',                default=True,       type=str2bool,      help='Whether to use PyBullet GUI (default: True)', metavar='')
    parser.add_argument('--record_video',       default=False,      type=str2bool,      help='Whether to record a video (default: False)', metavar='')
    parser.add_argument('--plot',               default=True,       type=str2bool,      help='Whether to plot the simulation results (default: True)', metavar='')
    parser.add_argument('--user_debug_gui',     default=False,      type=str2bool,      help='Whether to add debug lines and parameters to the GUI (default: False)', metavar='')
    parser.add_argument('--aggregate',          default=True,       type=str2bool,      help='Whether to aggregate physics steps (default: False)', metavar='')
    parser.add_argument('--obstacles',          default=False,      type=str2bool,      help='Whether to add obstacles to the environment (default: True)', metavar='')
    parser.add_argument('--simulation_freq_hz', default=240,        type=int,           help='Simulation frequency in Hz (default: 240)', metavar='')
    parser.add_argument('--control_freq_hz',    default=48,         type=int,           help='Control frequency in Hz (default: 48)', metavar='')
    parser.add_argument('--duration_sec',       default=1020,         type=int,           help='Duration of the simulation in seconds (default: 5)', metavar='')
    ARGS = parser.parse_args()

    AGGR_PHY_STEPS = int(ARGS.simulation_freq_hz/ARGS.control_freq_hz) if ARGS.aggregate else 1
    PHY = Physics.PYB

    #### Initialize the simulation #############################
    # INIT_XYZS = np.array([
    #                       [ 0, 0, .1],
    #                       [.3, 0, .1],
    #                       [.6, 0, .1],
    #                       [0.9, 0, .1]
    #                       ])

    # INIT_RPYS = np.array([
    #                       [0, 0, 0],
    #                       [0, 0, np.pi],
    #                       [0, 0, 0],
    #                       [0, 0, 0]
    #                       ])

    attractor_positions = np.array([[1., 1., 0.4], ])
                                    # [-1., -1., 1.]])

    obstacle_positions = np.array([[0., 0., 0.],])
                                  # [1., 1., 0.],
                                  # [-1., 1., 0.],
                                  # [1., -1., 0.],
                                  # [-1., -1., 0.],])
    wall_points = np.array([[-1., -1.], [-1.,1.], [1.,1.], [1., -1.], [-1., -1.] ])*2.5
    heights = np.array([0. , 3.])
    # attractor_positions = []
    obstacle_positions = []
    # obstacle_positions = np.array([[x*0.5, y*0.5., 0.] for x,y in [range(num_drones), ])

    # Generate Boids array
    num_drones = 2
    INIT_XYZS = np.array([[-0.5+x*0.25, 0., 0.1] for x in range(num_drones)])
    # print(INIT_XYZS)
    boids = [Boid() for _ in range(num_drones)]
    attractors = [Attractor(position) for position in attractor_positions]
    obstacles = [Attractor(position) for position in obstacle_positions]

    # Generate the flow field     
    fields = [Field(id) for id in range(num_drones)]

    # Change the characteristics of the swarm
    for boid in boids:
        boid._BOID_VIEW_ANGLE = 110.
        boid._ATTRACTOR_FACTOR = 0.0
        boid._MAX_SPEED = 1.1
        boid._MIN_SPEED = 0.3

    #### Create the environment ################################
    env = VelocityAviary(drone_model=ARGS.drone,
                         num_drones=num_drones,
                         initial_xyzs=INIT_XYZS,
                         initial_rpys=np.zeros([num_drones,3]), #INIT_RPYS,
                         physics=Physics.PYB,
                         neighbourhood_radius=10,
                         freq=ARGS.simulation_freq_hz,
                         aggregate_phy_steps=AGGR_PHY_STEPS,
                         gui=ARGS.gui,
                         record=ARGS.record_video,
                         obstacles=ARGS.obstacles,
                         user_debug_gui=ARGS.user_debug_gui
                         )

    ### Add Buildings ################################
    env._addExtraObstacles()

    #### Obtain the PyBullet Client ID from the environment ####
    PYB_CLIENT = env.getPyBulletClient()
    DRONE_IDS = env.getDroneIds()

    #### Compute number of control steps in the simlation ######
    PERIOD = ARGS.duration_sec
    NUM_WP = ARGS.control_freq_hz*PERIOD
    # wp_counters = np.array([0 for i in range(4)])s

    #### Initialize the velocity target ########################
    # TARGET_VEL = np.zeros((4,NUM_WP,4))
    # for i in range(NUM_WP):
    #     TARGET_VEL[0, i, :] = [-0.5, 1, 0, 0.19] if i < (NUM_WP/8) else [0.5, -1, 0, 0.99]
    #     TARGET_VEL[1, i, :] = [0, 1, 0, 0.9] if i < (NUM_WP/8+NUM_WP/6) else [0, -1, 0, 0.99]
    #     TARGET_VEL[2, i, :] = [0.2, 1, 0.2, 0.19] if i < (NUM_WP/8+2*NUM_WP/6) else [-0.2, -1, -0.2, 0.99]
    #     TARGET_VEL[3, i, :] = [0, 1, 0.5, 0.19] if i < (NUM_WP/8+3*NUM_WP/6) else [0, -1, -0.5, 0.99]

    # #### Initialize the logger #################################
    # logger = Logger(logging_freq_hz=int(ARGS.simulation_freq_hz/AGGR_PHY_STEPS),
    #                 num_drones=4
    #                 )

    # Draw a static line , this can be used to generate dynamic trailing trace for each quad...
    # for i in range(0, 10, 10):
    #     p.addUserDebugLine(lineFromXYZ=[i, 0., 1.],
    #                        lineToXYZ=[1., i, 1.],
    #                        lineColorRGB=[1, 0, 0],
    #                        # lifeTime=2 * env._CTRL_TIMESTEP,
    #                        physicsClientId=PYB_CLIENT)

    #### Run the simulation ####################################
    CTRL_EVERY_N_STEPS = int(np.floor(env.SIM_FREQ/ARGS.control_freq_hz))
    action = {str(i): np.array([0.0,0.0,0.0,0.0]) for i in range(num_drones)}
    START = time.time()
    for i in range(0, int(ARGS.duration_sec*env.SIM_FREQ), AGGR_PHY_STEPS):

        ############################################################
        # for j in range(3): env._showDroneLocalAxes(j)



        #### Step the simulation ###################################
        obs, reward, done, info = env.step(action)




        #### Compute control at the desired frequency ##############
        if i%CTRL_EVERY_N_STEPS == 0:
          # print('obs : ',obs['0']['state'][0:3])
          # write the position and velocity observation into boids
          for boid_nr, boid in enumerate(boids):
            boid.position = obs[str(boid_nr)]['state'][0:3]
            boid.velocity = obs[str(boid_nr)]['state'][10:13]
            # boid.update(boids, attractors, obstacles)
            # action[str(boid_nr)]=boid.velocity_setpoint

          for boid_nr, boid in enumerate(boids):
            boid.update(boids, attractors, obstacles, wall_points, heights)

            vel_circ = fields[boid_nr].get_vector_field_circle(boid.position)
            
            V_err = boid.velocity_setpoint + vel_circ # + boid.velocity : we dont need to add the velocity as it is being done in the update of each boid.
            mag = magnitude(*V_err)
            

            action[str(boid_nr)]=np.array([V_err[0]/mag,V_err[1]/mag,V_err[2]/mag, mag])

            # vel_circ = fields[boid_nr].get_vector_field_circle(boid.position)
            # # vel_sp = limit_magnitude(self.velocity, _MAX_SPEED, _MIN_SPEED)
            # mag = magnitude(*vel_circ)
            # action[str(boid_nr)] = np.array([vel_circ[0]/mag, vel_circ[1]/mag, vel_circ[2]/mag, mag])

          # print('action : ',action)

            #### Compute control for the current way point #############
            # for j in range(4):
            #     action[str(j)] = TARGET_VEL[j, wp_counters[j], :] 

            #### Go to the next way point and loop #####################
            # for j in range(4): 
            #     wp_counters[j] = wp_counters[j] + 1 if wp_counters[j] < (NUM_WP-1) else 0

        # #### Log the simulation ####################################
        # for j in range(4):
        #     logger.log(drone=j,
        #                timestamp=i/env.SIM_FREQ,
        #                state= obs[str(j)]["state"],
        #                control=np.hstack([TARGET_VEL[j, wp_counters[j], 0:3], np.zeros(9)])
        #                )

        #### Vehicle Trace #################################
        if i%4 == 0:
            Vehicle_colors=[[1, 0, 0], [0, 0, 1], [0, 0, 1],[1, 1, 0], [0, 1, 1], [0.5, 0.5, 1] ]
            for boid_nr, boid in enumerate(boids):
                boid.position = obs[str(boid_nr)]['state'][0:3]
                
                p.addUserDebugLine(lineFromXYZ=INIT_XYZS[boid_nr],
                           lineToXYZ=boid.position,
                           lineColorRGB=Vehicle_colors[boid_nr],
                           lifeTime=1 * 10,
                           physicsClientId=PYB_CLIENT)
                INIT_XYZS[boid_nr] = boid.position

        #### Printout ##############################################
        if i%env.SIM_FREQ == 0:
            env.render()

        #### Sync the simulation ###################################
        if ARGS.gui:
            sync(i, START, env.TIMESTEP)

    #### Close the environment #################################
    env.close()

    #### Plot the simulation results ###########################
    # logger.save_as_csv("vel") # Optional CSV save
    # if ARGS.plot:
    #     logger.plot()

if __name__ == "__main__":
    # main_indoor()
    main_path_plan()
    # main_vector_field()

#EOF