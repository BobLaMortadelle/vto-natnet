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
            #print("see aruco corner")

        # if ids is not None and self.callback:
        #     self.callback(corners, ids)

        return corners, ids

    # def run_detection(self, tello):
    #     tello.streamon()
    #     frame_read = tello.get_frame_read()
    #     try:
    #         while True:
    #             frame = frame_read.frame

    #             cv2.imshow("Drone Cam", frame)
    #             if cv2.waitKey(1) & 0xFF == ord('q'):
    #                 break

    #             corners, ids = self.find_aruco_markers(frame)

    #             if ids is not None:
    #                 for id in ids:
    #                     #print(f"Marqueur détecté: {id[0]}")
    #                     print("human found")
    #     finally:
    #         tello.streamoff()
    #         tello.end()
    #         cv2.destroyAllWindows()



