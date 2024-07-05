from time import sleep
import time
from djitellopy import TelloSwarm
from voliere import VolierePosition
from voliere import Vehicle
from voliere import Vehicle as Target
import pdb
import numpy as np
import json
import math
import cv2
import threading
import pygame
import sys
from aruco_detect import ArucoSquare




# # To signal readiness of video stream
# stream_ready = threading.Event()
# searching = threading.Event()
# spotting = threading.Event()
# approaching = threading.Event()
# interacting = threading.Event()
# fire = threading.Event()
# hazardous_material = threading.Event()
# survivor = threading.Event()
# map = threading.Event()
# failure = threading.Event()
# nothing_detected = threading.Event()



pygam_ready = threading.Event()
fire = threading.Event()
hazardous_material = threading.Event()
survivor = threading.Event()
map = threading.Event()
failure = threading.Event()
nothing_detected = threading.Event()
standby = threading.Event()

# def display_approach_pattern(tello):
#     print('Waiting for event to signal video readiness')
#     stream_ready.wait()

#     tello.send_expansion_command("led 0 0 0")
#     tello.send_expansion_command("mled sc")


#     # chase for searching
#     chase = ["00000000000000000b000b00b000b00000000000000000000000000000000000",
#     "000000000000000000b000b0000b000b00000000000000000000000000000000",
#     "00000000000000000000000000000000000b000b00b000b00000000000000000",
#     "00000000000000000000000000000000b000b0000b000b000000000000000000"]

#     # morse for spotting
#     morse = "00000000000000000rr00rr0r00rr00rr00rr00r0rr00rr00000000000000000"

#     # onedecent for approaching
#     onedecent = ["00000000000000000pp00pp0p00pp00pp00pp00p0pp00pp00000000000000000",
#                 "00000000000000000pp00pp0p00pp00pp00pp00p000000000000000000000000",
#                 "00000000000000000pp00pp0p00pp00p00000000000000000000000000000000",
#                 "00000000000000000pp00pp00000000000000000000000000000000000000000"]

#     # solid for ready to interact
#     solid = "00000000000000000bb00bb0b00bb00bb00bb00b0bb00bb00000000000000000"

#     start_pattern = time.time()

#     cycleStep = 0

    
    
    
    
      
#     while(True):
#         # raise flags for phases of the rescue operation (to control light accordingly)
#         if searching.is_set():
#             #print("change flags")
#             spotting.clear()
#             approaching.clear()
#             interacting.clear()
#             fire.clear()
#             hazardous_material.clear()
#             survivor.clear()
#             map.clear()
#             failure.clear()
#             nothing_detected.clear()
#         elif(spotting.is_set()):
#             searching.clear()
#             approaching.clear()
#             interacting.clear()  
#             fire.clear()
#             hazardous_material.clear()
#             survivor.clear()
#             map.clear()
#             failure.clear()
#             nothing_detected.clear()
#         elif(approaching.is_set()): 
#             print("approaching")
#             searching.clear()
#             spotting.clear()
#             interacting.clear()
#             fire.clear()
#             hazardous_material.clear()
#             survivor.clear()
#             map.clear()
#             failure.clear()
#             nothing_detected.clear()
#         elif(interacting.is_set()):
#             searching.clear()
#             spotting.clear()
#             approaching.clear()
#             fire.clear()
#             hazardous_material.clear()
#             survivor.clear()
#             map.clear()
#             failure.clear()
#             nothing_detected.clear()
#         elif(fire.is_set()):
#             searching.clear()
#             spotting.clear()
#             approaching.clear()
#             interacting.clear()
#             hazardous_material.clear()
#             survivor.clear()
#             map.clear()
#             failure.clear()
#             nothing_detected.clear()
#         elif(hazardous_material.is_set()):
#             searching.clear()
#             spotting.clear()
#             approaching.clear()
#             interacting.clear()  
#             fire.clear()
#             survivor.clear()
#             map.clear()
#             failure.clear()
#             nothing_detected.clear()
#         elif(survivor.is_set()):
#             searching.clear()
#             spotting.clear()
#             approaching.clear()
#             interacting.clear()  
#             fire.clear()
#             hazardous_material.clear()
#             map.clear()
#             failure.clear()
#             nothing_detected.clear()
#         elif(map.is_set()):
#             searching.clear()
#             spotting.clear()
#             approaching.clear()
#             interacting.clear()  
#             fire.clear()
#             hazardous_material.clear()
#             survivor.clear()
#             failure.clear()
#             nothing_detected.clear()
#         elif(failure.is_set()):
#             searching.clear()
#             spotting.clear()
#             approaching.clear()
#             interacting.clear()  
#             fire.clear()
#             hazardous_material.clear()
#             survivor.clear()
#             map.clear()
#             nothing_detected.clear()
#         elif(nothing_detected.is_set()):
#             searching.clear()
#             spotting.clear()
#             approaching.clear()
#             interacting.clear()  
#             fire.clear()
#             hazardous_material.clear()
#             survivor.clear()
#             map.clear()
#             failure.clear()
            

