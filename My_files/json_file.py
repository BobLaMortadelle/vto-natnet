import json
from djitellopy import Tello
import time
import os

# load the misson
file = open('Task1_handover.json')
command = json.load(file)
print(command)
# Connect to Tello (needs wifi connected to Tello already)
tello = Tello()
tello.connect()

# takeoff
tello.takeoff()

# travel waypoints
#tmp = [command['wayPoints'][0]['x'], command['wayPoints'][0]['y'], command['wayPoints'][0]['z'], command['wayPoints'][0]['theta']] # origin pose
for entry in range (len(command['wayPoints'])):
    x = command['wayPoints'][entry]['x']
    y = command['wayPoints'][entry]['y']
    z = command['wayPoints'][entry]['z']
    theta = command['wayPoints'][entry]['theta']
    v = command['velocity']

    #if(command['wayPoints'][entry]['x'] ==  tmp[0] and command['wayPoints'][entry]['y'] == tmp[1] and command['wayPoints'][entry]['z'] == tmp[2] and  command['wayPoints'][entry]['theta'] == tmp[3]):
    if(x ==  0 and y == 0 and z == 0 and  theta == 0):
        print("interaction in progress")
        time.sleep(10)
    else:
        print("order n°", entry)
        #tmp = [command['wayPoints'][entry]['x'], command['wayPoints'][entry]['y'], command['wayPoints'][entry]['z'], command['wayPoints'][entry]['theta']]
        if(x or y or z):
            tello.go_xyz_speed(x, y, z, v)
            #tello.fly_to_enu([float(x)/100, float(y)/100, float(z)/100], 0.)
        if(theta > 0):
            tello.rotate_clockwise(theta)

tello.land()
file.close()