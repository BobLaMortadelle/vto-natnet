#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


import threading

# In[2]:


# from IPython.core.display import display, HTML
# display(HTML("<style>.container { width:90% !important; }</style>"))


# In[3]:


class Building():
    def __init__(self,vertices,position = None): # Buildings(obstacles) are defined by coordinates of their vertices.
        self.vertices = np.array(vertices)
        self.position = np.array(position)
        self.panels = np.array([])
        self.nop  = None           # Number of Panels
        self.K = None              # Coefficient Matrix
        self.K_inv = None
        self.gammas = {}           # Vortex Strenghts
        #self.solution = np.array([])

    def inflate(self,safetyfac = 1.1, rad = 1e-4): 
        rad = rad * safetyfac
        scale = 1e6
        pco = pyclipper.PyclipperOffset() 
        pco.AddPath( (self.vertices[:,:2] * scale).astype(int).tolist() , pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)

        inflated  =  np.array ( pco.Execute( rad*scale )[0] ) / scale
        height = self.vertices[0,2]
        points = np.hstack(( inflated , np.ones((inflated.shape[0],1)) *height ))
        Xavg = np.mean(points[:,0:1])
        Yavg = np.mean(points[:,1:2])
        angles = np.arctan2( ( Yavg*np.ones(len(points[:,1])) - points[:,1] ) , ( Xavg*np.ones(len(points[:,0])) - points[:,0] ) )  
        sorted_angles = sorted(zip(angles, points), reverse = True)
        points_sorted = np.vstack([x for y, x in sorted_angles])
        self.vertices = points_sorted

    def panelize(self,size):
        # Divides obstacle edges into smaller line segments, called panels.
        for index,vertice in enumerate(self.vertices):
            xyz1 = self.vertices[index]                                 # Coordinates of the first vertice
            xyz2 = self.vertices[ (index+1) % self.vertices.shape[0] ]  # Coordinates of the next vertice
            s    = ( (xyz1[0]-xyz2[0])**2 +(xyz1[1]-xyz2[1])**2)**0.5   # Edge Length
            n    = math.ceil(s/size)                                    # Number of panels given desired panel size, rounded up

            if n == 1:
                self.panels = np.vstack((self.panels,np.linspace(xyz1,xyz2,n)[1:]))
                #raise ValueError('Size too large. Please give a smaller size value.')
            if self.panels.size == 0:
                self.panels = np.linspace(xyz1,xyz2,n)[1:]
            else:
            # Divide the edge into "n" equal segments:
                self.panels = np.vstack((self.panels,np.linspace(xyz1,xyz2,n)[1:]))
        
         
    def calculate_coef_matrix(self, method = 'Vortex'):
        # Calculates coefficient matrix.
        if method == 'Vortex':
            self.nop = self.panels.shape[0]    # Number of Panels
            self.pcp = np.zeros((self.nop,2))  # Controlpoints: at 3/4 of panel
            self.vp  = np.zeros((self.nop,2))  # Vortex point: at 1/4 of panel
            self.pl  = np.zeros((self.nop,1))  # Panel Length
            self.pb  = np.zeros((self.nop,1))  # Panel Orientation; measured from horizontal axis, ccw (+)tive, in radians

            XYZ2 = self.panels                      # Coordinates of end point of panel 
            XYZ1 = np.roll(self.panels,1,axis=0)    # Coordinates of the next end point of panel

            self.pcp  = XYZ2 + (XYZ1-XYZ2)*0.75 # Controlpoints point at 3/4 of panel. #self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]                                                   
            self.vp   = XYZ2 + (XYZ1-XYZ2)*0.25 # Vortex point at 1/4 of panel.
            self.pb   = np.arctan2( ( XYZ2[:,1] - XYZ1[:,1] ) , ( XYZ2[:,0] - XYZ1[:,0] ) )  + np.pi/2
            self.K = np.zeros((self.nop,self.nop))
            for m in range(self.nop ):
                for n in range(self.nop ):
                    self.K[m,n] = ( 1 / (2*np.pi)  
                                    * ( (self.pcp[m][1]-self.vp[n][1] ) * np.cos(self.pb[m] ) - ( self.pcp[m][0] - self.vp[n][0] ) * np.sin(self.pb[m] ) ) 
                                    / ( (self.pcp[m][0]-self.vp[n][0] )**2 + (self.pcp[m][1] - self.vp[n][1] )**2 ) )
            # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
            self.K_inv = np.linalg.inv(self.K)
        elif method == 'Source':
            self.nop = self.panels.shape[0]    # Number of Panels
            self.pcp = np.zeros((self.nop,2))  # Controlpoints: at 3/4 of panel
            self.vp  = np.zeros((self.nop,2))  # Vortex point: at 1/4 of panel
            self.pl  = np.zeros((self.nop,1))  # Panel Length
            self.pb  = np.zeros((self.nop,1))  # Panel Orientation; measured from horizontal axis, ccw (+)tive, in radians

            XYZ2 = self.panels                      # Coordinates of end point of panel 
            XYZ1 = np.roll(self.panels,1,axis=0)    # Coordinates of the next end point of panel
        
        # From Katz & Plotkin App D, Program 3
            self.pcp  = XYZ1 + (XYZ2-XYZ1)*0.5 # Controlpoints point at 1/2 of panel. #self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]                                                   
            self.pb   = np.arctan2( ( XYZ2[:,1] - XYZ1[:,1] ) , ( XYZ2[:,0] - XYZ1[:,0] ) )  # Panel Angle
            self.K = np.zeros((self.nop,self.nop))
            self.K = np.zeros((self.nop,self.nop))
            for m in range(self.nop ):
                for n in range(self.nop ):
                    # Convert collocation point to local panel coordinates:
                    xt  = self.pcp[m][0] - XYZ1[n][0]
                    yt  = self.pcp[m][1] - XYZ1[n][1]
                    x2t = XYZ2[n][0] - XYZ1[n][0]
                    y2t = XYZ2[n][1] - XYZ1[n][1]
                    x   =  xt * np.cos(self.pb[n]) + yt  * np.sin(self.pb[n])
                    y   = -xt * np.sin(self.pb[n]) + yt  * np.cos(self.pb[n])
                    x2  = x2t * np.cos(self.pb[n]) + y2t * np.sin(self.pb[n])
                    y2  = 0
                    # Find R1,R2,TH1,TH2:
                    R1  = (     x**2 +      y**2)**0.5
                    R2  = ((x-x2)**2 + (y-y2)**2)**0.5
                    TH1 = np.arctan2( ( y    ) , ( x    ) )
                    TH2 = np.arctan2( ( y-y2 ) , ( x-x2 ) )

                    # Compute Velocity in Local Ref. Frame
                    if m == n:
                        # Diagonal elements: Effect of a panel on itself.
                        up = 0
                        vp = 0.5
                    else:
                        # Off-diagonal elements: Effect of other panels on a panel.
                        up = np.log(R1/R2)/(2*np.pi)
                        vp = (TH2-TH1)/(2*np.pi)
                    # Return to global ref. frame
                    U =  up * np.cos(-self.pb[n]) + vp * np.sin(-self.pb[n]) 
                    V = -up * np.sin(-self.pb[n]) + vp * np.cos(-self.pb[n])
                    # Coefficient Matrix:
                    self.K[m,n] = -up * np.sin(self.pb[n]-self.pb[m]) + vp * np.cos(self.pb[n]-self.pb[m])
            # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
            self.K_inv = np.linalg.inv(self.K)  
    
    def gamma_calc(self,vehicle,othervehicles,arenamap,method = 'Vortex'):
    # Calculates unknown vortex strengths by solving panel method eq.  

        vel_sink   = np.zeros((self.nop,2)) 
        vel_source = np.zeros((self.nop,2))
        vel_source_imag = np.zeros((self.nop,2)) 
        RHS        = np.zeros((self.nop,1))

        if method == 'Vortex':
            vel_sink[:,0] = (-vehicle.sink_strength*(self.pcp[:,0]-vehicle.goal[0]))/(2*np.pi*((self.pcp[:,0]-vehicle.goal[0])**2+(self.pcp[:,1]-vehicle.goal[1])**2))
            vel_sink[:,1] = (-vehicle.sink_strength*(self.pcp[:,1]-vehicle.goal[1]))/(2*np.pi*((self.pcp[:,0]-vehicle.goal[0])**2+(self.pcp[:,1]-vehicle.goal[1])**2))

            vel_source_imag[:,0] = (vehicle.imag_source_strength*(self.pcp[:,0]-vehicle.position[0]))/(2*np.pi*((self.pcp[:,0]-vehicle.position[0])**2+(self.pcp[:,1]-vehicle.position[1])**2))
            vel_source_imag[:,1] = (vehicle.imag_source_strength*(self.pcp[:,1]-vehicle.position[1]))/(2*np.pi*((self.pcp[:,0]-vehicle.position[0])**2+(self.pcp[:,1]-vehicle.position[1])**2))

            for i,othervehicle in enumerate(othervehicles) :
                    
                    vel_source[:,0] += (othervehicle.source_strength*(self.pcp[:,0]-othervehicle.position[0]))/(2*np.pi*((self.pcp[:,0]-othervehicle.position[0])**2+(self.pcp[:,1]-othervehicle.position[1])**2))
                    vel_source[:,1] += (othervehicle.source_strength*(self.pcp[:,1]-othervehicle.position[1]))/(2*np.pi*((self.pcp[:,0]-othervehicle.position[0])**2+(self.pcp[:,1]-othervehicle.position[1])**2))


            RHS[:,0]  = -vehicle.V_inf[0]  * np.cos(self.pb[:])                                      -vehicle.V_inf[1]  * np.sin(self.pb[:])                                      -vel_sink[:,0]     * np.cos(self.pb[:])                                      -vel_sink[:,1]     * np.sin(self.pb[:])                                      -vel_source[:,0]   * np.cos(self.pb[:])                                      -vel_source[:,1]   * np.sin(self.pb[:])                                      -vel_source_imag[:,0]  * np.cos(self.pb[:])                                      -vel_source_imag[:,1]  * np.sin(self.pb[:])                                      -arenamap.windT * arenamap.wind[0] * np.cos(self.pb[:])                                     -arenamap.windT * arenamap.wind[1] * np.sin(self.pb[:]) +vehicle.safety

            self.gammas[vehicle.ID] = np.matmul(self.K_inv,RHS)
        elif method == 'Source':
            for m in range(self.nop):
                # Calculates velocity induced on each panel by a sink element.
                vel_sink[m,0] = (-vehicle.sink_strength*(self.pcp[m][0]-vehicle.goal[0]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))
                vel_sink[m,1] = (-vehicle.sink_strength*(self.pcp[m][1]-vehicle.goal[1]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))

                # Calculates velocity induced on each panel by source elements.
                for othervehicle in othervehicles:
                    vel_source[m,0] += (othervehicle.source_strength*(self.pcp[m][0]-othervehicle.position[0]))/(2*np.pi*((self.pcp[m][0]-othervehicle.position[0])**2+(self.pcp[m][1]-othervehicle.position[1])**2))
                    vel_source[m,1] += (othervehicle.source_strength*(self.pcp[m][1]-othervehicle.position[1]))/(2*np.pi*((self.pcp[m][0]-othervehicle.position[0])**2+(self.pcp[m][1]-othervehicle.position[1])**2))
                # Right Hand Side of panel method eq.
                    # Normal comp. of freestream +  Normal comp. of velocity induced by sink + Normal comp. of velocity induced by sources
                RHS[m]  = -vehicle.V_inf[0] * np.cos(self.pb[m] + (np.pi/2))                                      -vehicle.V_inf[1] * np.sin(self.pb[m] + (np.pi/2))                                      -vel_sink[m,0]    * np.cos(self.pb[m] + (np.pi/2))                                      -vel_sink[m,1]    * np.sin(self.pb[m] + (np.pi/2))                                      -vel_source[m,0]  * np.cos(self.pb[m] + (np.pi/2))                                      -vel_source[m,1]  * np.sin(self.pb[m] + (np.pi/2))                                      -arenamap.windT * arenamap.wind[0] * np.cos(self.pb[m] + (np.pi/2))                                     -arenamap.windT * arenamap.wind[1] * np.sin(self.pb[m] + (np.pi/2)) + vehicle.safety
            self.gammas[vehicle.ID] = np.matmul(self.K_inv,RHS)      