#         if(searching.is_set()):
#             #tello.send_expansion_command("led br 2.5 75 75 255")
#             if(time.time() - start_pattern > 0.1):
#                 tello.send_expansion_command("mled g " + chase[cycleStep % 4])
#                 start_pattern = time.time()
#                 cycleStep += 1

#         elif(spotting.is_set()):
#             nbcycle = 0
#             cycleStep = 0
#             start_pattern = time.time()
#             gapMorse = time.time()
#             matriceOn = False
#             tello.send_expansion_command("led br 2.5 255 0 0")
#             while(nbcycle < 5):
#                 spotting.wait()
#                 if(time.time() - gapMorse > 1):
#                     while(cycleStep <5):
#                         delay = time.time() - start_pattern
#                         if(delay > 0.1 and delay < 0.3 and matriceOn == False):
#                             tello.send_expansion_command("mled g " + morse)
#                             matriceOn = True
#                         elif(delay > 0.3 and delay < 0.4 and matriceOn == True):
#                             tello.send_expansion_command("mled sc")
#                             matriceOn = False
#                         elif(delay > 0.4):
#                             start_pattern = time.time()
#                             cycleStep += 1
#                     gapMorse = time.time()
#                     cycleStep = 0
#                     nbcycle += 1
#             tello.send_expansion_command("mled sc")
#             tello.send_expansion_command("led 0 0 0")    

#         elif(approaching.is_set()):        
#             start_pattern = time.time()
#             tello.send_expansion_command("led br 0.15 255 100 0")
#             while(cycleStep < 4):
#                 if(time.time() - start_pattern > 0.1):
#                     tello.send_expansion_command("mled g " + onedecent[cycleStep % 4])
#                     start_pattern = time.time()
#                     cycleStep += 1
#             tello.send_expansion_command("mled sc")
#             tello.send_expansion_command("led 0 0 0")

#         elif(interacting.is_set()):
#             start_pattern = time.time()
#             tello.send_expansion_command("led 0 255 0")
#             tello.send_expansion_command("mled g " + solid)
#             solidLightOn = True
#             while(solidLightOn == True):
#                 if(time.time() - start_pattern > 5):
#                     tello.send_expansion_command("mled sc")
#                     tello.send_expansion_command("led 0 0 0")
#                     solidLightOn = False
#         # else:
#         #     print('The pattern does not exist')


# def stream_video(tello):
#     aruco_detector = ArucoSquare()
#     # Simulation starts
#     sim_start_time = time.time()
#     starttime= time.time()
#     list_of_located_positions = np.empty((0, 3))
#     while True:
#         # Limite the experience to 4 minutes
#         if time.time()-sim_start_time > 240:
#             print("Experience exceed expected time.")
#             break
#         if ((time.time()-starttime > 0.1)):
#             # Start displaying the drone camera frames
#             frame = tello.get_frame_read().frame 
#             cv2.imshow("Drone Cam", frame)

#             if not stream_ready.set():
#                 stream_ready.set()
#                 #print('Event: stream is Live')
#             if not searching.set():
#                 searching.set()
                
#             # Exit if 'q' is pressed
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 print("Operation manually terminated.")
#                 break

#             # Detect Aruco markers
#             corners, ids = aruco_detector.find_aruco_markers(frame)
#             if ids is not None:
#                 for id in ids:
#                     if id == 0 and not approaching.set():
#                         #need_interaction_time = False
#                         is_far_enough = True
#                         #print("I see !")
#                         current_position = np.array([tello.position_enu])
#                         #new_position = np.array([current_position])
                        
