#!/usr/bin/env python3
#
# Copyright (C) 2017 Gautier Hattenberger <gautier.hattenberger@enac.fr>
#
# This file is part of paparazzi.
#
# paparazzi is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# paparazzi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paparazzi; see the file COPYING.  If not, see
# <http://www.gnu.org/licenses/>.
#

'''
Forward rigid body position from NatNet (Optitrack positioning system)
to the IVY bus as a REMOTE_GPS_LOCAL message

As the NatNetClient is only compatible with Python 3.x, the Ivy python
should be installed for this version, eventually by hand as paparazzi
packages are only providing an install for Python 2.x (although the
source code itself is compatile for both version)

Manual installation of Ivy:
    1. git clone https://gitlab.com/ivybus/ivy-python.git
    2. cd ivy-python
    3. sudo python3 setup.py install
Otherwise, you can use PYTHONPATH if you don't want to install the code
in your system

'''


from __future__ import print_function

import sys
from os import path, getenv
from time import time, sleep
import numpy as np
from collections import deque
import argparse

# import NatNet client
from NatNetClient import NatNetClient


# For pybullet :
import pybullet as p
from time import sleep
import pybullet_data
import pdb
import numpy as np

# if PAPARAZZI_HOME not set, then assume the tree containing this
# file is a reasonable substitute
# PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
# sys.path.append(PPRZ_HOME + "/var/lib/python")
# from pprzlink.ivy import IvyMessagesInterface
# from pprzlink.message import PprzMessage

# start ivy interface
# if args.ivy_bus is not None:
#     ivy = IvyMessagesInterface("natnet2ivy", ivy_bus=args.ivy_bus)
# else:
#     ivy = IvyMessagesInterface("natnet2ivy")

class VolierePosition():
    def __init__(self, ac, vehicles, freq=20, server="127.0.0.1", dataport=int(1511), commandport=int(1510), vel_samples=int(4), verbose=False):
        self.freq = freq
        self.vel_samples = vel_samples
        self.vehicles = vehicles
        # dictionary of ID associations
        self.id_dict = dict(ac)
        # initial time per AC
        self.timestamp = dict([(ac_id, None) for ac_id in self.id_dict.keys()])
        self.period = 1. / self.freq
        # initial track per AC
        self.track = dict([(ac_id, deque()) for ac_id in self.id_dict.keys()])
        # start natnet interface
        self.natnet = NatNetClient(
                server=server,
                rigidBodyListListener=self.receiveRigidBodyList,
                dataPort=dataport,
                commandPort=commandport,
                verbose=verbose)

    def run(self):
        self.natnet.run()

    def stop(self):
        if self.natnet is not None:
            print("Shutting down NATNET ...")
            self.natnet.stop()
            self.natnet = None

    def __del__(self):
        self.stop()

        # store track function
    def store_track(self, ac_id, pos, t):
        if ac_id in self.id_dict.keys():
            self.track[ac_id].append((pos, t))
            if len(self.track[ac_id]) > self.vel_samples:
                self.track[ac_id].popleft()

    # compute velocity from track
    # returns zero if not enough samples
    def compute_velocity(self, ac_id):
        vel = [ 0., 0., 0. ]
        if len(self.track[ac_id]) >= self.vel_samples:
            nb = -1
            for (p2, t2) in self.track[ac_id]:
                nb = nb + 1
                if nb == 0:
                    p1 = p2
                    t1 = t2
                else:
                    dt = t2 - t1
                    if dt < 1e-5:
                        continue
                    vel[0] += (p2[0] - p1[0]) / dt
                    vel[1] += (p2[1] - p1[1]) / dt
                    vel[2] += (p2[2] - p1[2]) / dt
                    p1 = p2
                    t1 = t2
            if nb > 0:
                vel[0] /= nb
                vel[1] /= nb
                vel[2] /= nb
        return vel

    def receiveRigidBodyList(self, rigidBodyList, stamp):
        for (ac_id, pos, quat, valid) in rigidBodyList:
            if not valid:
                # skip if rigid body is not valid
                continue

            i = str(ac_id)
            # print(self.id_dict.keys())
            if i not in self.id_dict.keys():
                continue

            self.store_track(i, pos, stamp)
            if self.timestamp[i] is None or abs(stamp - self.timestamp[i]) < self.period:
                if self.timestamp[i] is None:
                    self.timestamp[i] = stamp
                continue # too early for next message
            self.timestamp[i] = stamp

            # msg = PprzMessage("datalink", "REMOTE_GPS_LOCAL")
            msg={}
            msg['ac_id'] = self.id_dict[i]
            msg['pad'] = 0
            msg['enu_x'] = pos[0]
            msg['enu_y'] = pos[1]
            msg['enu_z'] = pos[2]
            vel = self.compute_velocity(i)
            # msg['enu_xd'] = vel[0]
            # msg['enu_yd'] = vel[1]
            # msg['enu_zd'] = vel[2]
            # msg['tow'] = int(1000. * stamp) # TODO convert to GPS itow ?
            # convert quaternion to psi euler angle
            dcm_0_0 = 1.0 - 2.0 * (quat[1] * quat[1] + quat[2] * quat[2])
            dcm_1_0 = 2.0 * (quat[0] * quat[1] - quat[3] * quat[2])
            # msg['course']
            # heading = 180. * np.arctan2(dcm_1_0, dcm_0_0) / 3.14
            heading = np.arctan2(dcm_1_0, dcm_0_0)
            # print(msg['ac_id'], msg['enu_x'], msg['enu_y'], msg['enu_z'], heading)
            # print(quat)
            if self.vehicles != None:
                for _v in self.vehicles:
                    # print(_v.get_ac_id())
                    if _v.get_ac_id() == str(ac_id) : 
                        _v.set_position_enu(np.array([pos[0],pos[1],pos[2]]))
                        _v.set_velocity_enu(np.array([vel[0],vel[1],vel[2]]))
                        _v.set_heading(heading)
                        _v.set_quaternion(quat)
            # ivy.send(msg)

            # send GROUND_REF message if needed
            # if args.ground_ref:
                # gr = PprzMessage("ground", "GROUND_REF")
                # gr['ac_id'] = str(id_dict[i])
                # gr['frame'] = "LTP_ENU"
                # gr['pos'] = pos
                # gr['speed'] = vel
                # gr['quat'] = [quat[3], quat[0], quat[1], quat[2]]
                # gr['rate'] = [ 0., 0., 0. ]
                # gr['timestamp'] = stamp
                # ivy.send(gr)

