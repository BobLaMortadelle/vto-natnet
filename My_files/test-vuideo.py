from djitellopy import Tello
import time 
import cv2

print(dir(cv2.aruco))

# if __name__ == "__main__":
#     tello = Tello()
#     tello.connect()
#     tello.streamon()
#     time.sleep(2)

#     frame_read = tello.get_frame_read()

#     while True:
#         frame = frame_read.frame

#         cv2.imshow("Drone Cam", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break