from __future__ import print_function # Python 2/3 compatibility
from time import sleep
import time
from djitellopy import Tello
import pdb
import numpy as np
import json
import math
import cv2
import threading
from aruco_detect import ArucoSquare
from scipy.spatial.transform import Rotation as R

# Side length of the ArUco marker in meters 
aruco_marker_side_length = 0.0952
 
# Calibration parameters yaml file
camera_calibration_parameters_filename = 'calibration_chessboard.yaml'
 

# To signal readiness of video stream
stream_ready = threading.Event()

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

def stream_video(tello):
    # Load the camera parameters from the saved file
    cv_file = cv2.FileStorage(
    camera_calibration_parameters_filename, cv2.FILE_STORAGE_READ) 
    mtx = cv_file.getNode('K').mat()
    dst = cv_file.getNode('D').mat()
    cv_file.release()
    aruco_detector = ArucoSquare()
    # Simulation starts
    sim_start_time = time.time()
    starttime= time.time()
    while True:
        # Limite the experience to 4 minutes
        if time.time()-sim_start_time > 240:
            print("Experience exceed expected time.")
            break
        if ((time.time()-starttime > 0.05)):
            # Start displaying the drone camera frames
            frame = tello.get_frame_read().frame 
            cv2.imshow("Drone Cam", frame)
            
            if not stream_ready.is_set():
                stream_ready.set()
                #searching.set()
                
                #print('Event: stream is Live')

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Operation manually terminated.")
                break

            # Detect Aruco markers
            corners, ids = aruco_detector.find_aruco_markers(frame)
            if ids is not None:
                # Get the rotation and translation vectors
                rvecs, tvecs, obj_points = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                aruco_marker_side_length,
                mtx,
                dst)

                for i, id in enumerate(ids):
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

                    if id == 0 :
                        # searching.clear()
                        # spotting.set()
                        print('Event: victim detected')
                        print("Human found")
                        print("transform_translation_x: {}".format(transform_translation_x))
                        print("transform_translation_y: {}".format(transform_translation_y))
                        print("transform_translation_z: {}".format(transform_translation_z))
                        print("roll_x: {}".format(roll_x))
                        print("pitch_y: {}".format(pitch_y))
                        print("yaw_z: {}".format(yaw_z))
                        print()

            starttime= time.time()
    cv2.destroyAllWindows()


def fly(tello):
    stream_ready.wait()
    tello.turn_motor_on()
    counter = 0
    while True:
        counter += 1
        #print(".")


        
def main():
    # Connect to the drone
    tello = Tello()
    tello.connect()
    
    #switch on camera
    tello.streamon()
    #tello.set_video_direction(1)
    print('cam switched on')
    stream_thread = threading.Thread(target=stream_video, args=(tello,))
    stream_thread.daemon = True
    stream_thread.start()
    print('stream running')

    try:
        fly(tello)
    except (KeyboardInterrupt, SystemExit):
        tello.turn_motor_off()
        tello.send_expansion_command("mled sc")
        tello.send_expansion_command("led 0 0 0")





if __name__=="__main__":
    main()