#!/usr/bin/env python
  
'''
Welcome to the ArUco Marker Pose Estimator!
  
This program:
  - Estimates the pose of an ArUco Marker
'''
  
from __future__ import print_function # Python 2/3 compatibility
import cv2 # Import the OpenCV library
import numpy as np # Import Numpy library
from scipy.spatial.transform import Rotation as R
import math # Math library
from djitellopy import Tello
import cv2.aruco as aruco
import time

 
# Project: ArUco Marker Pose Estimator
# Date created: 12/21/2021
# Python version: 3.8
 
# Side length of the ArUco marker in meters 
aruco_marker_side_length = 0.0952
 
# Calibration parameters yaml file
camera_calibration_parameters_filename = 'calibration_chessboard.yaml'
 
def euler_from_quaternion(x, y, z, w):
  """
  Convert a quaternion into euler angles (roll, pitch, yaw)
  roll is rotation around x in radians (counterclockwise)
  pitch is rotation around y in radians (counterclockwise)
  yaw is rotation around z in radians (counterclockwise)
  """
  t0 = +2.0 * (w * x + y * z)
  t1 = +1.0 - 2.0 * (x * x + y * y)
  roll_x = math.atan2(t0, t1)
      
  t2 = +2.0 * (w * y - z * x)
  t2 = +1.0 if t2 > +1.0 else t2
  t2 = -1.0 if t2 < -1.0 else t2
  pitch_y = math.asin(t2)
      
  t3 = +2.0 * (w * z + x * y)
  t4 = +1.0 - 2.0 * (y * y + z * z)
  yaw_z = math.atan2(t3, t4)
      
  return roll_x, pitch_y, yaw_z # in radians
 
def main():
    """
    Main method of the program.
    """
    tello = Tello()
    tello.connect()
    tello.turn_motor_on()
    tello.streamon()
    time.sleep(3)


    # Load the camera parameters from the saved file
    cv_file = cv2.FileStorage(
    camera_calibration_parameters_filename, cv2.FILE_STORAGE_READ) 
    mtx = cv_file.getNode('K').mat()
    dst = cv_file.getNode('D').mat()
    cv_file.release()
        
    # Load the ArUco dictionary
    this_aruco_dictionary = aruco.getPredefinedDictionary(getattr(aruco, "DICT_4X4_50"))
    this_aruco_parameters = aruco.DetectorParameters()

    #   # Start the video stream
    #   cap = cv2.VideoCapture(0)
    starttime= time.time()
    while(True):

    # Capture frame-by-frame
    # This method returns True/False as well
    # as the video frame.
        if (time.time()-starttime > 0.1):
            frame = tello.get_frame_read().frame 
            cv2.imshow("Drone Cam", frame)
            # Detect ArUco markers in the video frame
            (corners, marker_ids, rejected) = aruco.detectMarkers(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), this_aruco_dictionary, parameters=this_aruco_parameters)
            
            # Check that at least one ArUco marker was detected
            if marker_ids is not None:

                # Draw a square around detected markers in the video frame
                aruco.drawDetectedMarkers(frame, corners, marker_ids)
                
                # Get the rotation and translation vectors
                rvecs, tvecs, obj_points = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                aruco_marker_side_length,
                mtx,
                dst)
                    
                # Print the pose for the ArUco marker
                # The pose of the marker is with respect to the camera lens frame.
                # Imagine you are looking through the camera viewfinder, 
                # the camera lens frame's:
                # x-axis points to the right
                # y-axis points straight down towards your toes
                # z-axis points straight ahead away from your eye, out of the camera
                for i, marker_id in enumerate(marker_ids):
                
                    # Store the translation (i.e. position) information
                    transform_translation_x = tvecs[i][0][0]
                    transform_translation_y = tvecs[i][0][1]
                    transform_translation_z = tvecs[i][0][2]
            
                    # Store the rotation information
                    rotation_matrix = np.eye(4)
                    rotation_matrix[0:3, 0:3] = cv2.Rodrigues(np.array(rvecs[i][0]))[0]
                    r = R.from_matrix(rotation_matrix[0:3, 0:3])
                    quat = r.as_quat()   
                    
                    # Quaternion format     
                    transform_rotation_x = quat[0] 
                    transform_rotation_y = quat[1] 
                    transform_rotation_z = quat[2] 
                    transform_rotation_w = quat[3] 
                    
                    # Euler angle format in radians
                    roll_x, pitch_y, yaw_z = euler_from_quaternion(transform_rotation_x, 
                                                                transform_rotation_y, 
                                                                transform_rotation_z, 
                                                                transform_rotation_w)
                    
                    roll_x = math.degrees(roll_x)
                    pitch_y = math.degrees(pitch_y)
                    yaw_z = math.degrees(yaw_z)
                    print("transform_translation_x: {}".format(transform_translation_x))
                    print("transform_translation_y: {}".format(transform_translation_y))
                    print("transform_translation_z: {}".format(transform_translation_z))
                    print("roll_x: {}".format(roll_x))
                    print("pitch_y: {}".format(pitch_y))
                    print("yaw_z: {}".format(yaw_z))
                    print()
                    
                    # # Draw the axes on the marker
                    # aruco.drawDetectedMarkers(frame, corners, marker_ids)
                    
                # If "q" is pressed on the keyboard, 
                # exit this loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            starttime= time.time()
        # Close down the video stream
        #   cap.release()
    cv2.destroyAllWindows()
    tello.turn_motor_off()
    tello.reboot()
   
if __name__ == '__main__':
  print(__doc__)
  main()