class Vehicle():
    def __init__(self,ac_id):
        self.ac_id = ac_id
        self.position = np.zeros(3)
        self.velocity = np.zeros(3)
        self.heading = 0.
        self.quat = np.zeros(4)

    def get_ac_id(self):
        return self.ac_id
    def set_position_enu(self,pos):
        self.position = pos
    def set_velocity_enu(self,vel):
        self.velocity = vel
    def set_heading(self,heading):
        self.heading = heading
    def set_quaternion(self,quat):
        self.quat = quat

def main():
    # parse args
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-ac', action='append', nargs=2,
                        metavar=('rigid_id','ac_id'), help='pair of rigid body and A/C id (multiple possible)')
    parser.add_argument('-b', '--ivy_bus', dest='ivy_bus', help="Ivy bus address and port")
    parser.add_argument('-s', '--server', dest='server', default="127.0.0.1", help="NatNet server IP address")
    parser.add_argument('-m', '--multicast_addr', dest='multicast', default="239.255.42.99", help="NatNet server multicast address")
    parser.add_argument('-dp', '--data_port', dest='data_port', type=int, default=1511, help="NatNet server data socket UDP port")
    parser.add_argument('-cp', '--command_port', dest='command_port', type=int, default=1510, help="NatNet server command socket UDP port")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help="display debug messages")
    parser.add_argument('-f', '--freq', dest='freq', default=20, type=int, help="transmit frequency")
    # parser.add_argument('-gr', '--ground_ref', dest='ground_ref', action='store_true', help="also send the GROUND_REF message")
    parser.add_argument('-vs', '--vel_samples', dest='vel_samples', default=4, type=int, help="amount of samples to compute velocity (should be greater than 2)")
    args = parser.parse_args()

    if args.ac is None:
        print("At least one pair of rigid body / AC id must be declared")
        exit()
    print(args.ac[0][1])

    vehicles = [Vehicle(ac_id[1]) for ac_id in args.ac]
    voliere = VolierePosition(args.ac, vehicles)


    #==============
    physicsClient = p.connect(p.GUI)

    p.setAdditionalSearchPath(pybullet_data.getDataPath())

    p.setGravity(0, 0, -10)
    planeId = p.loadURDF("plane.urdf")
    textureId = p.loadTexture("checker_grid.jpg")

    vehicleStartPos = [0, 0, 0]
    vehicleStartOrientation = p.getQuaternionFromEuler([0, 0, 0])

    # servo1Id = p.addUserDebugParameter("serv1", -1.5, 1.5, 0)
    # servo2Id = p.addUserDebugParameter("serv2", -1.5, 1.5, 0)

    #boxId = p.loadURDF("r2d2.urdf", cubeStartPos, cubeStartOrientation)
    #boxId = p.loadURDF("cartpole.urdf", cubeStartPos, cubeStartOrientation)
    #boxId = p.loadURDF("pole.urdf", cubeStartPos, cubeStartOrientation)
    # vehicle = p.loadURDF("hexarotor.urdf", vehicleStartPos, vehicleStartOrientation)
    vehicle = p.loadURDF("quadrotor.urdf", vehicleStartPos, vehicleStartOrientation)
    p.resetDebugVisualizerCamera( cameraDistance=6.5, cameraYaw=0, cameraPitch=-40, cameraTargetPosition=[0.0, 0.0, 0.0])
    # v_Pos, v_cubeOrn = p.getBasePositionAndOrientation(vehicle)
    #==============

    print("Starting Natnet3.x to Ivy interface at %s" % (args.server))
    try:
        # Start up the streaming client.
        # This will run perpetually, and operate on a separate thread.
        voliere.run()
        sleep(1)
        while True:
            # print(vehicles[0].position)
            # rpy=[0.,0.,0.]
            # p.getQuaternionFromEuler(rpy)
            p.resetBasePositionAndOrientation(vehicle,
                                            vehicles[0].position,
                                            vehicles[0].quat,
                                            physicsClientId=physicsClient)
            sleep(0.01)

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        voliere.stop()
        p.disconnect(physicsClientId=physicsClient)
        # ivy.shutdown()
    except OSError:
        print("Natnet connection error")
        voliere.stop()
        # ivy.stop()
        exit(-1)

if __name__=="__main__":
    main()
