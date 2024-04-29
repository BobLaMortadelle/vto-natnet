# -*- coding: utf-8 -*-
"""Path Plan

##Imports
"""
# from google.colab import drive
# drive.mount('/content/drive')

# drive.mount('/content/gdrive')

# pip install pyclipper
# from google.colab import files
# from numba import jit, cuda
# import numba

import numpy as np
from numpy import linalg
import math
import matplotlib.pyplot as plt
import pyclipper
from shapely.geometry import Point, Polygon
from datetime import datetime
from itertools import compress

from building import Building
from vehicle import Vehicle
import pdb

# """##Building Code"""

# class Building():
#     def __init__(self,vertices): # Buildings(obstacles) are defined by coordinates of their vertices.
#         self.vertices = np.array(vertices)
#         self.panels = np.array([])
#         self.nop  = None           # Number of Panels
#         self.K = None              # Coefficient Matrix
#         self.K_inv = None
#         self.gammas = {}           # Vortex Strenghts
#         #self.solution = np.array([])

#     def inflate(self,safetyfac = 1.1, rad = 1e-4): 
#         rad = rad * safetyfac
#         scale = 1e6
#         pco = pyclipper.PyclipperOffset() 
#         pco.AddPath( (self.vertices[:,:2] * scale).astype(int).tolist() , pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)

#         inflated  =  np.array ( pco.Execute( rad*scale )[0] ) / scale
#         height = self.vertices[0,2]
#         points = np.hstack(( inflated , np.ones((inflated.shape[0],1)) *height ))
#         Xavg = np.mean(points[:,0:1])
#         Yavg = np.mean(points[:,1:2])
#         angles = np.arctan2( ( Yavg*np.ones(len(points[:,1])) - points[:,1] ) , ( Xavg*np.ones(len(points[:,0])) - points[:,0] ) )  
#         sorted_angles = sorted(zip(angles, points), reverse = True)
#         points_sorted = np.vstack([x for y, x in sorted_angles])
#         self.vertices = points_sorted

#     def panelize(self,size):
#         # Divides obstacle edges into smaller line segments, called panels.
#         for index,vertice in enumerate(self.vertices):
#             xyz1 = self.vertices[index]                                 # Coordinates of the first vertice
#             xyz2 = self.vertices[ (index+1) % self.vertices.shape[0] ]  # Coordinates of the next vertice
#             s    = ( (xyz1[0]-xyz2[0])**2 +(xyz1[1]-xyz2[1])**2)**0.5   # Edge Length
#             n    = math.ceil(s/size)                                    # Number of panels given desired panel size, rounded up

#             if n == 1:
#                 raise ValueError('Size too large. Please give a smaller size value.')
#             if self.panels.size == 0:
#                 self.panels = np.linspace(xyz1,xyz2,n)[1:]
#             else:
#             # Divide the edge into "n" equal segments:
#                 self.panels = np.vstack((self.panels,np.linspace(xyz1,xyz2,n)[1:]))
        
         
#     def calculate_coef_matrix(self, method = 'Vortex'):
# # Calculates coefficient matrix.
#         if method == 'Vortex':
#             self.nop = self.panels.shape[0]    # Number of Panels
#             self.pcp = np.zeros((self.nop,2))  # Controlpoints: at 3/4 of panel
#             self.vp  = np.zeros((self.nop,2))  # Vortex point: at 1/4 of panel
#             self.pl  = np.zeros((self.nop,1))  # Panel Length
#             self.pb  = np.zeros((self.nop,1))  # Panel Orientation; measured from horizontal axis, ccw (+)tive, in radians

#             XYZ2 = self.panels                      # Coordinates of end point of panel 
#             XYZ1 = np.roll(self.panels,1,axis=0)    # Coordinates of the next end point of panel