#                         for i in range (len(list_of_located_positions)):
#                             if ((current_position[0][0]-list_of_located_positions[i][0] <1  and current_position[0][0]-list_of_located_positions[i][0] > -1)
#                                 or (current_position[0][1]-list_of_located_positions[i][1] <1  and current_position[0][1]-list_of_located_positions[i][1] > -1)):
#                                 is_far_enough = False
#                                 break
                        
#                         if is_far_enough:
#                             print(ids.size)             
#                             list_of_located_positions = np.append(list_of_located_positions, current_position, axis=0)
#                             if not approaching.set():
#                                 searching.clear()
#                                 approaching.set()
#                                 print('Event: victim detected')
#                             print("Human found")
#                             print("Located at position: ", current_position)
#                             print("list of located victims: ", list_of_located_positions)
#                             #need_interaction_time = True


#             starttime= time.time()
#     cv2.destroyAllWindows()

def display_approach_pattern(tello):
    print('Waiting for event to signal video readiness')
    pygam_ready.wait()
    print("entered display thread!")
    tello.send_expansion_command("mled sc")

    fire_anim = ["00000000000rr000000rpr0000rrppr000rpppr00rpppprr0rpprppr00rrrrr0",
            "0000r000000rrr0000rrpr0000rrprr000rpprr00rpppprr0rpprprr00rrrrr0",
            "000rr000000rpr0000rrpr0000rppr000rppppr00rpppprr0rpprppr00rrrrr0",
            "000r000000rrr00000rprr000rrpprr00rppprr0rpppppr0rrprppr00rrrrr00"]
    
    survivor_anim = ["0000000000000bb00000bbbbr000bbbb0b000bb000bbbbbb0000bbbb0000bbbb",
                "0000000000000bb00r00bbbb0b00bbbb0b000bb000bbbbbb0000bbbb0000bbbb",
                "0000000000r00bb000b0bbbb00b0bbbb00b00bb0000bbbbb0000bbbb0000bbbb",
                "00000000000r0bb000b0bbbb00b0bbbb00b00bb0000bbbbb0000bbbb0000bbbb",
                "0000000000r00bb000b0bbbb00b0bbbb00b00bb0000bbbbb0000bbbb0000bbbb",
                "0000000000000bb00r00bbbb0b00bbbb0b000bb000bbbbbb0000bbbb0000bbbb"]
    
    hazardous_material_anim = ["0000000000000000000000000000000000000000pppppppppppppppp00000000",
                               "00000000000000000000000000000000000bb000pppbb000pppbpppp0000pppp",
                               "00000000000000000000000000bbbb0000bbbb00pppbbb00pppbpppp0000pppp",
                               "000000000b0bb000bbbbbb000bbbbbbb00bbbbbbpppbbb00pppbpppp0000pppp",
                               "0bb0bbbbbbbbbbbbbbbbbbbbbbbbbbbb00bbbbbbpppbbb00pppbpppp0000pppp"]
    
    map_anim = ["000rr00000000000000000000000000000000000000000000000000000000000",
                "rbbbbbbr00000000000000000000000000000000000000000000000000000000",
                "bbbbbbbbb000000bb000000br000000r00000000000000000000000000000000",
                "bbbbbbbbb000000bb000000bb000000bb000000bb000000br000000r00000000",
                "bbbbbbbbb000000bb000000bb000000bb000000bb000000bb000000bbr0000rb",
                "bbbbbbbbbr000p0bb000000bb00000rbbp00000bb000000bb0r00p0bbbbbbbbb",
                "bbbbbbbbb000000bb000000bb000000bb000000bb000000bb000000bbr0000rb",
                "bbbbbbbbb000000bb000000bb000000bb000000bb000000br000000r00000000",
                "bbbbbbbbb000000bb000000br000000r00000000000000000000000000000000",
                "rbbbbbbr00000000000000000000000000000000000000000000000000000000",
                "000rr00000000000000000000000000000000000000000000000000000000000"]
    
    start_pattern = time.time()

    cycleStep = 0

      
    while(True):
        # raise flags for phases of the rescue operation (to control light accordingly)           

        if(fire.is_set()):
            #tello.send_expansion_command("led br 2.5 75 75 255")
            if(time.time() - start_pattern > 0.1):
                tello.send_expansion_command("mled g " + fire_anim[cycleStep % 4])
                start_pattern = time.time()
                cycleStep += 1

        elif(survivor.is_set()):
            if(time.time() - start_pattern > 0.1):
                tello.send_expansion_command("mled g " + survivor_anim[cycleStep % 6])
                start_pattern = time.time()
                cycleStep += 1  

        elif(hazardous_material.is_set()):        
            if(time.time() - start_pattern > 0.1):
                tello.send_expansion_command("mled g " + hazardous_material_anim[cycleStep % 5])
                start_pattern = time.time()
                cycleStep += 1 

        elif(map.is_set()):
            if(time.time() - start_pattern > 0.1):
                tello.send_expansion_command("mled g " + map_anim[cycleStep % 11])
                start_pattern = time.time()
                cycleStep += 1 
        
        elif(nothing_detected.is_set()):
            tello.send_expansion_command("mled sc")
            nothing_detected.clear()
            standby.set()
            
        # else:
        #     print('The pattern does not exist')

