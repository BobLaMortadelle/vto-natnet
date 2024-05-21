from djitellopy import Tello
import time
import json
import cv2
import cv2.aruco as aruco
import numpy as np
import math


# def get_norm(origin, goal):
#     return math.sqrt((origin[1] - goal[1])**2 + (origin[2] - goal[2])**2)


# def new_vector(norm, heading, z):
#     newX = '{:.2f}'.format(norm * math.cos(heading))
#     newY = '{:.2f}'.format(norm * math.sin(heading))
#     return np.array([newX, newY, z])

# # load the misson
# file = open('task1_without_voliere.json')
# command = json.load(file)
# print(command)


# lengthWPs = len(command['wayPoints'])
# wPListPosABS = np.zeros((lengthWPs, 3))
# wPListHeadingABS = np.zeros((lengthWPs, 1))
# for i in range (lengthWPs):
#     x = command['wayPoints'][i]['x']
#     y = command['wayPoints'][i]['y']
#     z = command['wayPoints'][i]['z']
#     theta = command['wayPoints'][i]['theta']
    
#     #v = command['velocity']
#     wPListPosABS[i] = np.array([x, y, z])
#     wPListHeadingABS[i] = None if theta == None else 2 * math.pi * theta / 360  # conversion from degrees to rad
    

# print(wPListPosABS)
# print("\n")
# print(wPListHeadingABS)
# print("\n")

# WPListWithoutAviary = np.zeros((lengthWPs+1, 3))
# WPListWithoutAviary[0] = wPListPosABS[0]

# HeadingListWithoutAviary = np.zeros((lengthWPs+1, 1))
# HeadingListWithoutAviary[0] = wPListHeadingABS[0]

# DistanceToNextPointList = np.zeros((lengthWPs+1, 3))
# DistanceToNextPointList[0] = new_vector(get_norm(np.zeros(3), WPListWithoutAviary[0]), HeadingListWithoutAviary[0][0], WPListWithoutAviary[0][2])

# new_path = np.zeros((lengthWPs+1, 3))


# for i in range (1, lengthWPs):
#     WPListWithoutAviary[i] = wPListPosABS[i] - wPListPosABS[i-1]
#     HeadingListWithoutAviary[i] = wPListHeadingABS[i] - wPListHeadingABS[i-1]
#     # norm = get_norm(WPListWithoutAviary[i-1], WPListWithoutAviary[i])
#     # new_path[i] = new_vector(norm, HeadingListWithoutAviary[i], WPListWithoutAviary[i][2])
#     #DistanceToNextPointList[i] = new_vector(get_norm(WPListWithoutAviary[i-1], WPListWithoutAviary[i]),HeadingListWithoutAviary[i], WPListWithoutAviary[i][2])
# print(WPListWithoutAviary)
# print("\n")
# print(HeadingListWithoutAviary)
# print("\n")
# print(new_path)



# load the misson
file = open('task1_without_voliere.json')
command = json.load(file)
print(command)


lengthWPs = len(command['wayPoints'])
wPListPosABS = np.zeros((lengthWPs, 3))
wPListHeadingABS = np.zeros((lengthWPs, 1))
velocity = command['velocity']
print(velocity)
for i in range (lengthWPs):
    x = command['wayPoints'][i]['x']
    y = command['wayPoints'][i]['y']
    z = command['wayPoints'][i]['z']
    theta = command['wayPoints'][i]['theta']
    
    #v = command['velocity']
    wPListPosABS[i] = np.array([x, y, z])
    wPListHeadingABS[i] = None if theta == None else theta  # conversion from degrees to rad
print("path planning:", wPListPosABS, wPListHeadingABS)


#     # Connect to Tello (needs wifi connected to Tello already)
tello = Tello()
tello.connect()

tello.takeoff()

for i in range(lengthWPs):
    print("rank = ", i)
    displacementx = 100 * wPListPosABS[i][0]
    displacementz = 100 * wPListPosABS[i][2]
    
    tello.go_xyz_speed(displacementx, 0, displacementz, velocity)

    # if(wPListPosABS[i][2] > 0):
    #     tello.move_up(displacementz)
    # elif(wPListPosABS[i][2] < 0):
    #     tello.move_down(displacementz)
    # print(displacementz)

    # if(wPListPosABS[i][0] > 0):
    #     tello.move_forward(displacementx)
    # elif(wPListPosABS[i][0] < 0):
    #     tello.move_back(displacementx)
    # print(displacementx)


    if(wPListHeadingABS[i]>0):
        tello.rotate_clockwise(wPListHeadingABS[i][0])
    elif(wPListHeadingABS[i]<0):
        tello.rotate_counter_clockwise(wPListHeadingABS[i][0])
    print(wPListHeadingABS[i][0])
    
tello.land()