#             self.pcp  = XYZ2 + (XYZ1-XYZ2)*0.75 # Controlpoints point at 3/4 of panel. #self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]                                                   
#             self.vp   = XYZ2 + (XYZ1-XYZ2)*0.25 # Vortex point at 1/4 of panel.
#             self.pb   = np.arctan2( ( XYZ2[:,1] - XYZ1[:,1] ) , ( XYZ2[:,0] - XYZ1[:,0] ) )  + np.pi/2
#             self.K = np.zeros((self.nop,self.nop))
#             for m in range(self.nop ):
#                 for n in range(self.nop ):
#                     self.K[m,n] = ( 1 / (2*np.pi)  
#                                     * ( (self.pcp[m][1]-self.vp[n][1] ) * np.cos(self.pb[m] ) - ( self.pcp[m][0] - self.vp[n][0] ) * np.sin(self.pb[m] ) ) 
#                                     / ( (self.pcp[m][0]-self.vp[n][0] )**2 + (self.pcp[m][1] - self.vp[n][1] )**2 ) )
#             # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
#             self.K_inv = np.linalg.inv(self.K)
#         elif method == 'Source':
#             self.nop = self.panels.shape[0]    # Number of Panels
#             self.pcp = np.zeros((self.nop,2))  # Controlpoints: at 3/4 of panel
#             self.vp  = np.zeros((self.nop,2))  # Vortex point: at 1/4 of panel
#             self.pl  = np.zeros((self.nop,1))  # Panel Length
#             self.pb  = np.zeros((self.nop,1))  # Panel Orientation; measured from horizontal axis, ccw (+)tive, in radians

#             XYZ2 = self.panels                      # Coordinates of end point of panel 
#             XYZ1 = np.roll(self.panels,1,axis=0)    # Coordinates of the next end point of panel
        
#         # From Katz & Plotkin App D, Program 3
#             self.pcp  = XYZ1 + (XYZ2-XYZ1)*0.5 # Controlpoints point at 1/2 of panel. #self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]                                                   
#             self.pb   = np.arctan2( ( XYZ2[:,1] - XYZ1[:,1] ) , ( XYZ2[:,0] - XYZ1[:,0] ) )  # Panel Angle
#             self.K = np.zeros((self.nop,self.nop))
#             self.K = np.zeros((self.nop,self.nop))
#             for m in range(self.nop ):
#                 for n in range(self.nop ):
#                     # Convert collocation point to local panel coordinates:
#                     xt  = self.pcp[m][0] - XYZ1[n][0]
#                     yt  = self.pcp[m][1] - XYZ1[n][1]
#                     x2t = XYZ2[n][0] - XYZ1[n][0]
#                     y2t = XYZ2[n][1] - XYZ1[n][1]
#                     x   =  xt * np.cos(self.pb[n]) + yt  * np.sin(self.pb[n])
#                     y   = -xt * np.sin(self.pb[n]) + yt  * np.cos(self.pb[n])
#                     x2  = x2t * np.cos(self.pb[n]) + y2t * np.sin(self.pb[n])
#                     y2  = 0
#                     # Find R1,R2,TH1,TH2:
#                     R1  = (     x**2 +      y**2)**0.5
#                     R2  = ((x-x2)**2 + (y-y2)**2)**0.5
#                     TH1 = np.arctan2( ( y    ) , ( x    ) )
#                     TH2 = np.arctan2( ( y-y2 ) , ( x-x2 ) )

#                     #R1 = ((XYZ1[m][0]-self.pcp[n][0])**2 + (XYZ1[m][1]-self.pcp[n][1])**2 )**0.5
#                     #R2 = ((XYZ2[m][0]-self.pcp[n][0])**2 + (XYZ2[m][1]-self.pcp[n][1])**2 )**0.5
#                     #T1 = np.arctan2((XYZ1[m][1]-self.pcp[n][1]),(XYZ1[m][0]-self.pcp[n][0])) + self.pb[m]
#                     #T2 = np.arctan2((XYZ2[m][1]-self.pcp[n][1]),(XYZ2[m][0]-self.pcp[n][0])) + self.pb[m]

