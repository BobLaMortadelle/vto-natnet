#!/usr/bin/env python3

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

Problem :
=========

common/NatNetClient.py", line 489, in __unpack_marker_set_data
    trace_mf( "Model Name      : ", model_name.decode( 'utf-8' ) )
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x91 in position 0: invalid start byte


'''


from __future__ import print_function

import sys
from os import path, getenv
from time import time, sleep
import numpy as np
from collections import deque
import argparse

# import NatNet client
import sys
sys.path.insert(0,"../common")
from natnet import NatNetClient, DataFrame

# For pybullet :
import pybullet as p
from time import sleep
# import pybullet_data
import pdb
import numpy as np
import time

import requests

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

class Quaternion:
    def __init__(self, x, y, z, w):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other):
        w1, x1, y1, z1 = self.w, self.x, self.y, self.z
        w2, x2, y2, z2 = other.w, other.x, other.y, other.z
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
        z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
        return Quaternion(x, y, z, w)

    def conjugate(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)

    def to_angle_axis(self):
        # Normalize the quaternion if it's not already normalized
        if not np.isclose(self.magnitude(), 1):
            normalized_quat = self.normalize()
            w = normalized_quat.w
            x = normalized_quat.x
            y = normalized_quat.y
            z = normalized_quat.z
        else:
            w = self.w
            x = self.x
            y = self.y
            z = self.z

        angle = 2 * np.arccos(w)
        axis = [x, y, z] / np.sin(angle / 2)
        return angle, axis
    
    def to_euler(self): # NOT TESTED WELL
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (self.w * self.x + self.y * self.z)
        cosr_cosp = 1 - 2 * (self.x**2 + self.y**2)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2 * (self.w * self.y - self.z * self.x)
        if np.abs(sinp) >= 1:
            # Use 90 degrees if out of range
            pitch = np.sign(sinp) * np.pi / 2
        else:
            pitch = np.arcsin(sinp)

        # Yaw (z-axis rotation)
        siny_cosp = 2 * (self.w * self.z + self.x * self.y)
        cosy_cosp = 1 - 2 * (self.y**2 + self.z**2)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        return roll, pitch, yaw
    
    def to_rotation_matrix(self):
        """Convert the quaternion to a rotation matrix."""
        return np.array([
            [1 - 2*(self.y**2 + self.z**2),     2*(self.x*self.y - self.w*self.z), 2*(self.x*self.z + self.w*self.y)],
            [    2*(self.x*self.y + self.w*self.z), 1 - 2*(self.x**2 + self.z**2),     2*(self.y*self.z - self.w*self.x)],
            [    2*(self.x*self.z - self.w*self.y),     2*(self.y*self.z + self.w*self.x), 1 - 2*(self.x**2 + self.y**2)]
        ])
    
    def magnitude(self):
        return np.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        mag = self.magnitude()
        return Quaternion(self.x/mag, self.y/mag, self.z/mag, self.w/mag)

    def inverse(self):
        mag_sq = self.magnitude() ** 2
        return Quaternion(-self.x/mag_sq, -self.y/mag_sq, -self.z/mag_sq, self.w/mag_sq)

    def dot(self, other):
        return self.w*other.w + self.x*other.x + self.y*other.y + self.z*other.z
    
    def rotate_vector(self, v):
        qv = Quaternion(v[0], v[1], v[2], 0)
        qv_rot = self * qv * self.conjugate()
        return [qv_rot.x, qv_rot.y, qv_rot.z]

#------------------------------------------------------------------------------
class Rigidbody():
  def __init__(self,ac_id):
    self.ac_id = ac_id
    self.valid = False
    self.position = np.zeros(3)
    self.velocity = np.zeros(3)
    self.heading = 0.
    self.quat = np.zeros(4)

#------------------------------------------------------------------------------


def store_track(ac_id, pos, t):
  if ac_id in id_dict.keys():
    track[ac_id].append((pos, t))
    if len(track[ac_id]) > vel_samples:
      track[ac_id].popleft()

def compute_velocity(ac_id):
  vel = [ 0., 0., 0. ]
  if len(track[ac_id]) >= vel_samples:
    nb = -1
    for (p2, t2) in track[ac_id]:
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



class VolierePosition():
    def __init__(self, ac, vehicles, freq=20, server="192.168.10.132", dataport=int(1511), commandport=int(1510), vel_samples=int(4), verbose=False):
        self.freq = freq
        self.vel_samples = vel_samples
        self.vehicles = vehicles
        # rgbs = dict([(ac_id, Rigidbody(ac_id)) for ac_id in id_dict.keys()])
        # dictionary of ID associations
        self.id_dict = dict(ac)
        # initial time per AC
        self.timestamp = dict([(ac_id, None) for ac_id in self.id_dict.keys()])

        self.period = 1. / self.freq
        # initial track per AC
        self.track = dict([(ac_id, deque(maxlen=self.vel_samples)) for ac_id in self.id_dict.keys()])
        # initial quaternion track per AC
        self.quaternion_track = dict([(ac_id, deque(maxlen=self.vel_samples)) for ac_id in self.id_dict.keys()])

        self.streaming_client = NatNetClient(
            server_ip_address="192.168.10.132", # make sure to use correct optitrack (Motiv) ip and set it in the streaming pane of Motiv
            local_ip_address="192.168.10.197",  # make sure to use correct local ip
            use_multicast=True,
            multicast_address="224.0.0.1"       # make sure to use correct multicast address (as defined in Motiv)
        )
        self.streaming_client.connect()

        # Register callbacks
        # self.streaming_client.on_data_description_received_event.handlers.append(
        #     self._on_data_description
        # )
        self.streaming_client.on_data_frame_received_event.handlers.append(
            self.receiveRigidBodyMarkerSetList
        )


        # start natnet interface
        # self.natnet = NatNetClient()
        # self.natnet.set_server_address(server)
        # self.natnet.set_client_address('192.168.10.197')
        # self.natnet.set_print_level(1)  # 1 to print all frames
        # self.natnet.rigid_body_marker_set_list_listener = self.receiveRigidBodyMarkerSetList
        # self.natnet = NatNetClient(
        #         server=server,
        #         rigidBodyListListener=self.receiveRigidBodyList,
        #         dataPort=dataport,
        #         commandPort=commandport,
        #         verbose=verbose)
        # start natnet interface with new NatNet Class
        # self.natnet = NatNetClient()
        # self.natnet.rigidBodyListListener = self.receiveRigidBodyList

        self.last_time_processed = time.time()
  
    def receiveRigidBodyMarkerSetList(self, data_frame: DataFrame):

        if time.time() - self.last_time_processed < (1.0 / 30): 
            return
        
        self.last_time_processed = time.time()

        stamp = data_frame.suffix.timestamp

        for rigid_body in data_frame.rigid_bodies:

            if not rigid_body.tracking_valid:
                # skip if rigid body is not valid
                continue
            i = str(rigid_body.id_num)
            if i not in self.id_dict.keys():
                continue
            pos = rigid_body.pos
            quat = rigid_body.rot
            self.store_track(i, pos, stamp)
            self.store_quaternion_track(i, Quaternion(quat[0],quat[1],quat[2],quat[3]), stamp)

            if self.timestamp[i] is None or abs(stamp - self.timestamp[i]) < self.period:
                if self.timestamp[i] is None:
                    self.timestamp[i] = stamp
                continue # too early for next message
            self.timestamp[i] = stamp
            vel = self.compute_velocity(i)
            ang_vel = self.compute_angular_velocity(i)
            dcm_0_0 = 1.0 - 2.0 * (quat[1] * quat[1] + quat[2] * quat[2])
            dcm_1_0 = 2.0 * (quat[0] * quat[1] - quat[3] * quat[2])
            self.vehicles[i].set_position_enu(np.array([pos[0],pos[1],pos[2]]))
            self.vehicles[i].set_velocity_enu(np.array([vel[0],vel[1],vel[2]]))
            self.vehicles[i].set_heading(np.arctan2(dcm_1_0, dcm_0_0))
            self.vehicles[i].set_quaternion(quat)
            self.vehicles[i].set_angular_velocity(np.array(ang_vel))
            self.vehicles[i].valid = True
            # print(i,pos)
    
    def run(self):
        # self.natnet.run()
        is_running = True
        self.streaming_client.run_async()
        sleep(1)
        if not is_running:
            print("Natnet error: Could not start streaming client.")
            exit(-1)
        if not self.streaming_client.connected:
            print("Natnet error: Fail to connect to natnet")
            exit(-1)

    def stop(self):
        if self.streaming_client is not None:
            print("Shutting down NATNET ...")
            self.streaming_client.shutdown()
            self.streaming_client = None

    def __del__(self):
        self.stop()

    # store track function
    def store_track(self, ac_id, pos, t):
        if ac_id in self.id_dict.keys():
            self.track[ac_id].append((pos, t))
            # The below may not be needed as we have added maxlen to deque ... ???
            if len(self.track[ac_id]) > self.vel_samples:
                self.track[ac_id].popleft()

    def store_quaternion_track(self, ac_id, quat, t):
        if ac_id in self.id_dict.keys():
            self.quaternion_track[ac_id].append((quat, t))
            # The below may not be needed as we have added maxlen to deque ... ???
            if len(self.quaternion_track[ac_id]) > self.vel_samples:
                self.quaternion_track[ac_id].popleft()

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

    def compute_velocity_fast(self, ac_id):
        if len(self.track[ac_id]) < self.vel_samples:
            return [0., 0., 0.]

        vel = np.array([0., 0., 0.])
        nb = 0
        p1, t1 = self.track[ac_id][0]

        for p2, t2 in list(self.track[ac_id])[1:]:
            dt = t2 - t1
            if dt >= 1e-5:
                vel += (np.array(p2) - np.array(p1)) / dt
                nb += 1
            p1, t1 = p2, t2

        if nb > 0:
            vel /= nb

        return list(vel)
    
    # def compute_angular_velocity(self, ac_id):
    #     if len(self.quaternion_track[ac_id]) < self.vel_samples:
    #         return [0., 0., 0.]

    #     ang_vel = np.array([0., 0., 0.])
    #     nb = 0
    #     q1, t1 = self.quaternion_track[ac_id][0]

    #     for q2, t2 in list(self.quaternion_track[ac_id])[1:]:
    #         dt = t2 - t1
    #         if dt >= 1e-5:
    #             dq = q2 * q1.conjugate()
    #             angle, axis = dq.to_angle_axis()
    #             ang_vel += (axis * angle) / dt
    #             nb += 1
    #         q1, t1 = q2, t2

    #     if nb > 0:
    #         ang_vel /= nb

    #     return list(ang_vel)

    def compute_angular_velocity(self, ac_id):
        if len(self.quaternion_track[ac_id]) < self.vel_samples:
            return [0., 0., 0.]

        ang_vel = np.array([0., 0., 0.])
        nb = 0
        q1, t1 = self.quaternion_track[ac_id][0]

        for q2, t2 in list(self.quaternion_track[ac_id])[1:]:
            dt = t2 - t1
            if dt >= 1e-5:
                dq = q2 * q1.conjugate()
                angle, axis = dq.to_angle_axis()

                # Check if the angle is very small
                if np.isclose(angle, 0):
                    ang_vel += np.array([0., 0., 0.])
                else:
                    ang_vel += (axis * angle) / (dt + 1e-8)  # Add a small constant to dt

                nb += 1
            q1, t1 = q2, t2

        if nb > 0:
            ang_vel /= nb

        # Rotate the angular velocity to the body frame
        q = self.quaternion_track[ac_id][-1][0]  # Get the latest quaternion

        #1 ang_vel_body = q.rotate_vector(ang_vel)

        #2 (roll, pitch, yaw) = q.to_euler()

        # # Transformation matrix for Tait-Bryan angles
        # W = np.array([
        #     [1, np.sin(roll)*np.tan(pitch), np.cos(roll)*np.tan(pitch)],
        #     [0, np.cos(roll), -np.sin(roll)],
        #     [0, np.sin(roll)/np.cos(pitch), np.cos(roll)/np.cos(pitch)]
        # ])

        # # Multiply the angular velocities by the inverse of the transformation matrix
        # ang_vel_body = np.linalg.inv(W) @ ang_vel

        #3 Convert the quaternion to a rotation matrix
        # R = q.to_rotation_matrix()

        # # Multiply the angular velocities by the rotation matrix
        # ang_vel_body = R @ ang_vel

        #4
        R = np.array(p.getMatrixFromQuaternion([q.x, q.y, q.z, q.w])).reshape(3, 3)
        ang_vel_body = R.T.dot(ang_vel)
        
        if np.any(np.isnan(ang_vel_body)):
            return [0., 0., 0.]

        return list(ang_vel_body) # list(ang_vel)
    
    # def receiveRigidBodyList(self, rigidBodyList, stamp):
    #     for (ac_id, pos, quat, valid) in rigidBodyList:
    #         if not valid:
    #             # skip if rigid body is not valid
    #             continue

    #         i = str(ac_id)
    #         # print(self.id_dict.keys())
    #         if i not in self.id_dict.keys():
    #             continue

    #         self.store_track(i, pos, stamp)
    #         self.store_quaternion_track(i, Quaternion(quat[0],quat[1],quat[2],quat[3]), stamp)
    #         if self.timestamp[i] is None or abs(stamp - self.timestamp[i]) < self.period:
    #             if self.timestamp[i] is None:
    #                 self.timestamp[i] = stamp
    #             continue # too early for next message
    #         self.timestamp[i] = stamp

    #         # msg = PprzMessage("datalink", "REMOTE_GPS_LOCAL")
    #         msg={}
    #         msg['ac_id'] = self.id_dict[i]
    #         msg['pad'] = 0
    #         msg['enu_x'] = pos[0]
    #         msg['enu_y'] = pos[1]
    #         msg['enu_z'] = pos[2]
    #         vel = self.compute_velocity(i)
    #         ang_vel = self.compute_angular_velocity(i)
    #         # msg['enu_xd'] = vel[0]
    #         # msg['enu_yd'] = vel[1]
    #         # msg['enu_zd'] = vel[2]
    #         # msg['tow'] = int(1000. * stamp) # TODO convert to GPS itow ?
    #         # convert quaternion to psi euler angle
    #         dcm_0_0 = 1.0 - 2.0 * (quat[1] * quat[1] + quat[2] * quat[2])
    #         dcm_1_0 = 2.0 * (quat[0] * quat[1] - quat[3] * quat[2])
    #         # msg['course']
    #         # heading = 180. * np.arctan2(dcm_1_0, dcm_0_0) / 3.14
    #         heading = np.arctan2(dcm_1_0, dcm_0_0)
    #         # print(msg['ac_id'], msg['enu_x'], msg['enu_y'], msg['enu_z'], heading)
    #         # print(quat)
    #         if self.vehicles != None:
    #             for _v in self.vehicles:
    #                 # print(_v.get_ac_id())
    #                 if _v.get_ac_id() == str(ac_id) : 
    #                     _v.set_position_enu(np.array([pos[0],pos[1],pos[2]]))
    #                     _v.set_velocity_enu(np.array([vel[0],vel[1],vel[2]]))
    #                     _v.set_heading(heading)
    #                     _v.set_quaternion(quat)
    #                     _v.set_angular_velocity(np.array(ang_vel))

    #                     payload = {str(ac_id) : {'position_ENU': pos, 
    #                                         'velocity_ENU': vel,
    #                                         'quaternion' : quat,
    #                                         'angular_vel_body' : ang_vel,
    #                                         }
    #                     }
                        #r = requests.post('http://127.0.0.1:5600/vehicle', json=payload)
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
    def __init__(self,ac_id, commander=None):
        self.ac_id = ac_id
        self.valid = False
        self.commander = commander
        self.position = np.zeros(3)
        self.velocity = np.zeros(3)
        self.ang_vel = np.zeros(3)
        self.heading = 0.
        self.quat = np.zeros(4)
        self.state = 0 # DISARMED

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
    def set_angular_velocity(self,ang_vel):
        self.ang_vel = ang_vel

class TrackTarget(Vehicle):
    def __init__(self, ac_id):
        super().__init__(ac_id)
        self.target_found = False
        self.height_engaged = False
        self.position_tolerance = 0.1
        self.last_position = np.array([0,0,0])
        self.target_position = np.array([0,0,0])

    def check_height(self):
        if self.position[2] > 2:
            self.height_engaged = True
        else:
            self.height_engaged = False

    def identify_target(self):
        self.check_height()
        cur_position = self.position
        ini_position = self.last_position
        position_distance = np.sqrt((cur_position[0]-ini_position[0]) **2
                             + (cur_position[1]-ini_position[1]) **2
                             + (cur_position[2]-ini_position[2]) **2)
        if position_distance < self.position_tolerance and self.height_engaged:
            self.target_found = True
            self.target_position = cur_position
        self.last_position = cur_position
        return
        
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
        # exit()
    # print(args.ac[0][1])

    # Initialize lists to store data
    positions = []
    velocities = []
    angular_velocities = []

    id_dict = dict([('888','888'),('882', '882'),('889', '889'),('881', '881'),('68','68'),('69','69'),('333','333'), ('244','244'), ('245', '245'), ('221', '221')]) # rigidbody_ID, aircraft_ID
    # freq = 10
    # vel_samples = 20

    vehicles = dict([(ac_id, Vehicle(ac_id)) for ac_id in id_dict.keys()])
    # print(id_dict.keys(), vehicles['0'].get_ac_id())
    # vehicles = [Vehicle(ac_id[1]) for ac_id in args.ac]
    voliere = VolierePosition(id_dict, vehicles, freq=200, vel_samples=6)
    # voliere = VolierePosition(args.ac, vehicles, freq=200, vel_samples=6)


    #==============
    # physicsClient = p.connect(p.GUI)

    # p.setAdditionalSearchPath(pybullet_data.getDataPath())

    # p.setGravity(0, 0, -10)
    # planeId = p.loadURDF("plane.urdf")
    # textureId = p.loadTexture("checker_grid.jpg")

    # vehicleStartPos = [0, 0, 0]
    # vehicleStartOrientation = p.getQuaternionFromEuler([0, 0, 0])

    # servo1Id = p.addUserDebugParameter("serv1", -1.5, 1.5, 0)
    # servo2Id = p.addUserDebugParameter("serv2", -1.5, 1.5, 0)

    #boxId = p.loadURDF("r2d2.urdf", cubeStartPos, cubeStartOrientation)
    #boxId = p.loadURDF("cartpole.urdf", cubeStartPos, cubeStartOrientation)
    #boxId = p.loadURDF("pole.urdf", cubeStartPos, cubeStartOrientation)
    # vehicle = p.loadURDF("hexarotor.urdf", vehicleStartPos, vehicleStartOrientation)
    # vehicle = p.loadURDF("duck_vhacd.urdf", vehicleStartPos, vehicleStartOrientation)
    # p.resetDebugVisualizerCamera( cameraDistance=6.5, cameraYaw=0, cameraPitch=-40, cameraTargetPosition=[0.0, 0.0, 0.0])
    # v_Pos, v_cubeOrn = p.getBasePositionAndOrientation(vehicle)
    #==============

    print("Starting Natnet3.x to Ivy interface at %s" % (args.server))
    try:
        # Start up the streaming client.
        # This will run perpetually, and operate on a separate thread.
        voliere.run()
        # already_up = False
        while True:
            # if(voliere.vehicles['245'].position[2] > voliere.vehicles['888'].position[2] and not already_up):
            #     print('rise hand up at pos', voliere.vehicles['245'].position)
            #     already_up = True
                
            
            print(voliere.vehicles['221'].position)
            # Record data
            # positions.append(vehicles[0].position)
            # velocities.append(vehicles[0].velocity)
            # angular_velocities.append(vehicles[0].ang_vel)

            # rpy=[0.,0.,0.]
            # p.getQuaternionFromEuler(rpy)

            # p.resetBasePositionAndOrientation(vehicle,
            #                                 vehicles[0].position,
            #                                 vehicles[0].quat,
            #                                 physicsClientId=physicsClient)
            sleep(0.01)

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        voliere.stop()
        # plot_results(positions, velocities, angular_velocities)
        # p.disconnect(physicsClientId=physicsClient)
        # ivy.shutdown()
    except OSError:
        print("Natnet connection error")
        voliere.stop()
        # ivy.stop()
        exit(-1)

def plot_results(positions, velocities, angular_velocities):
    import matplotlib.pyplot as plt
    # Plot data
    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.plot(positions)
    plt.title('Position')

    plt.subplot(3, 1, 2)
    plt.plot(velocities)
    plt.title('Velocity')

    plt.subplot(3, 1, 3)
    plt.plot(angular_velocities)
    plt.title('Angular Velocity')

    plt.tight_layout()
    plt.show()

if __name__=="__main__":
    main()

# /home/b0b/vto-natnet_1.1/vto-natnet/without_ivy/voliere.py:102: RuntimeWarning: invalid value encountered in arccos
#   angle = 2 * np.arccos(w