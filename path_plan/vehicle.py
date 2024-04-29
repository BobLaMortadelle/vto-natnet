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
    def __init__(self,ID,source_strength = 0):
        self.t               = 0
        self.position        = np.zeros(3)
        self.velocity        = np.zeros(3)
        self.goal            = None
        self.source_strength = source_strength
        self.imag_source_strength = 0.4
        self.gamma           = 0
        self.altitude_mask   = None
        self.ID              = ID
        self.path            = []
        self.state           = 0
        self.velocitygain    = 1/50 # 1/300 or less for vortex method, 1/50 for hybrid

    def Set_Position(self,pos):
        self.position = np.array(pos)
        self.path     = np.array(pos)

    def Set_Goal(self,goal,goal_strength,safety):
        self.goal          = goal
        self.sink_strength = goal_strength
        self.safety = safety

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