# In[4]:


class ArenaMap():
    def __init__(self,number = 0, generate = 'manual'):
        self.panels = None
        self.wind = [0,0]
        self.windT = 0
        self.buildings =  []
        if generate == 'manual':
            version = number
            if version == 0:   # Dubai Map
                self.buildings = [Building([[55.1477081, 25.0890699, 50 ],[ 55.1475319, 25.0888817, 50 ],[ 55.1472176, 25.0891230, 50 ],[ 55.1472887, 25.0892549, 50],[55.1473938, 25.0893113, 50]]),
                                                    Building([[55.1481917, 25.0895323, 87 ],[ 55.1479193, 25.0892520, 87 ],[ 55.1476012, 25.0895056, 87 ],[ 55.1478737, 25.0897859, 87]]),
                                                    Building([[55.1486038, 25.0899385, 53 ],[ 55.1483608, 25.0896681, 53 ],[ 55.1480185, 25.0899204, 53 ],[ 55.1482615, 25.0901908, 53]]),
                                                    Building([[55.1490795, 25.0905518, 82 ],[ 55.1488245, 25.0902731, 82 ],[ 55.1485369, 25.0904890, 82 ],[ 55.1487919, 25.0907677, 82]]),
                                                    Building([[55.1494092, 25.0909286, 54 ],[ 55.1493893, 25.0908353, 54 ],[ 55.1493303, 25.0907662, 54 ],[ 55.1492275, 25.0907240, 54],[ 55.1491268, 25.0907304, 54],[ 55.1490341, 25.0907831, 54],[ 55.1489856, 25.0908571, 54],[ 55.1489748, 25.0909186, 54],[ 55.1489901, 25.0909906, 54],[ 55.1490319, 25.0910511, 54],[ 55.1491055, 25.0910987, 54],[ 55.1491786, 25.0911146, 54],[ 55.1492562, 25.0911063, 54],[ 55.1493356, 25.0910661, 54],[ 55.1493858, 25.0910076, 54]]),
                                                    Building([[55.1485317, 25.0885948, 73 ],[ 55.1482686, 25.0883259, 73 ],[ 55.1479657, 25.0885690, 73 ],[ 55.1482288, 25.0888379, 73]]),
                                                    Building([[55.1489093, 25.0890013, 101],[ 55.1486436, 25.0887191, 101],[ 55.1483558, 25.0889413, 101],[ 55.1486214, 25.0892235, 101]]),
                                                    Building([[55.1492667, 25.0894081, 75 ],[ 55.1489991, 25.0891229, 75 ],[ 55.1487253, 25.0893337, 75 ],[ 55.1489928, 25.0896189, 75]]),
                                                    Building([[55.1503024, 25.0903554, 45 ],[ 55.1499597, 25.0899895, 45 ],[ 55.1494921, 25.0903445, 45 ],[ 55.1497901, 25.0906661, 45],[ 55.1498904, 25.0906734, 45]]),
                                                    Building([[55.1494686, 25.0880107, 66 ],[ 55.1491916, 25.0877250, 66 ],[ 55.1490267, 25.0877135, 66 ],[ 55.1486811, 25.0879760, 66],[ 55.1490748, 25.0883619, 66]]),
                                                    Building([[55.1506663, 25.0900867, 47 ],[ 55.1503170, 25.0897181, 47 ],[ 55.1499784, 25.0899772, 47 ],[ 55.1503277, 25.0903494, 47]]),
                                                    Building([[55.1510385, 25.0898037, 90 ],[ 55.1510457, 25.0896464, 90 ],[ 55.1507588, 25.0893517, 90 ],[ 55.1503401, 25.0896908, 90],[ 55.1506901, 25.0900624, 90]])]
            # If we want to add other arenas:
            elif version == 1:
                self.buildings = [Building([[-1.5, -2.5, 1], [-2.5, -3.5 , 1], [-3.5, -2.5, 1], [-2.5, -1.5, 1]]),
                                                    Building([[ 3 ,  2, 1 ], [ 2.,  2, 1 ] ,[ 2.,  3, 1 ],[ 3.,  3, 1 ]]),
                                                    Building([[ 3.,  -1, 1 ], [ 2., -2, 1 ] ,[ 1., -2, 1 ],[ 1.,  -1, 1 ],[ 2, 0, 1 ],[ 3., 0, 1 ]]),
                                                    #Building([[ 4.1 , -3.9, 1 ], [ 4, -3.9, 1 ] ,[  4,  3.9, 1 ],[  4.1,  3.9, 1 ]]),
                                                    #Building([[ 3.9 , -4.1, 1 ], [ -3.9, -4.1, 1 ] ,[ -3.9,  -4, 1 ],[  3.9,  -4, 1 ]]),
                                                    #Building([[ 3.9 , 4, 1 ], [ -3.9, 4, 1 ] ,[ -3.9,  4.1, 1 ],[  3.9,  4.1, 1 ]]),
                                                    #Building([[ -4 , -3.9, 1 ], [ -4.1, -3.9, 1 ] ,[  -4.1,  3.9, 1 ],[  -4,  3.9, 1 ]]),
                                                    Building([[0.0, 1.0, 1], [-0.293, 0.293, 1], [-1.0, 0.0, 1], [-1.707, 0.293, 1], [-2.0, 1.0, 1], [-1.707, 1.707, 1], [-1.0, 2.0, 1], [-0.293, 1.707, 1]]),
                                                    Building([[-2.0, 3.0, 1], [-2.5, 2.134, 1], [-3.5, 2.134, 1], [-4.0, 3.0, 1], [-3.5, 3.866, 1], [-2.5, 3.866, 1]]) ]
                                                    
            elif version == 2:
                self.buildings = [Building([[0.3, 1.0, 2], [0.05, 0.567, 2], [-0.45, 0.567, 2], [-0.7, 1.0, 2], [-0.45, 1.433, 2], [0.05, 1.433, 2]]),
                                                    Building([[0.3, 3.0, 1.5], [0.05, 2.567, 1.5], [-0.45, 2.567, 1.5], [-0.7, 3.0, 1.5], [-0.45, 3.433, 1.5], [0.05, 3.433, 1.5]]),
                                                    Building([[1.7, 2.0, 1.2], [1.45, 1.567, 1.2], [0.95, 1.567, 1.2], [0.7, 2.0, 1.2], [0.95, 2.433, 1.2], [1.45, 2.433, 1.2]]),
                                                    Building([[-1.07, -0.2, 1.5], [-1.5, -0.63, 1.5], [-1.93, -0.2, 1.5], [-1.5, 0.23, 1.5]]),
                                                    Building([[-1.07, -2.0, 1.5], [-1.5, -2.43, 1.5], [-1.93, -2.0, 1.5], [-1.5, -1.57, 1.5]]),
                                                    Building([[-2.57, -1.0, 1.5], [-3.0, -1.43, 1.5], [-3.43, -1.0, 1.5], [-3.0, -0.57, 1.5]]),
                                                    Building([[-2.57, 1.0, 1.5], [-3.0, 0.57, 1.5], [-3.43, 1.0, 1.5], [-3.0, 1.43, 1.5]]),
                                                    Building([[1, -2.1, 1.2], [0.5, -2.1, 1.2], [0.5, -1, 1.2], [1, -0.6, 1.2]]),
                                                    Building([[2.5, -2.1, 1.2], [2, -2.1, 1.2], [2, -0.6, 1.2], [2.5, -1, 1.2]])]
            elif version == 3:
                self.buildings = [
                                                    Building([[1.7, 2.0, 2], [1.45, 1.567, 2], [0.95, 1.567, 2], [0.7, 2.0, 2], [0.95, 2.433, 2], [1.45, 2.433, 2]])]
            elif version == 4:
                self.buildings = [Building([[0.3, 1.0, 2], [0.05, 0.567, 2], [-0.45, 0.567, 2], [-0.7, 1.0, 2], [-0.45, 1.433, 2], [0.05, 1.433, 2]]),
                                                    Building([[0.3, 3.0, 2], [0.05, 2.567, 2], [-0.45, 2.567, 2], [-0.7, 3.0, 2], [-0.45, 3.433, 2], [0.05, 3.433, 2]]),
                                                    Building([[1.7, 2.0, 2], [1.45, 1.567, 2], [0.95, 1.567, 2], [0.7, 2.0, 2], [0.95, 2.433, 2], [1.45, 2.433, 2]])]
            elif version == 41:                          
                self.buildings = [Building([[0.3, 1.0, 2], [0.05, 0.567, 2], [-0.45, 0.567, 2], [-0.7, 1.0, 2], [-0.45, 1.433, 2], [0.05, 1.433, 2]]),
                                                    Building([[1.7, 2.0, 2], [1.45, 1.567, 2], [0.95, 1.567, 2], [0.7, 2.0, 2], [0.95, 2.433, 2], [1.45, 2.433, 2]])]
            elif version == 5:
                self.buildings = [Building([[-3.9, 3.9, 2], [-4.1, 3.9, 2], [-4.1, 4.1, 2], [-3.9, 4.1, 2]]),
                                                    Building([[4.1, 3.9, 2], [3.9, 3.9, 2], [3.9, 4.1, 2], [4.1, 4.1, 2]]),
                                                    Building([[4.1, -4.1, 2], [3.9, -4.1, 2], [3.9, -3.9, 2], [4.1, -3.9, 2]]),
                                                    Building([[-3.9, -4.1, 2], [-4.1, -4.1, 2], [-4.1, -3.9, 2], [-3.9, -3.9, 2]])]
            elif version == 6:
                self.buildings = [Building([[3.0, 2.0, 1.2], [2.75, 1.567, 1.2], [2.25, 1.567, 1.2], [2.0, 2.0, 1.2], [2.25, 2.433, 1.2], [2.75, 2.433, 1.2]]), #AddCircularBuilding( 2.5, 2, 6, 0.5, 1.2, angle = 0)
                                                    Building([[1.0, 3.0, 1.5], [0.75, 2.567, 1.5], [0.25, 2.567, 1.5], [0.0, 3.0, 1.5], [0.25, 3.433, 1.5], [0.75, 3.433, 1.5]]), #AddCircularBuilding( 0.5, 3, 6, 0.5, 1.5, angle = 0)
                                                    Building([[1.0, 0.5, 2], [0.75, 0.067, 2], [0.25, 0.067, 2], [0.0, 0.5, 2], [0.25, 0.933, 2], [0.75, 0.933, 2]]), #AddCircularBuilding( 0.5, 0.5, 6, 0.5, 2, angle = 0)  
                                                    Building([[-2.65, 1.5, 1.5], [-3.0, 1.15, 1.5], [-3.35, 1.5, 1.5], [-3.0, 1.85, 1.5]]), #AddCircularBuilding( -3, 1.5, 4, 0.35, 1.5, angle = 0)
                                                    Building([[-2.65, -1.5, 1.5], [-3.0, -1.85, 1.5], [-3.35, -1.5, 1.5], [-3.0, -1.15, 1.5]]), #AddCircularBuilding( -3, -1.5, 4, 0.35, 1.5, angle = 0) 
                                                    Building([[-1.15, -0.2, 1.5], [-1.5, -0.55, 1.5], [-1.85, -0.2, 1.5], [-1.5, 0.15, 1.5]]), #AddCircularBuilding( -1.5, -0.2, 4, 0.35, 1.5, angle = 0)
                                                    Building([[1.5, -2.5, 1.2], [1, -2.5, 1.2], [1, -1.4, 1.2], [1.5, -1, 1.2]]),
                                                    Building([[3.5, -2.5, 1.2], [3, -2.5, 1.2], [3, -1, 1.2], [3.5, -1.4, 1.2]])]
            elif version == 61:
                self.buildings = [Building([[1.0, 0.5, 2], [0.75, 0.067, 2], [0.25, 0.067, 2], [0.0, 0.5, 2], [0.25, 0.933, 2], [0.75, 0.933, 2]])]
            elif version == 65:
                self.buildings = [Building([[3.0, 2.0, 4.2], [2.75, 1.567, 4.2], [2.25, 1.567, 4.2], [2.0, 2.0, 4.2], [2.25, 2.433, 4.2], [2.75, 2.433, 4.2]]), #AddCircularBuilding( 2.5, 2, 6, 0.5, 1.2, angle = 0)
                                Building([[1.0, 3.0, 4.5], [0.75, 2.567, 4.5], [0.25, 2.567, 4.5], [0.0, 3.0, 4.5], [0.25, 3.433, 4.5], [0.75, 3.433, 4.5]]), #AddCircularBuilding( 0.5, 3, 6, 0.5, 1.5, angle = 0)
                                Building([[1.0, 0.5, 4], [0.75, 0.067, 4], [0.25, 0.067, 4], [0.0, 0.5, 4], [0.25, 0.933, 4], [0.75, 0.933, 4]]), #AddCircularBuilding( 0.5, 0.5, 6, 0.5, 2, angle = 0)  
                                Building([[-2.65, 1.5, 4.5], [-3.0, 1.15, 4.5], [-3.35, 1.5, 4.5], [-3.0, 1.85, 4.5]]), #AddCircularBuilding( -3, 1.5, 4, 0.35, 1.5, angle = 0)
                                Building([[-2.65, -1.5, 4.5], [-3.0, -1.85, 4.5], [-3.35, -1.5, 4.5], [-3.0, -1.15, 4.5]]), #AddCircularBuilding( -3, -1.5, 4, 0.35, 1.5, angle = 0) 
                                Building([[-1.15, -0.2, 4.5], [-1.5, -0.55, 4.5], [-1.85, -0.2, 4.5], [-1.5, 0.15, 4.5]]), #AddCircularBuilding( -1.5, -0.2, 4, 0.35, 1.5, angle = 0)
                                Building([[1.5, -2.5, 4.2], [1, -2.5, 4.2], [1, -1.4, 4.2], [1.5, -1, 4.2]]),
                                Building([[3.5, -2.5, 4.2], [3, -2.5, 4.2], [3, -1, 4.2], [3.5, -1.4, 4.2]])]

        elif generate == 'random':
            self.buildings = []
            self.buildings.append(self.AddRandomBuilding())
            while len(self.buildings) < number:
                temp_building = self.AddRandomBuilding()
                for i in range(len(self.buildings) ):
                    x = self.buildings[i].position[0]
                    y = self.buildings[i].position[1]
                    r = self.buildings[i].position[2]
                    d = ( (x-temp_building.position[0])**2 + (y-temp_building.position[1])**2 )**0.5
                    if d < r*1.2 + temp_building.position[2]:
                        break
                    if i == len(self.buildings)-1:
                        self.buildings.append(temp_building)


    def Inflate(self, visualize = False, radius = 1e-4):
        # Inflates buildings with given radius
        if visualize: self.Visualize2D(buildingno="All", show = False)
        for building in self.buildings:
            building.inflate(rad = radius)
        if visualize: self.Visualize2D(buildingno="All")
            #self.buildings[index].vertices[:,:2] = self.buildings[index].inflated 
    def Panelize(self,size):
         # Divides building edges into smaller line segments, called panels.
        for building in self.buildings:
            building.panelize(size)

    def Calculate_Coef_Matrix(self,method = 'Vortex'):
        # !!Assumption: Seperate building interractions are neglected. Each building has its own coef_matrix
        for building in self.buildings:
            building.calculate_coef_matrix(method = method)

    def Visualize2D(self,buildingno = "All",points = "buildings", show = True):
        plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
        #minx = -5 # min(min(building.vertices[:,0].tolist()),minx)
        #maxx = 5 # max(max(building.vertices[:,0].tolist()),maxx)
        #miny = -5 # min(min(building.vertices[:,1].tolist()),miny)
        #maxy = 5 # max(max(building.vertices[:,1].tolist()),maxy) 
        #plt.xlim([minx, maxx])
        #plt.ylim([miny, maxy])
        if buildingno == "All":
            if points == "buildings":
                for building in self.buildings:
                    # plt.scatter(  np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) )
                    plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'b' )
                    plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'b' )
            elif points == "panels":
                for building in self.buildings:
                    plt.scatter(building.panels[:,0],building.panels[:,1])
                    plt.plot(building.panels[:,0],building.panels[:,1])
                    controlpoints = building.pcp
                    plt.scatter(controlpoints[:,0],controlpoints[:,1], marker = '*')
            if show: plt.show()
        else:
            if points == "buildings":
                building = self.buildings[buildingno]
                plt.scatter(  np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) )
                plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) )
            elif points == "panels":
                building = self.buildings[buildingno]
                controlpoints = building.pcp
                plt.scatter(building.panels[:,0],building.panels[:,1])
                plt.scatter(controlpoints[:,0],controlpoints[:,1], marker = '*')
                plt.plot( np.vstack((building.panels[:], building.panels[0] ))[:,0], np.vstack((building.panels[:], building.panels[0]))[:,1],markersize = 0)
            if show: plt.show()

    def Visualize3D(self,buildingno = "All",show = "buildings"):
        pass

    def ScaleIntoMap(self, shape =  np.array(  ((-1,-1),(1,1))  ) ):
        pass

    def AddCircularBuilding(self, x_offset, y_offset, no_of_pts, size, height = 1, angle = 0):
        n = 6 #number of points
        circle_list = []
        #offset_x = -3
        #offset_y = 3
        #size = 1
        #height = 1
        for i in range(no_of_pts):
            delta_rad = -2*math.pi / no_of_pts * i
            circle_list.append( [round(math.cos(delta_rad)*size + x_offset,3) , round( math.sin(delta_rad)*size + y_offset,3), height] )
        print("Building(" + str(circle_list) + ")" )

    def Wind(self,wind_str = 0, wind_aoa = 0, info = 'unknown'):
        self.wind[0] = wind_str * np.cos(wind_aoa)
        self.wind[1] = wind_str * np.sin(wind_aoa)
        if info == 'known':
            self.windT = 1
        elif info == 'unknown':
            self.windT = 0

    def AddRandomBuilding(self):
            center_x = round(random.uniform(-3, 3),3)
            center_y = round(random.uniform(-3, 3),3)
            radius = round(random.uniform(0.25, 1),3)
            position = np.array([center_x, center_y, radius ])
            n = random.randint(3, 10) # number of vertices
            height = round(random.uniform(1.25, 2),3)
            circle_list = []
            theta = np.sort(np.random.rand(n)*2*np.pi)  ## Generate n random numbers btw 0-2pi and sort: small to large
            for j in range(n):
                circle_list.append( [round(math.cos(theta[j])*radius + center_x,3) , round( math.sin(theta[j])*radius  + center_y,3), height] )   ######
            return Building(circle_list,position)  ########