#                     # Compute Velocity in Local Ref. Frame
#                     if m == n:
#                         # Diagonal elements: Effect of a panel on itself.
#                         up = 0
#                         vp = 0.5
#                     else:
#                         # Off-diagonal elements: Effect of other panels on a panel.
#                         up = np.log(R1/R2)/(2*np.pi)
#                         vp = (TH2-TH1)/(2*np.pi)
#                     # Return to global ref. frame
#                     U =  up * np.cos(-self.pb[n]) + vp * np.sin(-self.pb[n]) 
#                     V = -up * np.sin(-self.pb[n]) + vp * np.cos(-self.pb[n])
#                     # Coefficient Matrix:
#                     #self.K[m,n] = -U * np.sin(self.pb[m]) + V * np.cos(self.pb[m])
#                     self.K[m,n] = -up * np.sin(self.pb[n]-self.pb[m]) + vp * np.cos(self.pb[n]-self.pb[m])
#             # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
#             self.K_inv = np.linalg.inv(self.K)  
#         elif method == 'Hybrid':
#             self.nop = self.panels.shape[0]    # Number of Panels
#             self.pcp = np.zeros((self.nop,2))  # Controlpoints: at 3/4 of panel
#             self.vp  = np.zeros((self.nop,2))  # Vortex point: at 1/4 of panel
#             self.pl  = np.zeros((self.nop,1))  # Panel Length
#             self.pb  = np.zeros((self.nop,1))  # Panel Orientation; measured from horizontal axis, ccw (+)tive, in radians

#             XYZ2 = self.panels                      # Coordinates of end point of panel 
#             XYZ1 = np.roll(self.panels,1,axis=0)    # Coordinates of the next end point of panel

#             self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]                                                   
#             self.pl   = ( ( XYZ1[:,0]-XYZ2[:,0] )**2 +( XYZ1[:,1]-XYZ2[:,1] )**2 )**0.5 
#             self.pb   = np.arctan2( ( XYZ2[:,1] - XYZ1[:,1] ) , ( XYZ2[:,0] - XYZ1[:,0] ) ) + (np.pi/2)
#             self.K = np.zeros((self.nop,self.nop))
#             self.K = np.zeros((self.nop,self.nop))
#     # Calculates coefficient matrix.
#             self.K = np.zeros((self.nop,self.nop))
#             for m in range(self.nop ):
#                 for n in range(self.nop ):
#                     if m == n:
#                         # Diagonal elements: Effect of a panel on itself.
#                         self.K[m,n] = -2/(np.pi*self.pl[n])
#                     else:
#                         # Off-diagonal elements: Effect of other panels on a panel.
#                         self.K[m,n] = ( self.pl[n] / (2*np.pi)  
#                                         * ( (self.pcp[m][1]-self.pcp[n][1] ) * np.cos(self.pb[m] ) - ( self.pcp[m][0] - self.pcp[n][0] ) * np.sin(self.pb[m] ) ) 
#                                         / ( (self.pcp[m][0]-self.pcp[n][0] )**2 + (self.pcp[m][1] - self.pcp[n][1] )**2 ) )
#             # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
#             self.K_inv = np.linalg.inv(self.K)         
#     '''
#     def vel_sink_calc(self,vehicle):
#     # Calculates velocity induced on each panel by a sink element.
#         vel_sink = np.zeros((self.nop,2)) 
#         for m in range(self.nop):
#             vel_sink[m,0] = (-vehicle.sink_strength*(self.pcp[m][0]-vehicle.goal[0]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))
#             vel_sink[m,1] = (-vehicle.sink_strength*(self.pcp[m][1]-vehicle.goal[1]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))
#         self.vel_sink[vehicle.ID] =  vel_sink   

