from djitellopy import Tello
import time 
import cv2
import cv2.aruco as aruco


class ArucoSquare:

    def __init__(self, marker_size=4, nb_markers=50, draw=True):
        self.marker_size = marker_size
        self.nb_markers = nb_markers
        self.aruco_dict = aruco.getPredefinedDictionary(getattr(aruco, f'DICT_{marker_size}X{marker_size}_{nb_markers}'))
        self.aruco_param = aruco.DetectorParameters()
        #self.callback = callback

    def find_aruco_markers(self, img, draw=True):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_param)
        if draw and ids is not None:
            aruco.drawDetectedMarkers(img, corners, ids)
        return corners, ids