# In[608]:

def dynamics(X, t, U):
    '''  Dynamic model :
    Xdot = X(k+1) - X(k)
    X(k+1) = AX(k) + BU(k)
    where X : [PE,PN,PU,Vx,Vy,Vz] Elem R6
    U : [VdesE, VdesN, VdesU]
    X = X0 + V*t
    V = V0 + a*t
    '''
    k = 1.140
    A = np.array([[1., 0., 0., t, 0., 0.],
                  [0., 1., 0., 0., t, 0.],
                  [0., 0., 1., 0., 0., t],
                  [0., 0., 0., 1.-k*t, 0., 0.],
                  [0., 0., 0., 0., 1.-k*t, 0.],
                  [0., 0., 0., 0., 0., 1.-k*t]])
    B = np.array([[0., 0., 0.],
                  [0., 0., 0.],
                  [0., 0., 0.],
                  [k*t, 0., 0.],
                  [0., k*t, 0.],
                  [0., 0., k*t]])
    
    Xdot = A@X + B@U - X
    return Xdot

def curvature(x,y):
    dx = np.gradient(x)
    ddx = np.gradient(dx)
    dy = np.gradient(y)
    ddy = np.gradient(dy)
    k = np.abs((dx*ddy - dy*ddx))/(dx*dx+dy*dy)**(3/2)
    return k


