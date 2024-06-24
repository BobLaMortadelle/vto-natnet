import os
import cv2
from djitellopy import Tello
import time
import numpy as np
import threading

# To signal readiness of video stream
stream_ready = threading.Event()

def take_picture(frame): # thank you Jacob Pitsenberger
    if not os.path.exists("pictures"):
        os.mkdir("pictures")
    file_name = "pictures/image_brighter.png"
    brighter_frame = cv2.addWeighted(frame, 5, np.zeros(frame.shape, frame.dtype), 0, 12)
    cv2.imwrite(file_name, brighter_frame)
    
    blur = cv2.GaussianBlur(brighter_frame, (5,5), 0)
    gray_image = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    _, image_threshold = cv2.threshold(gray_image, 180, 255, cv2.THRESH_BINARY)
    file_name = "pictures/image_threshold_brighter.png"
    cv2.imwrite(file_name, image_threshold)
    contours, hierarchy = cv2.findContours(image_threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    for i, contour in enumerate(contours):
        if i == 0:
            continue
        epsilon = 0.01*cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        cv2.drawContours(frame, contour, 0, (255, 0, 0), 4)
        
        x, y, w, h = cv2.boundingRect(approx)
        x_mid = int((x+w)/2)
        y_mid = int((y+h)/2)
        
        coords = (x_mid, y_mid)
        colour = (0, 0, 0)
        font = cv2.FONT_HERSHEY_COMPLEX
        
        if len(approx == 3):
            cv2.putText(frame, "triangle", coords, font, 1, colour, 1)
        elif len(approx == 4):
            cv2.putText(frame, "rectangle", coords, font, 1, colour, 1)
        
        cv2.imshow("Map", frame)
    file_name = "pictures/map_brighter.png"
    cv2.imwrite(file_name, frame)
    print("Image saved:", file_name)
    time.sleep(0.3)

         
def display_stream(tello):
    while True:        
        # get the stream's frame
        frame = tello.get_frame_read().frame 
        cv2.imshow("Frame", frame)
        
        if not stream_ready.is_set():
                stream_ready.set()
        
        # create a variable to check which key has been pressed
        key = cv2.waitKey(1) & 0xFF 
        
        # if q is pressed, the video stream is canceled
        if key == ord('q'):
            print("Operation manually terminated.")
            break
        elif key == ord('p'):
            take_picture(frame)
            
def flight_routine():
    stream_ready.wait()
    start_pattern = time.time()
    while(True):
        if(time.time() - start_pattern > 0.1):
            print("fly")
            start_pattern = time.time()
            
def main():
    tello = Tello()
    tello.connect()
    tello.streamon()
    tello.set_video_direction(tello.CAMERA_DOWNWARD)
    display_thread = threading.Thread(target=display_stream, args=(tello,))
    display_thread.daemon = True
    display_thread.start()

    flight_routine()
    
    


    

if __name__=="__main__":
    main()
        