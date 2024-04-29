from djitellopy import Tello
import time 
import cv2
import cv2.aruco as aruco





def find_aruco_markers(img, marker_size=4, total_markers=50, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_{marker_size}X{marker_size}_{total_markers}')
    aruco_dict = aruco.getPredefinedDictionary(key)
    aruco_param = aruco.DetectorParameters()
    corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=aruco_param)

    if draw and ids is not None:
        aruco.drawDetectedMarkers(img, corners, ids)

    return corners, ids


if __name__ == "__main__":
    tello = Tello()
    tello.connect()
    tello.streamon()
    time.sleep(2)

    frame_read = tello.get_frame_read()

    while True:
        frame = frame_read.frame

        cv2.imshow("Drone Cam", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        corners, ids = find_aruco_markers(frame)

        if ids is not None:
            for id in ids:
                #print(f"Marqueur détecté: {id[0]}")
                print("human found")

        

    tello.streamoff()
    tello.end()
    cv2.destroyAllWindows()