#     def vel_source_calc(self,vehicle,othervehicles):
#     # Calculates velocity induced on each panel by source elements.
#         vel_source = np.zeros((self.nop,2)) 
#         for othervehicle in othervehicles:
#             for m in range(self.nop):
#                     vel_source[m,0] += (othervehicle.source_strength*(self.pcp[m][0]-othervehicle.position[0]))/(2*np.pi*((self.pcp[m][0]-othervehicle.position[0])**2+(self.pcp[m][1]-othervehicle.position[1])**2))
#                     vel_source[m,1] += (othervehicle.source_strength*(self.pcp[m][1]-othervehicle.position[1]))/(2*np.pi*((self.pcp[m][0]-othervehicle.position[0])**2+(self.pcp[m][1]-othervehicle.position[1])**2))
#         self.vel_source[vehicle.ID] =  vel_source 
        
#     '''
    
#     def gamma_calc(self,vehicle,othervehicles,arenamap,method = 'Vortex'):
#     # Calculates unknown vortex strengths by solving panel method eq.  
#         #cycletime = datetime.now()

#         vel_sink   = np.zeros((self.nop,2)) 
#         vel_source = np.zeros((self.nop,2)) 
#         RHS        = np.zeros((self.nop,1))
#         #currenttime = datetime.now()
#         #print( " New array generation: "  + str(currenttime - cycletime ) )

#         if method == 'Vortex':
#             vel_sink[:,0] = (-vehicle.sink_strength*(self.pcp[:,0]-vehicle.goal[0]))/(2*np.pi*((self.pcp[:,0]-vehicle.goal[0])**2+(self.pcp[:,1]-vehicle.goal[1])**2))
#             vel_sink[:,1] = (-vehicle.sink_strength*(self.pcp[:,1]-vehicle.goal[1]))/(2*np.pi*((self.pcp[:,0]-vehicle.goal[0])**2+(self.pcp[:,1]-vehicle.goal[1])**2))

#             for i,othervehicle in enumerate(othervehicles) :
                    
#                     vel_source[:,0] += (othervehicle.source_strength*(self.pcp[:,0]-othervehicle.position[0]))/(2*np.pi*((self.pcp[:,0]-othervehicle.position[0])**2+(self.pcp[:,1]-othervehicle.position[1])**2))
#                     vel_source[:,1] += (othervehicle.source_strength*(self.pcp[:,1]-othervehicle.position[1]))/(2*np.pi*((self.pcp[:,0]-othervehicle.position[0])**2+(self.pcp[:,1]-othervehicle.position[1])**2))


#             RHS[:,0]  = -vehicle.V_inf[0] * np.cos(self.pb[:])  \
#                                     -vehicle.V_inf[1] * np.sin(self.pb[:])  \
#                                     -vel_sink[:,0]    * np.cos(self.pb[:])  \
#                                     -vel_sink[:,1]    * np.sin(self.pb[:])  \
#                                     -vel_source[:,0]  * np.cos(self.pb[:])  \
#                                     -vel_source[:,1]  * np.sin(self.pb[:])  \
#                                     -arenamap.windT * arenamap.wind[0] * np.cos(self.pb[:]) \
#                                     -arenamap.windT * arenamap.wind[1] * np.sin(self.pb[:]) +vehicle.safety
#                                     #-2                * np.cos(self.pb[m])  \
#                                     #-0                * np.sin(self.pb[m])#\

#             #for m in range(self.nop):
#                 # Calculates velocity induced on each panel by a sink element.
                
                

#                 #currenttime = datetime.now()
#                 #print( " Calculations for panel " + str(m) + " sink:"   + str(currenttime - cycletime ) )
#                 # Calculates velocity induced on each panel by source elements.
                
#                 # Right Hand Side of panel method eq.
#                     # Normal comp. of freestream +  Normal comp. of velocity induced by sink + Normal comp. of velocity induced by sources
#                 #currenttime = datetime.now()
#                 #print( " Calculations for panel " + str(m) + " sources:"   + str(currenttime - cycletime ) )


                