class Vehicle():
    def __init__(self,ID,source_strength = 0, imag_source_strength = 0.5, correction_type = 'none'):
        self.t               = 0
        self.position        = np.array([0,0,0])
        self.desiredpos      = np.array([0,0,0])
        self.correction      = np.array([0,0,0])
        self.velocity        = np.array([0,0,0])
        self.goal            = None
        self.source_strength = source_strength
        self.imag_source_strength = imag_source_strength
        self.gamma           = 0
        self.altitude_mask   = None
        self.ID              = ID
        self.path            = []
        self.state           = 0
        self.distance_to_destination = None
        self.velocitygain    = 1/50 # 1/300 or less for vortex method, 1/50 for hybrid
        self.correction_type = correction_type
        self._arena = None
        self._vehicle_list = []
        self.propagated_path = None#np.zeros((3,119,6))

    @property
    def arena(self):
        return self._arena
    @arena.setter
    def arena(self,arena):
        self._arena = arena

    @property
    def vehicle_list(self):
        return self._vehicle_list

    @vehicle_list.setter
    def vehicle_list(self,vehicle_list):
        self._vehicle_list = vehicle_list

    def Set_Position(self,pos):
        self.position = np.array(pos)
        self.path     = np.array(pos)

        if np.all(self.goal) != None:
            self.distance_to_destination = np.linalg.norm(np.array(self.goal)-np.array(self.position))
            if np.all(self.distance_to_destination) < 0.2:
                self.state = 1

    def Set_Velocity(self,vel):
        self.velocity = vel

    def Set_Desired_Velocity(self,vel, method='direct'):
        self.velocity_desired = vel
        self.correct_vel(method=method)

    def Set_Next_Goal(self,goal, goal_strength=5):
        self.state         = 0
        self.goal          = goal
        # self.sink_strength = goal_strength NOT USED FOR NOW

    def correct_vel(self, method='None'):

        if method == 'projection':
            #Projection Method
            wind = self.velocity - self.velocity_desired
            self.vel_err = self.vel_err - (wind - np.dot(wind, self.velocity_desired/np.linalg.norm(self.velocity_desired) ) * np.linalg.norm(self.velocity_desired) ) *(1./240.)
        elif method == 'direct':
            # err = self.velocity_desired - self.velocity
            self.vel_err = (self.velocity_desired - self.velocity)*(1./20.)
            # self.vel_err = (self.velocity_desired - self.velocity)
            # print(f' Vel err : {self.vel_err[0]:.3f}  {self.vel_err[1]:.3f}  {self.vel_err[2]:.3f}')
        else:
            self.vel_err = np.zeros(3)
            
        self.velocity_corrected = self.velocity_desired + self.vel_err
        self.velocity_corrected[2] = 0.


    def Set_Goal(self,goal=[3, 0.5, 0.5],goal_strength=5,safety=0):
        self.goal          = np.array(goal)
        self.sink_strength = goal_strength
        self.safety = safety
        

    def Go_to_Goal(self, altitude = 1.5, AoAsgn = 0, t_start = 0, Vinfmag = 0):
        self.AoA = (np.arctan2(self.goal[1]-self.position[1],self.goal[0]-self.position[0])) + AoAsgn*np.pi/2
        '''
        print( " AoA "    +  str( self.AoA*180/np.pi ) )
        print( " goal "   +  str( self.goal ) )
        print( " pos "    +  str( self.position ) )
        print( " AoAsgn " +  str( AoAsgn ) )
        print( " arctan " +  str( (np.arctan2(self.goal[1]-self.position[1],self.goal[0]-self.position[0]))*180/np.pi ) )
        '''
        self.altitude = altitude                                       # Cruise altitude
        self.Vinfmag = Vinfmag
        self.V_inf    = np.array([self.Vinfmag*np.cos(self.AoA), self.Vinfmag*np.sin(self.AoA)]) # Freestream velocity. AoA is measured from horizontal axis, cw (+)tive
        self.t = t_start

    def Update_Velocity(self,flow_vels,arenamap):
    # K is vehicle speed coefficient, a design parameter
        #flow_vels = flow_vels * self.velocitygain
        V_des = flow_vels
        mag = np.linalg.norm(V_des)
        V_des_unit = V_des/mag
        V_des_unit[2] = 0 
        mag = np.clip(mag, 0., 1) #0.3 tello 0.5 pprz
        mag_converted = mag # This is Tellos max speed 30Km/h
        flow_vels2 = V_des_unit * mag_converted
        flow_vels2 = flow_vels2 * self.velocitygain
        prevpos = self.position
        self.desiredpos = self.position + np.array(flow_vels2)
        self.position   = self.position + np.array(flow_vels2)  + np.array([arenamap.wind[0], arenamap.wind[1], 0]) +  self.correction
        dif1 = self.position  -prevpos
        dif2 = self.desiredpos-prevpos
        dif3 = self.position  -self.desiredpos
        if self.correction_type == 'none':
            self.correction      = np.array([0,0,0])
        elif self.correction_type == 'all':
            self.correction = self.desiredpos-self.position + self.correction
        elif self.correction_type == 'project':
            self.correction = -(dif3 - np.dot(dif3,dif2/np.linalg.norm(dif2))*np.linalg.norm(dif2) ) + self.correction
        self.path = np.vstack(( self.path,self.position ))
        if np.linalg.norm(self.goal-self.position) < 0.2: #0.1 for 2d
            self.state = 1
        return self.position
    
    def Update_Position(self):
        self.position = self.Velocity_Calculate(flow_vels)

    def start_propagate(self, maglist=[0.05, 0. , -0.05] ,dyn=dynamics, t0=0., dt=0.02, hor = 2.4, reset_position=True, set_best_state=True):
        self.propagate = threading.Thread(target=self.propagate_future_path, args=(maglist , dyn, t0, dt, hor, reset_position, set_best_state))
        self.propagate_running=True
        self.propagate.start()

    def stop_propagate(self):
        self.propagate_running=False
        self.propagate.join()

    def propagate_future_path(self,  maglist ,dyn=dynamics, t0=0., dt=0.02, hor = 2.4,reset_position=True, set_best_state=True):
        time_horizon = np.arange(t0 + dt, t0 + hor, dt)
        vinfmag_list = maglist
        # path         = np.zeros((len(vinfmag_list),len(time_horizon),6))

        # Generate a copy of vehicle list to be used on branch simulations
        vehicle = Vehicle('sim')
        vehicle.Set_Goal()
        vehicle.Go_to_Goal()

        propagated_vehicle_list = [vehicle] #self._vehicle_list #.copy()

        # Assuming that there is only one vehicle !
        # vehicle = propagated_vehicle_list[0]
        # while 1:
        #     print('Pos :',self.position, vehicle.position)
        #     time.sleep(1)
        while self.propagate_running:
            Xe = np.hstack([self.position,self.velocity])
            path         = np.zeros((len(vinfmag_list),len(time_horizon),6))

            for k,vinfmag_ in enumerate(vinfmag_list):
                X0 = Xe.copy()
                ti=t0

                # Updating the branch simulation vehicles properties
                vehicle.Vinfmag = np.abs(vinfmag_)
                for i, t_ in enumerate(time_horizon):
                    
                    vehicle.AoA   = (np.arctan2(self.goal[1]-X0[1],self.goal[0]-X0[0])) + np.sign(vinfmag_)*np.pi/2
                    vehicle.V_inf = np.array([vehicle.Vinfmag*np.cos(vehicle.AoA), vehicle.Vinfmag*np.sin(vehicle.AoA)])
                    # FIX ME : This will only work because we have only one vehicle...
                    flow_vels = Flow_Velocity_Calculation(propagated_vehicle_list, self._arena, method = 'Vortex')
                    V_des = flow_vels[0]
                    mag = np.linalg.norm(V_des)
                    V_des_unit = V_des/mag
                    V_des_unit[2] = 0 
                    mag = np.clip(mag, 0., 1) #0.3 tello 0.5 pprz
                    mag_converted = mag # This is Tellos max speed 30Km/h
                    flow_vels2 = V_des_unit * mag_converted
                    U = flow_vels2 #* self.velocitygain
                    X = scipy.integrate.odeint(dyn, X0, [ti, t_], args=(U,))
                    X0 = X[1].copy()
                    ti=t_
                    path[k,i]=X[1][:6] # Recording position and velocityto the path
                    vehicle.position=X[1][:3]
                    vehicle.velocity=X[1][3:6]
                    # print('Positions : ', vehicle.position, self.position)

            if reset_position:
                vehicle.position[:] = Xe[:3]
                vehicle.velocity[:] = Xe[3:]
            if set_best_state:
                best = np.argmin([np.sum(curvature(path[i, 30:, 0],path[i, 30:, 1])) for i in range(len(vinfmag_list))])
    #             self.position = path[best,-1, :3]
    #             self.velocity = path[best,-1, 3:6]
            self.propagated_path = path
            vinfmag = vinfmag_list[best]
            print('For vehicle ', str(best), 'Best V_inf is: ', str(vinfmag))
            self.Go_to_Goal(AoAsgn = np.sign(vinfmag), Vinfmag = np.abs(vinfmag))


#     # These should be changed to properties with decorators!!!!
#     def set_AoA(self,):
#         self.AoA = (np.arctan2(self.goal[1]-self.position[1],self.goal[0]-self.position[0])) + AoAsgn*np.pi/2


#     def dynamics(self,X, t, U, P):
#         '''  Dynamic model :
#         Xdot = X(k+1) - X(k)
#         X(k+1) = AX(k) + BU(k)
#         '''
#         Xdot = np.zeros(s_size)
#         gamma_a = X[s_th] - X[s_a]  # air path angle
#         cg, sg = math.cos(gamma_a), math.sin(gamma_a)
#         ca, sa = math.cos(X[s_a]), math.sin(X[s_a])
#         L, D, M = get_aero_forces_and_moments(X, U, P)
#         F = propulsion_model(X, U, P)
#         Xdot[s_y] = X[s_va] * cg - U[i_wy]
#         Xdot[s_h] = X[s_va] * sg - U[i_wz]
#         Xdot[s_va] = (F*ca-D)/P.m-P.g*sg 
#         Xdot[s_a] = X[s_q] - (L+F*sa)/P.m/X[s_va]  + P.g/X[s_va]*cg 
#         Xdot[s_th] = X[s_q]
#         Xdot[s_q] = M/P.Iyy
#         return Xdot
    
#     def propagate_path(self):
#         X = scipy.integrate.odeint(dyn.dyn, Xe, time, args=(Ue, aircraft))




# In[515]:


# ?scipy.integrate.odeint


# In[597]:


# Arena  = ArenaMap(41,'manual')
# ArenaR = ArenaMap(41,'manual')
# Arena.Inflate(radius = 0.2) #0.1
# Arena.Panelize(size= 0.01) #0.08
# Arena.Calculate_Coef_Matrix(method = 'Vortex')

# Case = Cases(73,Arena,'manual')
# Vehicle_list = Case.Vehicle_list


# # In[517]:


# current_vehicle_list = Vehicle_list
# for index,vehicle in enumerate(current_vehicle_list):
#     future_path = vehicle.propagate_future_path(reset_position=False)


# In[518]:


