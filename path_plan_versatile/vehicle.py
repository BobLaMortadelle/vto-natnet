import numpy as np
from numpy import linalg
import math
import matplotlib.pyplot as plt
import pyclipper
from shapely.geometry import Point, Polygon
from datetime import datetime
from itertools import compress


import pdb

class Vehicle():
    def __init__(self,ID,source_strength = 0, imag_source_strength = 0.4):
        self.t               = 0
        self.position        = np.zeros(3)
        self.velocity        = np.zeros(3)
        self.goal            = np.zeros(3)
        self.source_strength = source_strength
        self.imag_source_strength = imag_source_strength
        self.gamma           = 0
        self.altitude_mask   = None
        self.ID              = ID
        self.path            = []
        self.state           = 0
        self.distance_to_destination = None
        self.velocitygain    = 1/50 # 1/300 or less for vortex method, 1/50 for hybrid
        self.velocity_desired = np.zeros(3)
        self.velocity_corrected = np.zeros(3)
        self.vel_err = np.zeros(3)

    def Set_Position(self,pos):
        self.position = np.array(pos)
        self.path     = np.array(pos)
        # print('GOOOAAALLL : ', self.goal)
        if np.all(self.goal) != None:
            self.distance_to_destination = np.linalg.norm(np.array(self.goal)-np.array(self.position))
            if np.all(self.distance_to_destination) < 0.2:
                self.state = 1

    def Set_Velocity(self,vel):
        self.velocity = vel

    def Set_Desired_Velocity(self,vel, method='direct'):
        self.velocity_desired = vel
        self.correct_vel(method=method)


    def correct_vel(self, method='None'):

        if method == 'projection':
            #Projection Method
            wind = self.velocity - self.velocity_desired
            self.vel_err = self.vel_err - (wind - np.dot(wind, self.velocity_desired/np.linalg.norm(self.velocity_desired) ) * np.linalg.norm(self.velocity_desired) ) *(1./240.)
        elif method == 'direct':
            # err = self.velocity_desired - self.velocity
            self.vel_err = (self.velocity_desired - self.velocity)*(1./40.)
            # self.vel_err = (self.velocity_desired - self.velocity)
            # print(f' Vel err : {self.vel_err[0]:.3f}  {self.vel_err[1]:.3f}  {self.vel_err[2]:.3f}')
        else:
            self.vel_err = np.zeros(3)

        self.velocity_corrected = self.velocity_desired + self.vel_err
        self.velocity_corrected[2] = 0.
        # print(f' Wind              : {wind[0]:.3f}  {wind[1]:.3f}  {wind[2]:.3f}')
        # print(f' Projected Vel err : {self.vel_err[0]:.3f}  {self.vel_err[1]:.3f}  {self.vel_err[2]:.3f}')
        # print(f' Desired   Vel     : {self.velocity_desired[0]:.3f}  {self.velocity_desired[1]:.3f}  {self.velocity_desired[2]:.3f}')
        # print(f' Corrected Vel     : {self.velocity_corrected[0]:.3f}  {self.velocity_corrected[1]:.3f}  {self.velocity_corrected[2]:.3f}')
        # print('   ')
        # print('   ')
        # print('   ')

    def Set_Goal(self,goal,goal_strength,safety):
        self.goal          = goal
        self.sink_strength = goal_strength
        self.safety = safety

    def Set_Next_Goal(self,goal, goal_strength=5):
        self.state         = 0
        self.goal          = goal
        # self.sink_strength = goal_strength NOT USED FOR NOW

    def Go_to_Goal(self,altitude,AoA,t_start,Vinf):
        self.altitude = altitude                                       # Cruise altitude
        self.V_inf    = np.array([Vinf*np.cos(AoA), Vinf*np.sin(AoA)]) # Freestream velocity. AoA is measured from horizontal axis, cw (+)tive
        self.t = t_start

    def Update_Velocity(self,flow_vels):
    # K is vehicle speed coefficient, a design parameter
        #flow_vels = flow_vels * self.velocitygain
        #print(" flow vels " + str(flow_vels))
        V_des = flow_vels
        mag = np.linalg.norm(V_des)
        V_des_unit = V_des/mag
        V_des_unit[2] = 0 
        mag = np.clip(mag, 0., 1.5)
        mag_converted = mag # This is Tellos max speed 30Km/h
        flow_vels2 = V_des_unit * mag_converted
        #print(" flow vels2 " + str(flow_vels2))
        flow_vels2 = flow_vels2 * self.velocitygain
        self.position = np.array(self.position) + np.array(flow_vels2)  #+ [0.001, 0, 0]
        self.path = np.vstack(( self.path,self.position ))
        if np.linalg.norm(np.array(self.goal)-np.array(self.position)) < 0.1:
            self.state = 1
        return self.position
    def Update_Position(self):
        self.position = self.Velocity_Calculate(flow_vels)

# class Vehicle_old():
#     def __init__(self,ID,source_strength = 0):
#         self.t               = 0
#         self.position        = np.zeros(3)
#         self.velocity        = np.zeros(3)
#         self.goal            = None
#         self.source_strength = source_strength
#         self.gamma           = 0
#         self.altitude_mask   = None
#         self.ID              = ID
#         self.path            = []
#         self.state           = 0
#         self.velocitygain    = 1/300 # 1/300 or less for vortex method, 1/50 for hybrid

#     def Set_Position(self,pos):
#         self.position = np.array(pos)
#         self.path     = np.array(pos)

#     def Set_Goal(self,goal,goal_strength,safety):
#         self.goal          = goal
#         self.sink_strength = goal_strength
#         self.safety = safety

#     def Go_to_Goal(self,altitude,AoA,t_start,Vinf):
#         self.altitude = altitude                                       # Cruise altitude
#         self.V_inf    = np.array([Vinf*np.cos(AoA), Vinf*np.sin(AoA)]) # Freestream velocity. AoA is measured from horizontal axis, cw (+)tive
#         self.t = t_start

#     def Update_Velocity(self,flow_vels):
#     # K is vehicle speed coefficient, a design parameter
#         flow_vels = flow_vels * self.velocitygain
#         self.position = np.array(self.position) + np.array(flow_vels)  #+ [0.001, 0, 0]
#         self.path = np.vstack(( self.path,self.position ))
#         if np.linalg.norm(np.array(self.goal)-np.array(self.position)) < 0.1:
#             self.state = 1
#         return self.position
#     def Update_Position(self):
#         self.position = self.Velocity_Calculate(flow_vels)