def display_button():
    pygame.init()
    clock = pygame.time.Clock()
    # Initializing surface
    window_size = (800,600)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('What can you see on the Tello drone')
    
    
    # Create a font object
    font = pygame.font.Font(None, 25)
    # Create a surface for the button
    fire_button_surface = pygame.Surface((200, 100))
    survivor_button_surface = pygame.Surface((200, 100))
    hazardous_materials_button_surface = pygame.Surface((200, 100))
    mapping_button_surface = pygame.Surface((200, 100))
    nothing_detected_surface = pygame.Surface((200, 100))
    
    # Render text on the button
    fire_text = font.render("Fire", True, (255, 255, 255))
    fire_text_rect = fire_text.get_rect(center=(fire_button_surface.get_width()/2, fire_button_surface.get_height()/2))
    
    survivor_text = font.render("Survivor", True, (255, 255, 255))
    survivor_text_rect = fire_text.get_rect(center=(survivor_button_surface.get_width()/2.5, survivor_button_surface.get_height()/2))
    
    hazardous_materials_text = font.render("Hazardous Materials", True, (255, 255, 255))
    hazardous_materials_text_rect = fire_text.get_rect(center=(hazardous_materials_button_surface.get_width()/7, hazardous_materials_button_surface.get_height()/2))
    
    mapping_text = font.render("Mapping", True, (255, 255, 255))
    mapping_text_rect = mapping_text.get_rect(center=(mapping_button_surface.get_width()/2, mapping_button_surface.get_height()/2))
    
    nothing_detected_text = font.render("Nothing", True, (255, 255, 255))
    nothing_detected_text_rect = nothing_detected_text.get_rect(center=(nothing_detected_surface.get_width()/2, nothing_detected_surface.get_height()/2))
    
    # Create a pygame.Rect object that represents the button's boundaries
    fire_display = pygame.Rect(125, 100, 200, 100)  # Adjust the position as needed
    survivor_display  = pygame.Rect(475, 100, 200, 100) 
    hazardous_materials_display  = pygame.Rect(125, 250, 200, 100)
    mapping_display  = pygame.Rect(475, 250, 200, 100)
    nothing_detected_display = pygame.Rect(300, 400, 200, 100)
    
    pygam_ready.set()
    print("pygame is ready!")
    # Start the main loop
    while True:
        # Set the frame rate
        clock.tick(60)
        
        # Fill the display with color
        screen.fill((100, 100, 100))
        # Get events from the event queue
        for event in pygame.event.get():
            # Check for the quit event
            if event.type == pygame.QUIT:
                # Quit the game
                pygame.quit()
                sys.exit()
                
            # Check for the mouse button down event
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Call the on_mouse_button_down() function
                if fire_display.collidepoint(event.pos):
                    print("fire seen!")
                    standby.clear()
                    survivor.clear()
                    hazardous_material.clear()
                    map.clear()
                    fire.set()
                    
                    
                if survivor_display.collidepoint(event.pos):
                    print("survivor seen!")
                    standby.clear()
                    fire.clear()
                    hazardous_material.clear()
                    map.clear()
                    survivor.set()
                    
                if hazardous_materials_display.collidepoint(event.pos):
                    print("hazardous materials seen!")
                    standby.clear()
                    fire.clear()
                    survivor.clear()                    
                    map.clear()
                    hazardous_material.set()
                    
                if mapping_display.collidepoint(event.pos):
                    print("mapping seen!")
                    standby.clear()
                    fire.clear()
                    survivor.clear()
                    hazardous_material.clear()
                    map.set()
                
                if nothing_detected_display.collidepoint(event.pos):
                    print("Nothing seen!")
                    standby.clear()
                    fire.clear()
                    survivor.clear()
                    hazardous_material.clear()
                    map.clear()
                    nothing_detected.set()
                    
            # Check if the mouse is over the button. This will create the button hover effect
            if fire_display.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(fire_button_surface, (255, 0, 0), (1, 1, 198, 98))
            else:
                pygame.draw.rect(fire_button_surface, (128, 0, 0), (1, 1, 198, 98))
            
            if survivor_display.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(survivor_button_surface, (0, 0, 255), (1, 1, 198, 98))
            else:
                pygame.draw.rect(survivor_button_surface, (0, 0, 128), (1, 1, 198, 98))

            if hazardous_materials_display.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(hazardous_materials_button_surface, (255, 127, 0), (1, 1, 198, 98))
            else:
                pygame.draw.rect(hazardous_materials_button_surface, (128, 63, 0), (1, 1, 198, 98))
            
            if mapping_display.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(mapping_button_surface, (255, 0, 255), (1, 1, 198, 98))
            else:
                pygame.draw.rect(mapping_button_surface, (128, 0, 128), (1, 1, 198, 98))
            
            if nothing_detected_display.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(nothing_detected_surface, (128, 128, 128), (1, 1, 198, 98))
            else:
                pygame.draw.rect(nothing_detected_surface, (0, 0, 0), (1, 1, 198, 98))
                
        # Shwo the button text
        fire_button_surface.blit(fire_text, fire_text_rect)
        survivor_button_surface.blit(survivor_text, survivor_text_rect)
        hazardous_materials_button_surface.blit(hazardous_materials_text, hazardous_materials_text_rect)
        mapping_button_surface.blit(mapping_text, mapping_text_rect)
        nothing_detected_surface.blit(nothing_detected_text, nothing_detected_text_rect)
        # Draw the button on the screen
        screen.blit(fire_button_surface, (fire_display.x, fire_display.y))
        screen.blit(survivor_button_surface, (survivor_display.x, survivor_display.y))
        screen.blit(hazardous_materials_button_surface, (hazardous_materials_display.x, hazardous_materials_display.y))
        screen.blit(mapping_button_surface, (mapping_display.x, mapping_display.y))
        screen.blit(nothing_detected_surface, (nothing_detected_display.x, nothing_detected_display.y))
        # Update the game state
        pygame.display.update()