# fig = plt.figure(figsize=(10,10))
# minx = -2.5 # min(min(building.vertices[:,0].tolist()),minx)
# maxx = 3.5 # max(max(building.vertices[:,0].tolist()),maxx)
# miny = -1 # min(min(building.vertices[:,1].tolist()),miny)
# maxy = 5 # max(max(building.vertices[:,1].tolist()),maxy)
# labellist = ['V_inf = 0','V_inf = -0.01','V_inf = 0.01','V_inf = -0.025','V_inf = 0.025','V_inf = -0.05','V_inf = 0.05']
# plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
# for building in Arena.buildings:
#     plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
#     plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
# for buildingR in ArenaR.buildings:
#     plt.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
#     plt.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
# for i in range(7):
#     plt.plot(future_path[i,:,0],future_path[i,:,1], linewidth = 2, label = labellist[i])
# #     plt.plot(Vehicle_list[_v].path[0,0],Vehicle_list[_v].path[0,1],'o')
# #     plt.plot(Vehicle_list[_v].goal[0],Vehicle_list[_v].goal[1],'x')
# plt.xlabel('East-direction --> (m)')
# plt.ylabel('North-direction --> (m)')
# plt.xlim([minx, maxx])
# plt.ylim([miny, maxy])
# plt.legend(loc = 'lower left',fontsize='small')
# plt.show()


# # In[522]:


# # for i in range(len(future_path)):
# #     plt.plot(np.diff(future_path[i, :, 0])**2+np.diff(future_path[i, :, 1])**2)
    
# x = [np.sum(np.diff(future_path[i, :, 0])**2) for i in range(len(future_path))]
# y = [np.sum(np.diff(future_path[i, :, 1])**2) for i in range(len(future_path))]
# print(x,y)
# plt.plot(x)
# plt.plot(y)


# # In[555]:


# def curvature(x,y):
#     dx = np.gradient(x)
#     ddx = np.gradient(dx)
#     dy = np.gradient(y)
#     ddy = np.gradient(dy)
#     k = np.abs((dx*ddy - dy*ddx))/(dx*dx+dy*dy)**(3/2)
#     return k


# # In[556]:


# for i in range(7):
#     plt.plot(future_path[i, :, 0],future_path[i, :, 1])


# # In[557]:


# for i in range(7):
#     k = curvature(future_path[i, 30:, 0],future_path[i, 30:, 1])
#     plt.plot(k)
# #     plt.ylim([-5,5])


# In[562]:


# best = np.argmin([np.sum(curvature(future_path[i, 30:, 0],future_path[i, 30:, 1])) for i in range(7)])
# plt.plot(future_path[i, :, 0],future_path[i, :, 1])


# # In[596]:


# current_vehicle_list = Vehicle_list

    
# fig = plt.figure(figsize=(10,10))
# minx = -2.5 # min(min(building.vertices[:,0].tolist()),minx)
# maxx = 3.5 # max(max(building.vertices[:,0].tolist()),maxx)
# miny = -1 # min(min(building.vertices[:,1].tolist()),miny)
# maxy = 5 # max(max(building.vertices[:,1].tolist()),maxy)
# labellist = ['V_inf = 0','V_inf = -0.01','V_inf = 0.01','V_inf = -0.025','V_inf = 0.025','V_inf = -0.05','V_inf = 0.05']
# plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
# for building in Arena.buildings:
#     plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
#     plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
# for buildingR in ArenaR.buildings:
#     plt.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
#     plt.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
# for _ in range(3):
#     for index,vehicle in enumerate(current_vehicle_list):
#         future_path = vehicle.propagate_future_path(reset_position=False, set_best_state=True)
#     best = np.argmin([np.sum(curvature(future_path[i, 30:, 0],future_path[i, 30:, 1])) for i in range(7)])
#     # Set position and velocity of the vehicle to the best one here
# #     for index,vehicle in enumerate(current_vehicle_list):
# #         vehicle.position = 
#     for i in range(7):
#         if i == best :
#             plt.plot(future_path[i,:,0],future_path[i,:,1], color='b', linewidth = 2, label = labellist[i])
#         else:
#             plt.plot(future_path[i,:,0],future_path[i,:,1], color='g', linewidth = 0.5, alpha = 0.6, label = labellist[i])
#     #     plt.plot(Vehicle_list[_v].path[0,0],Vehicle_list[_v].path[0,1],'o')
#     #     plt.plot(Vehicle_list[_v].goal[0],Vehicle_list[_v].goal[1],'x')
#     plt.xlabel('East-direction --> (m)')
#     plt.ylabel('North-direction --> (m)')
#     plt.xlim([minx, maxx])
#     plt.ylim([miny, maxy])
#     plt.legend(loc = 'lower left',fontsize='small')
# plt.show()


# In[ ]:





# In[609]:


# Arena  = ArenaMap(41,'manual')
# ArenaR = ArenaMap(41,'manual')
# Arena.Inflate(radius = 0.2) #0.1
# Arena.Panelize(size= 0.01) #0.08
# Arena.Calculate_Coef_Matrix(method = 'Vortex')

# Case = Cases(73,Arena,'manual')
# Vehicle_list = Case.Vehicle_list


# # In[610]:


# current_vehicle_list = Vehicle_list
# vinfmag_list = [0.05, 0.025, 0.01, 0. , -0.01, -0.025, -0.05]
# for i in range (350):
#     Flow_Vels = Flow_Velocity_Calculation(current_vehicle_list,Arena,method = 'Vortex')
#     for index,vehicle in enumerate(current_vehicle_list):
#         if (i % 10 == 0):
#             future_path = vehicle.propagate_future_path(reset_position = True, set_best_state = True)
#             best = np.argmin([np.sum(curvature(future_path[i, 30:, 0],future_path[i, 30:, 1])) for i in range(7)])
#             vinfmag = vinfmag_list[best]
#             print('For vehicle ', str(index), 'Best V_inf is: ', str(vinfmag))
#         vehicle.Go_to_Goal(AoAsgn = np.sign(vinfmag), Vinfmag = np.abs(vinfmag))                                           #def Go_to_Goal(self, altitude = 1.5, AoAsgn = 0, t_start = 0, Vinfmag = 0)
#         vehicle.Update_Velocity(Flow_Vels[index],Arena)
#         if vehicle.state == 1:
#             current_vehicle_list = current_vehicle_list[:index] + current_vehicle_list[index+1:]
#             print(str(i))


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[598]:


# for _ in range(3):
#     for index,vehicle in enumerate(current_vehicle_list):
#         future_path = vehicle.propagate_future_path(reset_position=False, set_best_state=True)
#     best = np.argmin([np.sum(curvature(future_path[i, 30:, 0],future_path[i, 30:, 1])) for i in range(7)])
#     plt.plot(future_path[best,:, 3])


# In[ ]:





# In[473]:


# def dynamics(X, t, U):
#     '''  Dynamic model :
#     Xdot = X(k+1) - X(k)
#     X(k+1) = AX(k) + BU(k)
#     where X : [Px,Py,Pz,Vx,Vy,Vz] Elem R6
#     '''
#     k = 0.10
#     A = np.array([[1., 0., 0., t, 0., 0.],
#                   [0., 1., 0., 0., t, 0.],
#                   [0., 0., 1., 0., 0., t],
#                   [0., 0., 0., 1.-k*t, 0., 0.],
#                   [0., 0., 0., 0., 1.-k*t, 0.],
#                   [0., 0., 0., 0., 0., 1.-k*t]])
#     B = np.array([[0., 0., 0.],
#                   [0., 0., 0.],
#                   [0., 0., 0.],
#                   [k*t, 0., 0.],
#                   [0., k*t, 0.],
#                   [0., 0., k*t]])
    
#     Xdot = A@X + B@U - X
#     return Xdot

# def propagate_path():
#     pass


# def propagate_future_path(dyn, Xe, t0, dt=0.1):
#     time_horizon=np.arange(t0+dt,t0+4, dt)
#     path=np.zeros((7,len(time_horizon),3))
#     vinfmag_list = [0.05, 0.025, 0.01, 0. , -0.01, -0.025, -0.05]
#     for k,vinfmag_ in enumerate(vinfmag_list):
#         X0 = Xe.copy()
#         ti=t0
# #         print(X0)
# #         self.Vinfmag = vinfmag_
#         for i, t_ in enumerate(time_horizon):
#             U = np.ones(3)
#             U[2]=0.
#             #self.AoA = (np.arctan2(self.goal[1]-X0[1],self.goal[0]-X0[0])) + np.sign(vinfmag_)*np.pi/2
#             #self.V_inf    = np.array([self.Vinfmag*np.cos(self.AoA), self.Vinfmag*np.sin(self.AoA)])
#             # FIX ME : This will only work because we have only one vehicle...
#             #flow_vels = Flow_Velocity_Calculation(current_vehicle_list,Arena,method = 'Vortex')
#             #U = flow_vels[0]
            
#             X = scipy.integrate.odeint(dyn, X0, [ti, t_], args=(U,))
# #             print(X)
#             X0 = X[1]
#             ti=t_
#             path[k,i]=X[1][:3] # Recording only the positions to the path
#     return path



# X = np.ones(6)*0.
# U = np.ones(3)
# time = np.arange(0., 1, 0.05)
# Xe = np.zeros(6)

# Xpath = propagate_future_path(dynamics, X, 0)
# for i in range(7):
#     plt.plot(Xpath[i,:,0])
# #     plt.plot(Xpath[i,:,1])
# #     plt.plot(Xpath[i,:,2])
# # plt.plot(time, Xpath[:,0])
# # plt.plot(time, Xpath[:,1])
# # plt.plot(time, Xpath[:,4])


# # In[471]:


# t0=0; dt=0.1
# np.arange(t0+dt,t0+4, dt)


# In[61]:


# Arena  = ArenaMap(41,'manual')
# ArenaR = ArenaMap(41,'manual')
# Arena.Inflate(radius = 0.2) #0.1
# Arena.Panelize(size= 0.01) #0.08
# Arena.Calculate_Coef_Matrix(method = 'Vortex')

# Case = Cases(73,Arena,'manual')
# Vehicle_list = Case.Vehicle_list

# current_vehicle_list = Vehicle_list
# for i in range (100):
#     Flow_Vels = Flow_Velocity_Calculation(current_vehicle_list,Arena,method = 'Vortex')
#     for index,vehicle in enumerate(current_vehicle_list):
#         vehicle.Update_Velocity(Flow_Vels[index],Arena)


# In[6]:


def Flow_Velocity_Calculation(vehicles, arenamap, method = 'Vortex', update_velocities = True):

    starttime = datetime.now()
    
    # Calculating unknown vortex strengths using panel method:
    for f,vehicle in enumerate(vehicles):
        # Remove current vehicle from vehicle list. 
        othervehicleslist = vehicles[:f] + vehicles[f+1:]

        # Remove buildings with heights below cruise altitue:
        vehicle.altitude_mask = np.zeros(( len(arenamap.buildings) )) #, dtype=int) 
        for index,panelledbuilding in enumerate(arenamap.buildings):
            if (panelledbuilding.vertices[:,2] > vehicle.altitude).any():
                vehicle.altitude_mask[index] = 1
        related_buildings = list(compress(arenamap.buildings,vehicle.altitude_mask))

        # Vortex strenght calculation (related to panels of each building):
        for building in related_buildings:
            building.gamma_calc(vehicle,othervehicleslist,arenamap,method = method)

    #--------------------------------------------------------------------
    # Flow velocity calculation given vortex strengths:
    flow_vels = np.zeros([len(vehicles),3])

    # Wind velocity
    #U_wind = arenamap.wind[0] #* np.ones([len(vehicles),1])
    #V_wind = arenamap.wind[1] #* np.ones([len(vehicles),1])

    V_gamma   = np.zeros([len(vehicles),2]) # Velocity induced by vortices
    V_sink    = np.zeros([len(vehicles),2]) # Velocity induced by sink element
    V_source  = np.zeros([len(vehicles),2]) # Velocity induced by source elements
    V_sum     = np.zeros([len(vehicles),2]) # V_gamma + V_sink + V_source
    V_normal  = np.zeros([len(vehicles),2]) # Normalized velocity
    V_flow    = np.zeros([len(vehicles),2]) # Normalized velocity inversly proportional to magnitude
    V_norm    = np.zeros([len(vehicles),1]) # L2 norm of velocity vector

    W_sink    = np.zeros([len(vehicles),1]) # Velocity induced by 3-D sink element
    W_source  = np.zeros([len(vehicles),1]) # Velocity induced by 3-D source element
    W_flow    = np.zeros([len(vehicles),1]) # Vertical velocity component (to be used in 3-D scenarios)
    W_sum     = np.zeros([len(vehicles),1])
    W_norm    = np.zeros([len(vehicles),1])
    W_normal  = np.zeros([len(vehicles),1])

    for f,vehicle in enumerate(vehicles):
         
        # Remove current vehicle from vehicle list
        othervehicleslist = vehicles[:f] + vehicles[f+1:]
        
        # Velocity induced by 2D point sink, eqn. 10.2 & 10.3 in Katz & Plotkin:
        V_sink[f,0] = (-vehicle.sink_strength*(vehicle.position[0]-vehicle.goal[0]))/(2*np.pi*((vehicle.position[0]-vehicle.goal[0])**2+(vehicle.position[1]-vehicle.goal[1])**2))
        V_sink[f,1] = (-vehicle.sink_strength*(vehicle.position[1]-vehicle.goal[1]))/(2*np.pi*((vehicle.position[0]-vehicle.goal[0])**2+(vehicle.position[1]-vehicle.goal[1])**2))
        # Velocity induced by 3-D point sink. Katz&Plotkin Eqn. 3.25
        W_sink[f,0] = (-vehicle.sink_strength*(vehicle.position[2]-vehicle.goal[2]))/(4*np.pi*(((vehicle.position[0]-vehicle.goal[0])**2+(vehicle.position[1]-vehicle.goal[1])**2+(vehicle.position[2]-vehicle.goal[2])**2)**1.5))

        # Velocity induced by 2D point source, eqn. 10.2 & 10.3 in Katz & Plotkin:
        source_gain = 0
        for othervehicle in othervehicleslist:
            V_source[f,0] += (othervehicle.source_strength*(vehicle.position[0]-othervehicle.position[0]))/(2*np.pi*((vehicle.position[0]-othervehicle.position[0])**2+(vehicle.position[1]-othervehicle.position[1])**2))
            V_source[f,1] += (othervehicle.source_strength*(vehicle.position[1]-othervehicle.position[1]))/(2*np.pi*((vehicle.position[0]-othervehicle.position[0])**2+(vehicle.position[1]-othervehicle.position[1])**2))
            W_source[f,0] += (source_gain*othervehicle.source_strength*(vehicle.position[2]-othervehicle.position[2]))/(4*np.pi*((vehicle.position[0]-othervehicle.position[0])**2+(vehicle.position[1]-othervehicle.position[1])**2+(vehicle.position[2]-othervehicle.position[2])**2)**(3/2))

        if method == 'Vortex':
            for building in arenamap.buildings:
                u = np.zeros((building.nop,1))
                v = np.zeros((building.nop,1))
                if vehicle.ID in building.gammas.keys():
                    # Velocity induced by vortices on each panel: 
                    
                    u = ( building.gammas[vehicle.ID][:].T/(2*np.pi))  *((vehicle.position[1]-building.pcp[:,1]) /((vehicle.position[0]-building.pcp[:,0])**2+(vehicle.position[1]-building.pcp[:,1])**2)) ####
                    v = (-building.gammas[vehicle.ID][:].T/(2*np.pi))  *((vehicle.position[0]-building.pcp[:,0]) /((vehicle.position[0]-building.pcp[:,0])**2+(vehicle.position[1]-building.pcp[:,1])**2))
                    V_gamma[f,0] = V_gamma[f,0] + np.sum(u) 
                    V_gamma[f,1] = V_gamma[f,1] + np.sum(v)

        elif method == 'Source':
            pass  
        elif method == 'Hybrid':
            pass  

        # Total velocity induced by all elements on map:
        V_sum[f,0] = V_gamma[f,0] + V_sink[f,0] + vehicle.V_inf[0] + V_source[f,0]
        V_sum[f,1] = V_gamma[f,1] + V_sink[f,1] + vehicle.V_inf[1] + V_source[f,1]

        # L2 norm of flow velocity:
        V_norm[f] = (V_sum[f,0]**2 + V_sum[f,1]**2)**0.5
        # Normalized flow velocity:
        V_normal[f,0] = V_sum[f,0]/V_norm[f]
        V_normal[f,1] = V_sum[f,1]/V_norm[f]

        # Flow velocity inversely proportional to velocity magnitude:
        V_flow[f,0] = V_normal[f,0]/V_norm[f] 
        V_flow[f,1] = V_normal[f,1]/V_norm[f]

        # Add wind disturbance
        #V_flow[f,0] = V_flow[f,0] + U_wind 
        #V_flow[f,1] = V_flow[f,0] + V_wind
    
        W_sum[f] = W_sink[f] + W_source[f]
        if W_sum[f] != 0.:
                W_norm[f] = (W_sum[f]**2)**0.5
                W_normal[f] = W_sum[f] /W_norm[f]
                W_flow[f] = W_normal[f]/W_norm[f]
                W_flow[f] = np.clip(W_flow[f],-0.07, 0.07)
        else: 
                W_flow[f] = W_sum[f]

        flow_vels[f,:] = [V_flow[f,0], V_flow[f,1], W_flow[f,0]] 

    return flow_vels


# In[6]:


def Steamline_Calculator(vehicles,vehicle_no,arenamap,ArenaR,resolution = 10, verbose = False, method = 'Vortex', outside = False, arenastlye = 'manual'):
    f = vehicle_no
    vehicle = vehicles[f]
    # Remove current vehicle from vehicle list. 
    othervehicleslist = vehicles[:f] + vehicles[f+1:]
     
    # Remove buildings with heights below cruise altitue:
    vehicle.altitude_mask = np.zeros(( len(arenamap.buildings) )) #, dtype=int) 
    for index,panelledbuilding in enumerate(arenamap.buildings):
        if (panelledbuilding.vertices[:,2] > vehicle.altitude).any():
            vehicle.altitude_mask[index] = 1
    related_buildings = list(compress(Arena.buildings,vehicle.altitude_mask))

    # Vortex strenght calculation (related to panels of each building):
    for building in related_buildings:
        building.gamma_calc(vehicle,othervehicleslist,arenamap, method = method)
    
 #--------------------------------------------------------------------
    # Flow velocity calculation given vortex strengths:
    if outside == False:
        w = 5
        Y, X = np.mgrid[-w:w:complex(0,resolution), -w:w:complex(0,resolution)] # Divide map into grid
    elif outside == True:
        Y, X = np.mgrid[-150:375:complex(0,resolution), -275:275:complex(0,resolution)] # Divide map into grid

    norm      = np.zeros([X.shape[0],Y.shape[0]])

    V_gamma   = np.zeros([X.shape[0],Y.shape[0]]) # Velocity induced by vortices
    V_sink    = np.zeros([X.shape[0],Y.shape[0]]) # Velocity induced by sink element
    V_source  = np.zeros([X.shape[0],Y.shape[0]]) # Velocity induced by source elements
    V_sum     = np.zeros([X.shape[0],Y.shape[0]]) # V_gamma + V_sink + V_source
    V_normal  = np.zeros([X.shape[0],Y.shape[0]]) # Normalized velocity
    V_flow    = np.zeros([X.shape[0],Y.shape[0]]) # Normalized velocity inversly proportional to magnitude
    V         = np.zeros([X.shape[0],Y.shape[0]])

    U_gamma   = np.zeros([X.shape[0],Y.shape[0]]) # Velocity induced by vortices
    U_sink    = np.zeros([X.shape[0],Y.shape[0]]) # Velocity induced by sink element
    U_source  = np.zeros([X.shape[0],Y.shape[0]]) # Velocity induced by source elements
    U_sum     = np.zeros([X.shape[0],Y.shape[0]]) # V_gamma + V_sink + V_source
    U_normal  = np.zeros([X.shape[0],Y.shape[0]]) # Normalized velocity
    U_flow    = np.zeros([X.shape[0],Y.shape[0]]) # Normalized velocity inversly proportional to magnitude
    U         = np.zeros([X.shape[0],Y.shape[0]]) 

    mask      = np.zeros((X.shape), dtype=bool)

    for i in range(X.shape[0]):
        for j in range(Y.shape[0]):
            for building in arenamap.buildings:
                if Point(X[i,j], Y[i,j]).within(Polygon(building.vertices)):
                    mask[i,j] = True
                    if verbose: print( " the point: " +  str(X[i,j]) + "," + str(Y[i,j]) + " is inside a building " )
            if mask[i,j] == False:
                if verbose: print( " the point: " +  str(X[i,j]) + "," + str(Y[i,j]) + " calculation starting: " )
                # Velocity induced by 2D point sink, eqn. 10.2 & 10.3 in Katz & Plotkin:
                U_sink[i,j] = (-vehicle.sink_strength*(X[i,j]-vehicle.goal[0]))/(2*np.pi*((X[i,j]-vehicle.goal[0])**2+(Y[i,j]-vehicle.goal[1])**2))
                V_sink[i,j] = (-vehicle.sink_strength*(Y[i,j]-vehicle.goal[1]))/(2*np.pi*((X[i,j]-vehicle.goal[0])**2+(Y[i,j]-vehicle.goal[1])**2))
                if verbose: print( " U_sink: " +  str(U_sink[i,j]) )
                # Velocity induced by 2D point source, eqn. 10.2 & 10.3 in Katz & Plotkin:
                for othervehicle in othervehicleslist:
                    U_source[i,j] += (othervehicle.source_strength*(X[i,j]-othervehicle.position[0]))/(2*np.pi*((X[i,j]-othervehicle.position[0])**2+(Y[i,j]-othervehicle.position[1])**2))
                    V_source[i,j] += (othervehicle.source_strength*(Y[i,j]-othervehicle.position[1]))/(2*np.pi*((X[i,j]-othervehicle.position[0])**2+(Y[i,j]-othervehicle.position[1])**2))
                if verbose: print( " U_source: " +  str( U_source[i,j] ) )
                
                if method == 'Vortex':
                    for building in arenamap.buildings:
                        u = np.zeros((building.nop,1))
                        v = np.zeros((building.nop,1))
                        if vehicle.ID in building.gammas.keys():
                            # Velocity induced by vortices on each panel:                  
                            for m in range(building.nop):
                                # eqn. 10.9 & 10.10 in Katz & Plotkin:
                                u = (building.gammas[vehicle.ID][m]/(2*np.pi))*((Y[i,j]-building.pcp[m,1])/((X[i,j]-building.pcp[m,0])**2+(Y[i,j]-building.pcp[m,1])**2))
                                v = (-building.gammas[vehicle.ID][m]/(2*np.pi))*((X[i,j]-building.pcp[m,0])/((X[i,j]-building.pcp[m,0])**2+(Y[i,j]-building.pcp[m,1])**2))
                                U_gamma[i,j] = U_gamma[i,j] + u
                                V_gamma[i,j] = V_gamma[i,j] + v
                elif method == 'Source':
                    pass 
                if verbose: print( " U_gamma: " +  str( U_gamma[i,j] ) )
                # Total velocity induced by all elements on map:
                U_sum[i,j] = U_gamma[i,j] + U_sink[i,j] + vehicle.V_inf[0] + U_source[i,j]
                V_sum[i,j] = V_gamma[i,j] + V_sink[i,j] + vehicle.V_inf[1] + V_source[i,j]

                if verbose: print( " U_sum: " +  str( U_sum[i,j] ) )
                # L2 norm of flow velocity:
                norm[i,j] = (U_sum[i,j]**2 + V_sum[i,j]**2)**0.5
        
                # Normalized flow velocity:
                U_normal[i,j] = U_sum[i,j]/norm[i,j]
                V_normal[i,j] = V_sum[i,j]/norm[i,j]

                # Flow velocity inversely proportional to velocity magnitude:
                U_flow[i,j] = U_normal[i,j]/norm[i,j]
                V_flow[i,j] = V_normal[i,j]/norm[i,j]

                U[i,j] = U_flow[i,j]/50   
                V[i,j] = V_flow[i,j]/50

                if verbose: print( " U[i,j]: " +  str( U[i,j] ) )

            for building in arenamap.buildings:
                plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
                plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
            if arenastlye == 'manual':
                for buildingR in ArenaR.buildings:
                    plt.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
                    plt.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
            elif arenastlye == 'random':
                pass

    U =  np.ma.array(U, mask=mask)
    V =  np.ma.array(V, mask=mask)

    plt.streamplot(X, Y, U, V,color=np.absolute(norm), linewidth=1, cmap='plasma')
    plt.clim(0,1) 
    plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
    plt.plot(vehicle.goal[0],vehicle.goal[1],'x')
    plt.colorbar(label = 'Normalized Flow Velocity in x-direction')