#                 #currenttime = datetime.now()
#                 #print( " Calculations for panel " + str(m) + " rhs:"   + str(currenttime - cycletime ) )
#             self.gammas[vehicle.ID] = np.matmul(self.K_inv,RHS)
#         elif method == 'Source':
#             for m in range(self.nop):
#                 # Calculates velocity induced on each panel by a sink element.
#                 vel_sink[m,0] = (-vehicle.sink_strength*(self.pcp[m][0]-vehicle.goal[0]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))
#                 vel_sink[m,1] = (-vehicle.sink_strength*(self.pcp[m][1]-vehicle.goal[1]))/(2*np.pi*((self.pcp[m][0]-vehicle.goal[0])**2+(self.pcp[m][1]-vehicle.goal[1])**2))

#                 # Calculates velocity induced on each panel by source elements.
#                 for othervehicle in othervehicles:
#                     vel_source[m,0] += (othervehicle.source_strength*(self.pcp[m][0]-othervehicle.position[0]))/(2*np.pi*((self.pcp[m][0]-othervehicle.position[0])**2+(self.pcp[m][1]-othervehicle.position[1])**2))
#                     vel_source[m,1] += (othervehicle.source_strength*(self.pcp[m][1]-othervehicle.position[1]))/(2*np.pi*((self.pcp[m][0]-othervehicle.position[0])**2+(self.pcp[m][1]-othervehicle.position[1])**2))
#                 # Right Hand Side of panel method eq.
#                     # Normal comp. of freestream +  Normal comp. of velocity induced by sink + Normal comp. of velocity induced by sources
#                 RHS[m]  = -vehicle.V_inf[0] * np.cos(self.pb[m] + (np.pi/2))  \
#                                     -vehicle.V_inf[1] * np.sin(self.pb[m] + (np.pi/2))  \
#                                     -vel_sink[m,0]    * np.cos(self.pb[m] + (np.pi/2))  \
#                                     -vel_sink[m,1]    * np.sin(self.pb[m] + (np.pi/2))  \
#                                     -vel_source[m,0]  * np.cos(self.pb[m] + (np.pi/2))  \
#                                     -vel_source[m,1]  * np.sin(self.pb[m] + (np.pi/2))  \
#                                     -arenamap.windT * arenamap.wind[0] * np.cos(self.pb[m] + (np.pi/2)) \
#                                     -arenamap.windT * arenamap.wind[1] * np.sin(self.pb[m] + (np.pi/2)) + vehicle.safety
#             self.gammas[vehicle.ID] = np.matmul(self.K_inv,RHS)      
            
#         #currenttime = datetime.now()
#         #print( " Calculations for panel  gammas:"   + str(currenttime - cycletime ) )


class ArenaMap():
    def __init__(self,version = 0):
        self.panels = None
        self.wind = [0,0]
        self.windT = 0
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
            # B1 : Hexa with center -0.20,1.0 height 2.0
            # B2 : Hexa with center -0.20,3.0 height 1.5
            # B3 : Hexa with center  1.20,2.0 height 1.2
            # B4 : Square with center -1.5, -0.2 angle 45deg height 1.5
            # B5 : Square with center -1.5, -2.0 angle 45deg height 1.5
            # B6 : Square with center -3.0, -1.0 angle 45deg height 1.5
            # B7 : Square with center -3.0,  1.0 angle 45deg height 1.5
            # B8 & B9 are the strange ones
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
        elif version == 5:
            self.buildings = [Building([[-3.9, 3.9, 2], [-4.1, 3.9, 2], [-4.1, 4.1, 2], [-3.9, 4.1, 2]]),
                            Building([[4.1, 3.9, 2], [3.9, 3.9, 2], [3.9, 4.1, 2], [4.1, 4.1, 2]]),
                            Building([[4.1, -4.1, 2], [3.9, -4.1, 2], [3.9, -3.9, 2], [4.1, -3.9, 2]]),
                            Building([[-3.9, -4.1, 2], [-4.1, -4.1, 2], [-4.1, -3.9, 2], [-3.9, -3.9, 2]])]


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