def norm_ang(x):
            while x > np.pi :
                x -= 2*np.pi
            while x < -np.pi :
                x += 2*np.pi
            return x


def euclidean_distance(pos, goal):
    return math.sqrt((goal[0]-pos[0])**2 + (goal[1]-pos[1])**2 + (goal[2]-pos[2])**2)

def heading_distance(pos, goal):
    return norm_ang(norm_ang(goal)- norm_ang(pos))


def flight_routine(swarm, voliere):
    # wait for the drone to live stream before takeoff
    # stream_ready.wait()
    #searching.wait()
    # receive the list of waypoints from a json file
    # load the misson
    file = open('Task1_handover_voliere.json')
    command = json.load(file)
    
    lengthWPs = len(command['wayPoints'])
    wPListPos = [[0]*3] * lengthWPs
    wPListHeading = [0] * lengthWPs
    for i in range (lengthWPs):
        x = command['wayPoints'][i]['x']
        y = command['wayPoints'][i]['y']
        z = command['wayPoints'][i]['z']
        theta = command['wayPoints'][i]['theta']
        
        #v = command['velocity']
        wPListPos[i] = [x, y, z]
        wPListHeading[i] = None if theta == None else 2 * math.pi * theta / 360  # conversion from degrees to rad

    print(wPListPos)
    print(wPListHeading)

    wPCounter = 1
    epsilonDist = 0.2
    minepsilonAngle = 0.2
    maxepsilonAngle = 6.08
    interaction_time = 0
 



    # Simulation starts
    sim_start_time = time.time()
    print("Current Tello Battery ",swarm.tellos[0].get_battery())
    try:
        swarm.takeoff()
        lastPointReached = False
        starttime= time.time()
        while time.time()-sim_start_time < 240:
            if(lastPointReached == True):
                break
            # print(time.time()-sim_start_time)
            if ((time.time()-starttime > 0.025)):
                if((time.time() > interaction_time)):
                    if(lastPointReached == False):
                        swarm.tellos[0].fly_to_enu([wPListPos[wPCounter][0], wPListPos[wPCounter][1], wPListPos[wPCounter][2]], wPListHeading[wPCounter])
                        dist = euclidean_distance(swarm.tellos[0].position_enu, wPListPos[wPCounter])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[wPCounter]) #% 2 * math.pi   
                    #print("angle: ", angle)
                    
                # reach the position of the currently loaded waypoint close enough in distance and angle
                
                    if(wPCounter < lengthWPs-1):
                        if(dist <= epsilonDist and (angle %(2*math.pi)<= minepsilonAngle or angle%(2*math.pi) >= maxepsilonAngle)):
                            if((wPListPos[wPCounter] == wPListPos[wPCounter-1]) and (wPListHeading[wPCounter] == wPListHeading[wPCounter-1])):
                                interaction_time = time.time()+10
                                print("Time to wait!")
                                swarm.tellos[0].send_rc_control(0, 0, 0, 0)
                            wPCounter += 1
                            print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " way point number: ", wPCounter, " distance to goal: ", dist, " angle to goal: ", angle)
                            print("WP number: ", wPCounter)
                    else:
                        lastPointReached = True
                else:
                    swarm.tellos[0].fly_to_enu([wPListPos[wPCounter-1][0], wPListPos[wPCounter-1][1], wPListPos[wPCounter-1][2]], wPListHeading[wPCounter-1])
                starttime= time.time()
                    

        #### Save the simulation results ###########################
        # log.save(flight_type='Tello')
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        # log.save(flight_type='Tello')
        #swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        # if visualize:
        #     p.disconnect(physicsClientId=physicsClient)
        sleep(1)

    except (ValueError):
        swarm.land()
        voliere.stop()
        swarm.end()

    except OSError:
        print("Natnet connection error")
        swarm.move_down(int(40))
        swarm.land()
        voliere.stop()
        swarm.end()
        exit(-1)