# In[603]:


class Cases():
    def __init__(self,number,arenamap, generate = 'manual'):
        if generate == 'manual':
            version = number
            if version == 61:
                Vehicle1 = Vehicle("V1",0,0.5)             # Vehicle ID, Source_strength,safety
                Vehicle_list = [Vehicle1]
                Vehicle1.Set_Position([ -2, 0.5, 0.50])
                Vehicle1.Set_Goal([3, 0.5, 0.5], 5, 0 )       # goal,goal_strength 30, safety 0.001
                Vehicle1.Go_to_Goal(1.5, 0,0)               # altitude,AoAsgn,t_start,Vinfmag

            elif version == 71:
                Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength,safety
                Vehicle2 = Vehicle("V2",0,0.5)
                Vehicle3 = Vehicle("V3",0,0.5)
                Vehicle4 = Vehicle("V4",0,0.5)
                Vehicle5 = Vehicle("V5",0,0.5)
                Vehicle6 = Vehicle("V6",0,0.5)
                Vehicle7 = Vehicle("V7",0,0.5)
                Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5,Vehicle6,Vehicle7]

                Vehicle1.Set_Position([ -2, 3, 0.50])
                Vehicle2.Set_Position([-1.999, 2, 0.50])
                Vehicle3.Set_Position([-2.002, 2, 0.50])
                Vehicle4.Set_Position([-1.99, 2, 0.50])
                Vehicle5.Set_Position([-1.995, 2, 0.50])
                Vehicle6.Set_Position([-2.0015, 2, 0.50]) 
                Vehicle7.Set_Position([-2.001, 2, 0.50])

                Vehicle1.Set_Goal([3, 2, 0.5], 5, 0, 0    )       # goal,goal_strength 30, safety 0.001, Vinfmag=0.5,0.5,1.5 for vortex method
                Vehicle2.Set_Goal([3, 2, 0.5], 5, 0, 0.01 )
                Vehicle3.Set_Goal([3, 2, 0.2], 5, 0, 0.01 )
                Vehicle4.Set_Goal([3, 2, 0.2], 5, 0, 0.025)
                Vehicle5.Set_Goal([3, 2, 0.2], 5, 0, 0.025)
                Vehicle6.Set_Goal([3, 2, 0.2], 5, 0, 0.05 )
                Vehicle7.Set_Goal([3, 2, 0.2], 5, 0, 0.05 )

                Vehicle1.Go_to_Goal(1.5, 0,0)         # altitude,AoAsgn,t_start,
                Vehicle2.Go_to_Goal(1.5, 1,0)
                Vehicle3.Go_to_Goal(1.5, 1,0)
                Vehicle4.Go_to_Goal(1.5, 1,0)
                Vehicle5.Go_to_Goal(1.5,-1,0)
                Vehicle6.Go_to_Goal(1.5,-1,0)
                Vehicle7.Go_to_Goal(1.5,-1,0)
            elif version == 72:
                Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength,safety
                Vehicle2 = Vehicle("V2",0,0.5)
                Vehicle3 = Vehicle("V3",0,0.5)
                Vehicle4 = Vehicle("V4",0,0.5)
                Vehicle5 = Vehicle("V5",0,0.5)
                Vehicle6 = Vehicle("V6",0,0.5)
                Vehicle7 = Vehicle("V7",0,0.5)
                Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5,Vehicle6,Vehicle7]

                Vehicle1.Set_Position([0  ,    3, 0.50])
                Vehicle2.Set_Position([0.002,  3, 0.50])
                Vehicle3.Set_Position([-0.002, 3, 0.50])
                Vehicle4.Set_Position([0.001,  3, 0.50])
                Vehicle5.Set_Position([0.0015, 3, 0.50])
                Vehicle6.Set_Position([-0.0015,3, 0.50]) 
                Vehicle7.Set_Position([-0.001, 3, 0.50])

                Vehicle1.Set_Goal([2, 0, 0.5], 5, 0, 0    )       # goal,goal_strength 30, safety 0.001, Vinfmag=0.5,0.5,1.5 for vortex method
                Vehicle2.Set_Goal([2, 0, 0.5], 5, 0, 0.01 )
                Vehicle3.Set_Goal([2, 0, 0.5], 5, 0, 0.01 )
                Vehicle4.Set_Goal([2, 0, 0.5], 5, 0, 0.025)
                Vehicle5.Set_Goal([2, 0, 0.5], 5, 0, 0.025)
                Vehicle6.Set_Goal([2, 0, 0.5], 5, 0, 0.05 )
                Vehicle7.Set_Goal([2, 0, 0.5], 5, 0, 0.05 )

                Vehicle1.Go_to_Goal(1.5, 0,0)         # altitude,AoAsgn,t_start,
                Vehicle2.Go_to_Goal(1.5, 1,0)
                Vehicle3.Go_to_Goal(1.5, 1,0)
                Vehicle4.Go_to_Goal(1.5, 1,0)
                Vehicle5.Go_to_Goal(1.5,-1,0)
                Vehicle6.Go_to_Goal(1.5,-1,0)
                Vehicle7.Go_to_Goal(1.5,-1,0)
                
            elif version == 73:
                Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength,safety
                Vehicle_list = [Vehicle1]

                Vehicle1.Set_Position([0  ,    3, 0.50])
                Vehicle1.Set_Goal([2, 0, 0.5], 5, 0    )       # goal,goal_strength 30, safety 0.001, Vinfmag=0.5,0.5,1.5 for vortex method
                Vehicle1.Go_to_Goal(1.5, 0,0)         # altitude,AoAsgn,t_start,

            elif version == 74:
                Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength,safety
                Vehicle_list = [Vehicle1]

                Vehicle1.Set_Position([-2,  2, 0.50])
                Vehicle1.Set_Goal([3, 2, 0.5], 5,  0 )       # goal,goal_strength 30, safety 0.001, Vinfmag=0.5,0.5,1.5 for vortex method
                Vehicle1.Go_to_Goal(0.5, 0, 0)         # altitude,AoAsgn,t_start,

            elif version == 121:
                Vehicle1 = Vehicle("V1",0,0.85)            # Vehicle ID, Source_strength imaginary source = 0.75
                Vehicle_list = [Vehicle1] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]
                Vehicle1.Set_Position([-2, 3 , 0.5])
                Vehicle1.Set_Goal([2.5, -3.5, 0.5], 5, 0.)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
                Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5

            elif version == 0:
                Vehicle1 = Vehicle("V1",0,0)            # Vehicle ID, Source_strength
                Vehicle2 = Vehicle("V2",0,0.1)
                Vehicle3 = Vehicle("V3",0,0.5)
                Vehicle4 = Vehicle("V4",0,1)
                Vehicle5 = Vehicle("V5",0,2.5)
                Vehicle6 = Vehicle("V6",0,25)
                Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5,Vehicle6]

                Vehicle1.Set_Goal([3, 2, 0.5], 5, 0)       # goal,goal_strength 30, safety 0.001 for vortex method
                Vehicle2.Set_Goal([3, 2, 0.5], 5, 0)
                Vehicle3.Set_Goal([3, 2, 0.2], 5, 0)
                Vehicle4.Set_Goal([3, 2, 0.2], 5, 0)
                Vehicle5.Set_Goal([3, 2, 0.2], 5, 0)
                Vehicle6.Set_Goal([3, 2, 0.2], 5, 0)

                Vehicle1.Go_to_Goal(1.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
                Vehicle2.Go_to_Goal(1.5,0,0,0)
                Vehicle3.Go_to_Goal(1.5,0,0,0)
                Vehicle4.Go_to_Goal(1.5,0,0,0)
                Vehicle5.Go_to_Goal(1.5,0,0,0)
                Vehicle6.Go_to_Goal(1.5,0,0,0)

                Vehicle1.Set_Position([ -2, 2, 0.50])
                Vehicle2.Set_Position([-1.999, 2, 0.50])
                Vehicle3.Set_Position([-2.002, 2, 0.50])
                Vehicle4.Set_Position([-1.998, 2, 0.50])
                Vehicle5.Set_Position([-1.9985, 2, 0.50])
                Vehicle6.Set_Position([-2.0015, 2, 0.50])          
            elif version == 8:
                Vehicle1 = Vehicle("V1",0,0.85)            # Vehicle ID, Source_strength, im 0.85 veh 0.95
                Vehicle2 = Vehicle("V2",2,0.85)

                Vehicle_list = [Vehicle1,Vehicle2] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

                Vehicle1.Set_Goal([1.5, -3, 0.5], 5, 0)       # for arena 6  [1.5, -3.3, 0.5]
                Vehicle2.Set_Goal([1.50001, -2, 0.5] , 5, 0)   # for arena 6 [2.0001, -2.3, 0.5]

                Vehicle1.Go_to_Goal(0.5,-np.pi/2,0,0.5)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
                Vehicle2.Go_to_Goal(0.5,0,0,0)

                Vehicle1.Set_Position([2, 1.5, 0.50])   #for arena 6 [2.5, 0.5, 0.50]
                Vehicle2.Set_Position([1.5, -2 , 0.5])     #for arena 6 [2, -2.3 , 0.5]
            elif version == 11:
                Vehicle1 = Vehicle("V1",0,0.3)            # Vehicle ID, Source_strength imaginary source = 1.5
                Vehicle2 = Vehicle("V2",0,0.3)
                Vehicle3 = Vehicle("V3",0,0.3)
                Vehicle_list = [Vehicle1,Vehicle2,Vehicle3] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

                Vehicle1.Set_Goal([-3, 0, 0.5], 5, 0.0000)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
                Vehicle2.Set_Goal([2, 3.5, 0.5], 5, 0.00000)
                Vehicle3.Set_Goal([2, 1, 0.5], 5, 0.00000)

                Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
                Vehicle2.Go_to_Goal(0.5,0,0,0)        # np.arctan2(3.5+1,1.5+0.5) = 1.1525719 rad
                Vehicle3.Go_to_Goal(0.5,0,0,0)

                Vehicle1.Set_Position([3, 1 , 0.5])
                Vehicle2.Set_Position([-1, -3 , 0.5])
                Vehicle3.Set_Position([-3, 3 , 0.5])
            elif version == 12:
                Vehicle1 = Vehicle("V1",0,0.85)            # Vehicle ID, Source_strength imaginary source = 0.75
                Vehicle2 = Vehicle("V2",0.75,0.85)
                Vehicle3 = Vehicle("V3",0,0.85)
                Vehicle_list = [Vehicle1,Vehicle2,Vehicle3] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

                Vehicle1.Set_Goal([2.5, -3.5, 0.5], 5, 0.0000)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
                Vehicle2.Set_Goal([-0.5, 3 , 0.5], 5, 0.00000)
                Vehicle3.Set_Goal([3, 3, 0.5], 5, 0.00000)

                Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
                Vehicle2.Go_to_Goal(0.5,0,0,0)   
                Vehicle3.Go_to_Goal(0.5,0,0,0)

                Vehicle1.Set_Position([-2, 3 , 0.5])
                Vehicle2.Set_Position([-2, -3, 0.5])
                Vehicle3.Set_Position([-3, 0, 0.5])
            elif version == 13:
                Vehicle1 = Vehicle("V1",0.25)            # Vehicle ID, Source_strength
                Vehicle2 = Vehicle("V2",0.5)
                Vehicle3 = Vehicle("V3",0.25)
                Vehicle4 = Vehicle("V4",0.5)
                Vehicle5 = Vehicle("V5",0.5)
                Vehicle6 = Vehicle("V6",0.5)
                Vehicle7 = Vehicle("V7",0.25)
                Vehicle8 = Vehicle("V8",0.5)
                Vehicle9 = Vehicle("V9",0.25)
                Vehicle10 = Vehicle("V10",0.5)
                Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5,Vehicle6,Vehicle7,Vehicle8,Vehicle9,Vehicle10] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

                Vehicle1.Set_Goal([3   , 0.5, 0.5], 5, 0)       # goal,goal_strength 30, safety 0.001 for vortex method
                Vehicle2.Set_Goal([2.5 ,-3.5, 0.5], 5, 0)
                Vehicle3.Set_Goal([-1  , 3  , 0.5], 5, 0)
                Vehicle4.Set_Goal([-1  ,-3  , 0.5], 5, 0)
                Vehicle5.Set_Goal([-3  , 0  , 0.5], 5, 0)
                Vehicle6.Set_Goal([2   , 1  , 0.5], 5, 0)
                Vehicle7.Set_Goal([3   , 3.7, 0.5], 5, 0)
                Vehicle8.Set_Goal([-1  ,-1  , 0.5], 5, 0)
                Vehicle9.Set_Goal([2.2 ,-2  , 0.5], 5, 0)
                Vehicle10.Set_Goal([-0.5,-1  , 0.5], 5, 0)

                Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
                Vehicle2.Go_to_Goal(0.5,0,0,0)
                Vehicle3.Go_to_Goal(0.5,0,0,0)
                Vehicle4.Go_to_Goal(0.5,0,0,0)
                Vehicle5.Go_to_Goal(0.5,0,0,0)
                Vehicle6.Go_to_Goal(0.5,0,0,0)
                Vehicle7.Go_to_Goal(0.5,0,0,0)
                Vehicle8.Go_to_Goal(0.5,0,0,0)
                Vehicle9.Go_to_Goal(0.5,0,0,0)
                Vehicle10.Go_to_Goal(0.5,0,0,0)

                Vehicle1.Set_Position([-2  , 2, 0.5])
                Vehicle2.Set_Position([-2  , 1, 0.5])
                Vehicle3.Set_Position([0   ,-2, 0.5])
                Vehicle4.Set_Position([-3  , 3, 0.5])
                Vehicle5.Set_Position([3   , 0, 0.5])
                Vehicle6.Set_Position([-0.5,-3, 0.5])
                Vehicle7.Set_Position([-2  , 3, 0.5])
                Vehicle8.Set_Position([-3  ,-3, 0.5])
                Vehicle9.Set_Position([3.8 , 2, 0.5])
                Vehicle10.Set_Position([1  , 2, 0.5])
        if generate == 'random':
            no_of_vehicles = number
            Vehicle_list = []
            for no in range(no_of_vehicles):
                Vehicle_list.append(self.SetRandomStartGoal(arenamap,"V" + str(no)))
        self.Vehicle_list = Vehicle_list

    def SetRandomStartGoal(self,arenamap,ID):
        loop = True
        while loop == True:
            goal_temp  = [round(random.uniform(-3.5, 3.5),1),round(random.uniform(-3.5, 3.5),1),0.5]
            start_temp = [round(random.uniform(-3.5, 3.5),1),round(random.uniform(-3.5, 3.5),1),0.5]
            d = ( (goal_temp[0]-start_temp[0])**2 + (goal_temp[1]-start_temp[1])**2 )**0.5
            if d > 1:
                for i in range(len(arenamap.buildings) ):
                    x = arenamap.buildings[i].position[0]
                    y = arenamap.buildings[i].position[1]
                    r = arenamap.buildings[i].position[2]
                    d_goal  = ( (x-goal_temp[0])**2  + (y-goal_temp[1])**2 )**0.5
                    d_start = ( (x-start_temp[0])**2 + (y-start_temp[1])**2 )**0.5
                    if d_goal < r*1.2:
                        break
                    elif d_start < r*1.2:
                        break
                    if i == len(arenamap.buildings)-1:
                        goal_position  = goal_temp
                        start_position = start_temp
                        loop = False
        Vehicle_ = Vehicle(ID,0.25)  
        Vehicle_.Set_Goal(goal_position, 5, 0.0000)
        Vehicle_.Set_Position(start_position)
        Vehicle_.Go_to_Goal(0.5,0,0,0)
        return Vehicle_