# class Vehicle():
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



def Flow_Velocity_Calculation(vehicles, arenamap, method = 'Vortex', update_velocities = True):

    starttime = datetime.now()
    
    # Calculating unknown vortex strengths using panel method:
    for f,vehicle in enumerate(vehicles):
        # Remove current vehicle from vehicle list. 
        #cycletime = datetime.now()

        othervehicleslist = vehicles[:f] + vehicles[f+1:]
     
        #currenttime = datetime.now()
        #print( " Vehicle removal over: "  + str(currenttime - cycletime ) )

        # Remove buildings with heights below cruise altitue:
        vehicle.altitude_mask = np.zeros(( len(arenamap.buildings) )) #, dtype=int) 
        for index,panelledbuilding in enumerate(arenamap.buildings):
            if (panelledbuilding.vertices[:,2] > vehicle.altitude).any():
                vehicle.altitude_mask[index] = 1
        related_buildings = list(compress(arenamap.buildings,vehicle.altitude_mask))

        #currenttime = datetime.now()
        #print( " Building mask for all buildings over: "  + str(currenttime - cycletime ) )

        # Vortex strenght calculation (related to panels of each building):
        for building in related_buildings:
            #building.vel_sink_calc(vehicle)
            #building.vel_source_calc(vehicle,othervehicleslist)
            #building.RMS_calc(vehicle)
            building.gamma_calc(vehicle,othervehicleslist,arenamap,method = method)

        #currenttime = datetime.now()
        #print( " Gamma calculation for related buildings: "  + str(currenttime - cycletime ) )

    #currenttime = datetime.now()
    #print( " Flow vel init over: "  + str(currenttime - starttime ) )
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

        #currenttime = datetime.now()
        #print( " Flow sink calc over: "  + str(currenttime - starttime ) )
        # Velocity induced by 2D point source, eqn. 10.2 & 10.3 in Katz & Plotkin:
        for othervehicle in othervehicleslist:
            V_source[f,0] += (othervehicle.source_strength*(vehicle.position[0]-othervehicle.position[0]))/(2*np.pi*((vehicle.position[0]-othervehicle.position[0])**2+(vehicle.position[1]-othervehicle.position[1])**2))
            V_source[f,1] += (othervehicle.source_strength*(vehicle.position[1]-othervehicle.position[1]))/(2*np.pi*((vehicle.position[0]-othervehicle.position[0])**2+(vehicle.position[1]-othervehicle.position[1])**2))
            W_source[f,0] += (othervehicle.source_strength*(vehicle.position[2]-othervehicle.position[2]))/(4*np.pi*((vehicle.position[0]-othervehicle.position[0])**2+(vehicle.position[1]-othervehicle.position[1])**2+(vehicle.position[2]-othervehicle.position[2])**2)**(3/2))
        #currenttime = datetime.now()
        #print( " Flow source calc over: "  + str(currenttime - starttime ) )

        if method == 'Vortex':
            for building in arenamap.buildings:
                u = np.zeros((building.nop,1))
                v = np.zeros((building.nop,1))
                if vehicle.ID in building.gammas.keys():
                    # Velocity induced by vortices on each panel: 
                    global a, b, c, d, e
                    
                    u = ( building.gammas[vehicle.ID][:].T/(2*np.pi))  *((vehicle.position[1]-building.pcp[:,1]) /((vehicle.position[0]-building.pcp[:,0])**2+(vehicle.position[1]-building.pcp[:,1])**2)) ####
                    v = (-building.gammas[vehicle.ID][:].T/(2*np.pi))  *((vehicle.position[0]-building.pcp[:,0]) /((vehicle.position[0]-building.pcp[:,0])**2+(vehicle.position[1]-building.pcp[:,1])**2))
                    V_gamma[f,0] = V_gamma[f,0] + np.sum(u) 
                    V_gamma[f,1] = V_gamma[f,1] + np.sum(v)
                    """
                    for m in range(building.nop):  
                        u = ( building.gammas[vehicle.ID][m]/(2*np.pi))  *((vehicle.position[1]-building.pcp[m,1]) /((vehicle.position[0]-building.pcp[m,0])**2+(vehicle.position[1]-building.pcp[m,1])**2)) ####
                        v = (-building.gammas[vehicle.ID][m]/(2*np.pi))  *((vehicle.position[0]-building.pcp[m,0]) /((vehicle.position[0]-building.pcp[m,0])**2+(vehicle.position[1]-building.pcp[m,1])**2))
                        V_gamma[f,0] = V_gamma[f,0] + u
                        V_gamma[f,1] = V_gamma[f,1] + v
                    """
                    a = building.gammas[vehicle.ID]
                    
                    b = building.pcp   
                    c = u
                    d = v 
                    e = V_gamma
        elif method == 'Source':
            for building in arenamap.buildings:
                if vehicle.ID in building.gammas.keys():
                    # Velocity induced by vortices on each panel:       
                    XYZ2 = building.panels                      # Coordinates of end point of panel 
                    XYZ1 = np.roll(building.panels,1,axis=0)    # Coordinates of the next end point of panel                                               
                    for m in range(building.nop ):
                        # Convert collocation point to local panel coordinates:
                        xt  = vehicle.position[0] - XYZ1[m][0]
                        yt  = vehicle.position[1] - XYZ1[m][1]
                        x2t = XYZ2[m][0] - XYZ1[m][0]
                        y2t = XYZ2[m][1] - XYZ1[m][1]
                        x   =  xt * np.cos(building.pb[m]) + yt  * np.sin(building.pb[m])
                        y   = -xt * np.sin(building.pb[m]) + yt  * np.cos(building.pb[m])
                        x2  = x2t * np.cos(building.pb[m]) + y2t * np.sin(building.pb[m])
                        y2  = 0
                        # Find R1,R2,TH1,TH2:
                        R1  = (     x**2 +      y**2)**0.5
                        R2  = ((x-x2)**2 + (y-y2)**2)**0.5
                        T1 = np.arctan2( ( y    ) , ( x    ) )
                        T2 = np.arctan2( ( y-y2 ) , ( x-x2 ) )

                    #for m in range(building.nop):
                        #R1 = ((XYZ1[m][0]-vehicle.position[0])**2 + (XYZ1[m][1]-vehicle.position[1])**2 )**0.5
                        #R2 = ((XYZ2[m][0]-vehicle.position[0])**2 + (XYZ2[m][1]-vehicle.position[1])**2 )**0.5
                        #T1 = np.arctan2((XYZ1[m][1]-vehicle.position[1]),(XYZ1[m][0]-vehicle.position[0])) + building.pb[m]
                        #T2 = np.arctan2((XYZ2[m][1]-vehicle.position[1]),(XYZ2[m][0]-vehicle.position[0])) + building.pb[m]

                        up = ( building.gammas[vehicle.ID][m]/(2*np.pi)) * np.log(R1/R2)
                        vp = ( building.gammas[vehicle.ID][m]/(2*np.pi)) * (T2-T1)
                        V_gamma[f,0] = V_gamma[f,0] + up * np.cos(building.pb[m]) + vp * np.sin(building.pb[m])
                        V_gamma[f,1] = V_gamma[f,1] - up * np.sin(building.pb[m]) + vp * np.cos(building.pb[m])      
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

        flow_vels[f,:] = [V_flow[f,0] + arenamap.wind[0]/(1.35*1.35), V_flow[f,1] + arenamap.wind[1]/(1.35*1.35), W_flow[f,0]] 

    return flow_vels