def main():
    # Connect to the drone
    #---------- OpTr- ACID - -----IP------
    ac_list = [['244', '244', '192.168.1.244'],]

    ip_list = [_[2] for _ in ac_list]
    swarm = TelloSwarm.fromIps(ip_list)

    id_list = [_[1] for _ in ac_list]
    for i,id in enumerate(id_list):
        swarm.tellos[i].set_ac_id(id)

    print('Connecting to Tello Swarm...')
    swarm.connect()
    print('Connected to Tello Swarm...')

    id_dict = dict([('244','244')]) # rigidbody_ID, aircraft_ID
    vehicles = dict([(ac_id, swarm.tellos[i]) for i,ac_id in enumerate(id_dict.keys())])
    voliere = VolierePosition(id_dict, vehicles, freq=100, vel_samples=6)

    voliere.run()
    sleep(2)
    print("Starting Natnet3.x interface at %s" % ("1234567"))

    # Enable live stream of the first swarm's tello
    # swarm.tellos[0].streamon()
    # print('cam switched on')
    # stream_thread = threading.Thread(target=stream_video, args=(swarm.tellos[0],))
    # stream_thread.daemon = True
    # stream_thread.start()
    print('threading running')
    
    pygame_thread = threading.Thread(target=display_button, args=())
    pygame_thread.daemon = True
    pygame_thread.start()

    display_thread = threading.Thread(target=display_approach_pattern, args=(swarm.tellos[0],))
    display_thread.daemon = True
    display_thread.start()

    flight_routine(swarm, voliere)





if __name__=="__main__":
    main()