# In[ ]:





# In[ ]:





# In[335]:


# Arena  = ArenaMap(41,'manual')
# ArenaR = ArenaMap(41,'manual')
# Arena.Inflate(radius = 0.2) #0.1
# Arena.Panelize(size= 0.01) #0.08
# Arena.Calculate_Coef_Matrix(method = 'Vortex')

# Case = Cases(72,Arena,'manual')
# Vehicle_list = Case.Vehicle_list

# current_vehicle_list = Vehicle_list
# for i in range (300):
#     Flow_Vels = Flow_Velocity_Calculation(current_vehicle_list,Arena,method = 'Vortex')
#     for index,vehicle in enumerate(current_vehicle_list):
#         vehicle.Update_Velocity(Flow_Vels[index],Arena)


# In[336]:


# Case = Cases(73,Arena,'manual')
# Vehicle_list = Case.Vehicle_list


# In[337]:


# current_vehicle_list = Vehicle_list
# for i in range (100):
#     Flow_Vels = Flow_Velocity_Calculation(current_vehicle_list,Arena,method = 'Vortex')
#     for index,vehicle in enumerate(current_vehicle_list):
#         vehicle.Update_Velocity(Flow_Vels[index],Arena)


# In[338]:


# fig = plt.figure(figsize=(10,10))
# minx = -2.5 # min(min(building.vertices[:,0].tolist()),minx)
# maxx = 3.5 # max(max(building.vertices[:,0].tolist()),maxx)
# miny = -1 # min(min(building.vertices[:,1].tolist()),miny)
# maxy = 5 # max(max(building.vertices[:,1].tolist()),maxy)
# labellist = ['V_inf = 0','V_inf = -0.01','V_inf = 0.01','V_inf = -0.025','V_inf = 0.025','V_inf = -0.05','V_inf = 0.05']
# plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
# for building in Arena.buildings:
#     plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
#     plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
# for buildingR in ArenaR.buildings:
#     plt.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
#     plt.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
# for _v in range(len(Vehicle_list)):
#     plt.plot(Vehicle_list[_v].path[:,0],Vehicle_list[_v].path[:,1], linewidth = 2, label = labellist[_v])
#     plt.plot(Vehicle_list[_v].path[0,0],Vehicle_list[_v].path[0,1],'o')
#     plt.plot(Vehicle_list[_v].goal[0],Vehicle_list[_v].goal[1],'x')
# plt.xlabel('East-direction --> (m)')
# plt.ylabel('North-direction --> (m)')
# plt.xlim([minx, maxx])
# plt.ylim([miny, maxy])
# plt.legend(loc = 'lower left',fontsize='small')
# plt.show()


# In[ ]:





# In[82]:


# future_path[0,:,2]


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[14]:


# current_vehicle_list = Vehicle_list
# for i in range (350):
#     Flow_Vels = Flow_Velocity_Calculation(current_vehicle_list,Arena,method = 'Vortex')
#     for index,vehicle in enumerate(current_vehicle_list):
#         if vehicle.t >= i:
#             pass
#         else:
#             pass
#         vehicle.Update_Velocity(Flow_Vels[index],Arena)
#         vehicle.Go_to_Goal(1.5,(-1)**(index))
#         #print('Vehicle ', str(index), 'AoA ', str(vehicle.AoA*180/np.pi) )
#         if vehicle.state == 1:
#             current_vehicle_list = current_vehicle_list[:index] + current_vehicle_list[index+1:]
#             print(str(i))

