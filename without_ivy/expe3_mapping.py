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
import random
import logging 
import matplotlib.pyplot as plt
import os
import csv

# system event
pygame_ready = threading.Event()
failure = threading.Event()
anim_set = threading.Event()
log_ready = threading.Event()
nothing_detected = threading.Event()
standby = threading.Event()
#trajectory event
next_pose = threading.Event()

#animation event
go_to_position = threading.Event()
wP0 = threading.Event()
wP1 = threading.Event()
wP2 = threading.Event()
in_position = threading.Event()
return_home = threading.Event()
wP3 = threading.Event()
wP4 = threading.Event()





nothing_found = threading.Event()
fire = threading.Event()
hazardous_material = threading.Event()
survivor = threading.Event()
map = threading.Event()
start_handover = threading.Event()
validate_handover = threading.Event()
nothing_displayed = threading.Event()

lock = threading.Lock()



userNb  = ''
nbToDisplay = '0'
state = ''
anim_state = 'none'
traj_state = ''

def take_picture(tello): # thank you Jacob Pitsenberger
    in_position.wait()
    tello.streamon()
    tello.set_video_direction(tello.CAMERA_DOWNWARD)       
    # get the stream's frame
    frame = tello.get_frame_read().frame 
    tello.streamoff() 
    cv2.imshow("Frame", frame)
    if not os.path.exists("pictures"):
        os.mkdir("pictures")
    file_name = "pictures/map.png"
    cv2.imwrite(file_name, frame)
    
            


def display_approach_pattern(tello):
    global nbToDisplay
    pygame_ready.wait()
    print("entered display thread!")
    

    fire_anim = ["00000000000rr000000rpr0000rrppr000rpppr00rpppprr0rpprppr00rrrrr0",
            "0000r000000rrr0000rrpr0000rrprr000rpprr00rpppprr0rpprprr00rrrrr0",
            "000rr000000rpr0000rrpr0000rppr000rppppr00rpppprr0rpprppr00rrrrr0",
            "000r000000rrr00000rprr000rrpprr00rppprr0rpppppr0rrprppr00rrrrr00"]
    
    survivor_anim = ["000000000rr0rr00rrrrrrr0rrrrrrp00rrrrp0000rrp000000p000000000000",
                "0000000000rr0rr00rrrrrrr0rrrrrrp0rrrrrrp00rrrrp0000rrp000000p000",
                "000000000rr0rr00rrrrrrr0rrrrrrp00rrrrp0000rrp000000p000000000000",
                "0000000000rr0rr00rrrrrrr0rrrrrrp0rrrrrrp00rrrrp0000rrp000000p000",
                "000000000rr0rr00rrrrrrr0rrrrrrp00rrrrp0000rrp000000p000000000000",]
    
    hazardous_material_anim = ["00bbbb00000bb000000bb000000bb00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000bb000000bb000000pp00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000bb000000pp000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000pp000000rr000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000rr000000rr000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0"]
    
    map_anim = ["000rr00000000000000000000000000000000000000000000000000000000000",
                "bbbbbbbbb000000bb000000br000000r00000000000000000000000000000000",
                "bbbbbbbbb000000bb000000bb000000bb000000bb000000bb000000bbr0000rb",
                "bbbbbbbbbr000p0bb000000bb00000rbbp00000bb000000bb0r00p0bbbbbbbbb",
                "bbbbbbbbb000000bb000000bb000000bb000000bb000000bb000000bbr0000rb",
                "bbbbbbbbb000000bb000000br000000r00000000000000000000000000000000"]
    
    start_handover_anim = ["00000000000000000000000000pppp0000ppppp00pppppp00pppppp000pppp00",
                           "00000000000p00000p0p0p000p0p0p0000pppp0p00ppppp00pppppp000pppp00",
                           "000p00000p0p0p000p0p0p000p0p0p0p00pppp0pp0ppppp00pppppp000pppp00"]
    
    validate_handover_anim = ["000000000000000000pppp00bbppppp0bbppppp0bbppppp0bbppppp000000000",
                              "000000000000pp0000ppp000bbppppp0bbppppp0bbppppp0bbppppp000000000",
                              "0000p000000pp00000pp0000bbppppp0bbppppp0bbppppp0bbppppp000000000",
                              "0000p000000pp00000pp0000bbppppp0bbppppp0bbppppp0bbppppp000000000"]
    

    start_pattern = time.time()
    cycleStep = 0
    start_light= time.time()
    while(True):
        if (time.time() - start_light > 0.05):
            lock.acquire()
            # if not in stand by mode (meaning a static display or an original UDP animation)                     
            try:
                if(fire.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        if((cycleStep % 6  == 1 or cycleStep % 6  == 2) and nbToDisplay != '0'):
                            tello.send_expansion_command("mled s p {nb}".format(nb = nbToDisplay))
                        else:
                            tello.send_expansion_command("mled g " + fire_anim[cycleStep % 4])
                        start_pattern = time.time()
                        cycleStep += 1

                elif(survivor.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        if((cycleStep % 7  == 1 or cycleStep % 7  == 2) and nbToDisplay != '0'):
                            tello.send_expansion_command("mled s p {nb}".format(nb = nbToDisplay))
                        else:
                            tello.send_expansion_command("mled g " + survivor_anim[cycleStep % 5])
                        start_pattern = time.time()
                        cycleStep += 1  

                elif(hazardous_material.is_set()):        
                    if(time.time() - start_pattern > 0.1):
                        if((cycleStep % 7  == 1 or cycleStep % 7  == 2) and nbToDisplay != '0'):
                            tello.send_expansion_command("mled s p {nb}".format(nb = nbToDisplay))
                        else:
                            tello.send_expansion_command("mled g " + hazardous_material_anim[cycleStep % 5])
                        start_pattern = time.time()
                        cycleStep += 1 

                elif(map.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        if((cycleStep % 8  == 1 or cycleStep % 8  == 2) and nbToDisplay != '0'):
                            tello.send_expansion_command("mled s p {nb}".format(nb = nbToDisplay))
                        else:
                            tello.send_expansion_command("mled g " + map_anim[cycleStep % 6])
                        start_pattern = time.time()
                        cycleStep += 1 
                
                elif(start_handover.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        if((cycleStep % 5  == 1 or cycleStep % 5  == 2) and nbToDisplay != '0'):
                            tello.send_expansion_command("mled s p {nb}".format(nb = nbToDisplay))
                        else:
                            tello.send_expansion_command("mled g " + start_handover_anim[cycleStep % 3])
                        start_pattern = time.time()
                        cycleStep += 1
                
                elif(validate_handover.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        if((cycleStep % 6  == 1 or cycleStep % 6  == 2) and nbToDisplay != '0'):
                            tello.send_expansion_command("mled s p {nb}".format(nb = nbToDisplay))
                        else:
                            tello.send_expansion_command("mled g " + validate_handover_anim[cycleStep % 4])
                        start_pattern = time.time()
                        cycleStep += 1
                        
                elif(nothing_detected.is_set()):
                    if not standby.is_set():
                        tello.send_expansion_command("mled sc")
                        tello.send_expansion_command("led 0 255 0")
                        standby.set()
                    nothing_detected.clear()
                    
                elif(nothing_displayed.is_set()):
                    if not standby.is_set():
                        tello.send_expansion_command("mled sc")
                        tello.send_expansion_command("led 0 0 0")
                        standby.set()
                    nothing_displayed.clear()
            finally:
                lock.release()
            start_light = time.time()
                
            
def display_button():
    global traj_state
    global anim_state
    global userNb
    global nbToDisplay
    
    pygame.init()
    clock = pygame.time.Clock()
    is_display = True
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    window_size = (220,50)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Particpant number: ')
    # Create a font object
    font = pygame.font.Font(None, 32)
    # Input box
    input_box = pygame.Rect(10, 10, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    # Main loop
    clock = pygame.time.Clock()
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                # Change the current color of the input box
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        print(text)
                        pygame.quit()
                        is_display = False
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        if(is_display):
            screen.fill(WHITE)
            # Render the current text
            txt_surface = font.render(text, True, BLACK)
            # Resize the box if the text is too long
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            # Blit the text
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            # Blit the input_box rect
            pygame.draw.rect(screen, color, input_box, 2)

            pygame.display.flip()
            clock.tick(30)               
    userNb = text   
   
    log_ready.set()
    
    
    pygame.init()
    clock = pygame.time.Clock() 
    # Initializing surface
    window_size = (1800,600)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('What can you see on the Tello drone')
    
    
    # Create a font object
    font = pygame.font.Font(None, 25)
    # Create a surface for the button
    fire_button_surface = pygame.Surface((200, 100))
    survivor_button_surface = pygame.Surface((200, 100))
    hazardous_materials_button_surface = pygame.Surface((200, 100))
    mapping_button_surface = pygame.Surface((200, 100))
    start_handover_surface = pygame.Surface((200, 100))
    validate_handover_surface = pygame.Surface((200, 100))
    no_display_surface = pygame.Surface((200, 100))
    surface_1 = pygame.Surface((100, 100))
    surface_2 = pygame.Surface((100, 100))
    surface_3 = pygame.Surface((100, 100))
    surface_4 = pygame.Surface((100, 100))
    surface_5 = pygame.Surface((100, 100))
    surface_6 = pygame.Surface((100, 100))
    surface_7 = pygame.Surface((100, 100))
    surface_8 = pygame.Surface((100, 100))
    surface_9 = pygame.Surface((100, 100))
    find_survivor_surface = pygame.Surface((200, 100))
    return_home_surface = pygame.Surface((200, 100))
    
    
    # Render text on the button
    fire_text = font.render("Fire", True, (255, 255, 255))
    fire_text_rect = fire_text.get_rect(center=(fire_button_surface.get_width()/2, fire_button_surface.get_height()/2))
    
    survivor_text = font.render("Survivor", True, (255, 255, 255))
    survivor_text_rect = fire_text.get_rect(center=(survivor_button_surface.get_width()/2.5, survivor_button_surface.get_height()/2))
    
    hazardous_materials_text = font.render("Hazardous Materials", True, (255, 255, 255))
    hazardous_materials_text_rect = fire_text.get_rect(center=(hazardous_materials_button_surface.get_width()/7, hazardous_materials_button_surface.get_height()/2))
    
    mapping_text = font.render("Mapping", True, (255, 255, 255))
    mapping_text_rect = mapping_text.get_rect(center=(mapping_button_surface.get_width()/2, mapping_button_surface.get_height()/2))
    
    start_handover_text = font.render("Start handover", True, (255, 255, 255))
    start_handover_text_rect = start_handover_text.get_rect(center=(start_handover_surface.get_width()/2, start_handover_surface.get_height()/2))
    
    validate_handover_text = font.render("Validate handover", True, (255, 255, 255))
    validate_handover_text_rect = validate_handover_text.get_rect(center=(validate_handover_surface.get_width()/2, validate_handover_surface.get_height()/2))
    
    no_display_text = font.render("No Display", True, (255, 255, 255))
    no_display_text_rect = no_display_text.get_rect(center=(no_display_surface.get_width()/2, no_display_surface.get_height()/2))
    
    surface_1_text = font.render("1", True, (0, 0, 0))
    surface_1_text_rect = surface_1_text.get_rect(center=(surface_1.get_width()/2, surface_1.get_height()/2))

    surface_2_text = font.render("2", True, (0, 0, 0))
    surface_2_text_rect = surface_2_text.get_rect(center=(surface_2.get_width()/2, surface_2.get_height()/2))

    surface_3_text = font.render("3", True, (0, 0, 0))
    surface_3_text_rect = surface_3_text.get_rect(center=(surface_3.get_width()/2, surface_3.get_height()/2))

    surface_4_text = font.render("4", True, (0, 0, 0))
    surface_4_text_rect = surface_4_text.get_rect(center=(surface_4.get_width()/2, surface_4.get_height()/2))

    surface_5_text = font.render("5", True, (0, 0, 0))
    surface_5_text_rect = surface_5_text.get_rect(center=(surface_5.get_width()/2, surface_5.get_height()/2))

    surface_6_text = font.render("6", True, (0, 0, 0))
    surface_6_text_rect = surface_6_text.get_rect(center=(surface_6.get_width()/2, surface_6.get_height()/2))

    surface_7_text = font.render("7", True, (0, 0, 0))
    surface_7_text_rect = surface_7_text.get_rect(center=(surface_7.get_width()/2, surface_7.get_height()/2))

    surface_8_text = font.render("8", True, (0, 0, 0))
    surface_8_text_rect = surface_8_text.get_rect(center=(surface_8.get_width()/2, surface_8.get_height()/2))

    surface_9_text = font.render("9", True, (0, 0, 0))
    surface_9_text_rect = surface_9_text.get_rect(center=(surface_9.get_width()/2, surface_9.get_height()/2))

    find_survivor_text = font.render("Go to position", True, (255, 255, 255))
    find_survivor_text_rect = find_survivor_text.get_rect(center=(find_survivor_surface.get_width()/2, find_survivor_surface.get_height()/2))
    
    return_home_text = font.render("Return PRV", True, (255, 255, 255))
    return_home_text_rect = return_home_text.get_rect(center=(return_home_surface.get_width()/2, return_home_surface.get_height()/2))
    
    # Create a pygame.Rect object that represents the button's boundaries
    mapping_display = pygame.Rect(20, 100, 200, 100)  # Adjust the position as needed
    survivor_display  = pygame.Rect(240, 100, 200, 100) 
    hazardous_materials_display  = pygame.Rect(20, 250, 200, 100)
    fire_display  = pygame.Rect(240, 250, 200, 100)
    start_handover_display  = pygame.Rect(20, 400, 200, 100)
    validate_handover_display  = pygame.Rect(240, 400, 200, 100)
    no_display_display = pygame.Rect(460, 100, 200, 100) 
    display_1 = pygame.Rect(740, 100, 100, 100)
    display_2 = pygame.Rect(860, 100, 100, 100)
    display_3 = pygame.Rect(980, 100, 100, 100)
    display_4 = pygame.Rect(740, 250, 100, 100)
    display_5 = pygame.Rect(860, 250, 100, 100)
    display_6 = pygame.Rect(980, 250, 100, 100)
    display_7 = pygame.Rect(740, 400, 100, 100)
    display_8 = pygame.Rect(860, 400, 100, 100)
    display_9 = pygame.Rect(980, 400, 100, 100)
    find_survivor_display = pygame.Rect(1140, 100, 200, 100)
    return_home_display = pygame.Rect(1360, 100, 200, 100)
    
    
    pygame_ready.set()
    print("pygame is ready!")
    # Start the main loop
    start_interface = time.time()
    while True:
        if(time.time() - start_interface > 0.05):
            if lock.acquire(blocking=False):
                try:
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
                                print("fire display")
                                anim_state = "fire"
                                fire.set()
                                standby.clear()
                                
                            if survivor_display.collidepoint(event.pos):
                                print("survivor display")
                                anim_state = "survivor"
                                survivor.set()
                                standby.clear()
                                
                            if hazardous_materials_display.collidepoint(event.pos):
                                print("hazardous materials display")
                                anim_state = "hazardous material"
                                hazardous_material.set()
                                standby.clear()
                                
                            if mapping_display.collidepoint(event.pos):
                                print("mapping display")
                                anim_state = "mapping"
                                map.set()
                                standby.clear()
                            
                            if start_handover_display.collidepoint(event.pos):
                                print("start handover display")
                                anim_state = "start handover"
                                start_handover.set()
                                standby.clear()
                                
                            if validate_handover_display.collidepoint(event.pos):
                                print("validate handover seen!")
                                anim_state = "validate handover"
                                validate_handover.set()
                                standby.clear()
                                
                            if no_display_display.collidepoint(event.pos):
                                print("no display")
                                anim_state = "none"
                                nbToDisplay = '0'
                                if fire.is_set():
                                    fire.clear()
                                if survivor.is_set():
                                    survivor.clear()
                                if hazardous_material.is_set():
                                    hazardous_material.clear()
                                if map.is_set():
                                    map.clear()
                                if start_handover.is_set():
                                    start_handover.clear()
                                if validate_handover.is_set():
                                    validate_handover.clear()
                                if not nothing_displayed.is_set():
                                    nothing_displayed.set()
                                
                                
                            if display_1.collidepoint(event.pos):
                                print("1 displayed")
                                anim_state = anim_state + "1"
                                nbToDisplay = '1'
                                
                            if display_2.collidepoint(event.pos):
                                print("2 displayed")
                                anim_state = anim_state + "2"
                                nbToDisplay ='2'
                                
                            if display_3.collidepoint(event.pos):
                                print("3 displayed")
                                anim_state = anim_state + "3"
                                nbToDisplay = '3'
                            
                            if display_4.collidepoint(event.pos):
                                print("4 displayed")
                                anim_state = anim_state + "4"
                                nbToDisplay = '4'
                                
                            if display_5.collidepoint(event.pos):
                                print("5 displayed")
                                anim_state = anim_state + "5"
                                nbToDisplay = '5'
                            
                            if display_6.collidepoint(event.pos):
                                print("6 displayed")
                                anim_state = anim_state + "6"
                                nbToDisplay = '6'
                            
                            if display_7.collidepoint(event.pos):
                                print("7 displayed")
                                anim_state = anim_state + "7"
                                nbToDisplay = '7'
                                
                            if display_8.collidepoint(event.pos):
                                print("8 displayed")
                                anim_state = anim_state + "8"
                                nbToDisplay = '8'
                            
                            if display_9.collidepoint(event.pos):
                                print("9 displayed")
                                anim_state = anim_state + "9"
                                nbToDisplay = '9'
                                    
                            if find_survivor_display.collidepoint(event.pos):
                                print("Go to position")
                                traj_state = "go to position WP0"
                                go_to_position.set()
                                return_home.clear()
                                wP0.set()
                                wP1.clear()
                                wP2.clear()
                                wP3.clear()
                                wP4.clear()
                                
                            if return_home_display.collidepoint(event.pos):
                                print("Return home")
                                traj_state = "retrun home WP2"
                                nothing_detected.set()
                                fire.clear()
                                survivor.clear()
                                hazardous_material.clear()
                                map.clear()
                                start_handover.clear()
                                validate_handover.clear()
                                return_home.set()
                                wP2.set()
                                wP3.clear()
                                wP4.clear()
                                go_to_position.clear()
                                
                                
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
                        
                        if start_handover_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(start_handover_surface, (200, 200, 0), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(start_handover_surface, (100, 100, 0), (1, 1, 198, 98))
                        
                        if validate_handover_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(validate_handover_surface, (0, 255, 0), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(validate_handover_surface, (0, 128, 0), (1, 1, 198, 98))
                            
                        if no_display_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(no_display_surface, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(no_display_surface, (0, 0, 0), (1, 1, 198, 98))
                        
                        if display_1.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(surface_1, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(surface_1, (255, 255, 255), (1, 1, 198, 98))
                        
                        if display_2.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(surface_2, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(surface_2, (255, 255, 255), (1, 1, 198, 98))
                        
                        if display_3.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(surface_3, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(surface_3, (255, 255, 255), (1, 1, 198, 98))
                        
                        if display_4.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(surface_4, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(surface_4, (255, 255, 255), (1, 1, 198, 98))
                        
                        if display_5.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(surface_5, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(surface_5, (255, 255, 255), (1, 1, 198, 98))
                        
                        if display_6.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(surface_6, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(surface_6, (255, 255, 255), (1, 1, 198, 98))
                        
                        if display_7.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(surface_7, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(surface_7, (255, 255, 255), (1, 1, 198, 98))
                        
                        if display_8.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(surface_8, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(surface_8, (255, 255, 255), (1, 1, 198, 98))
                        
                        if display_9.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(surface_9, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(surface_9, (255, 255, 255), (1, 1, 198, 98))
                                
                        if find_survivor_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(find_survivor_surface, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(find_survivor_surface, (0, 0, 0), (1, 1, 198, 98))
                        
                        if return_home_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(return_home_surface, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(return_home_surface, (0, 0, 0), (1, 1, 198, 98))
                        
                             
                    # Show the button text
                    fire_button_surface.blit(fire_text, fire_text_rect)
                    survivor_button_surface.blit(survivor_text, survivor_text_rect)
                    hazardous_materials_button_surface.blit(hazardous_materials_text, hazardous_materials_text_rect)
                    mapping_button_surface.blit(mapping_text, mapping_text_rect)
                    start_handover_surface.blit(start_handover_text, start_handover_text_rect)
                    validate_handover_surface.blit(validate_handover_text, validate_handover_text_rect)
                    no_display_surface.blit(no_display_text, no_display_text_rect)
                    surface_1.blit(surface_1_text, surface_1_text_rect)
                    surface_2.blit(surface_2_text, surface_2_text_rect)
                    surface_3.blit(surface_3_text, surface_3_text_rect)
                    surface_4.blit(surface_4_text, surface_4_text_rect)
                    surface_5.blit(surface_5_text, surface_5_text_rect)
                    surface_6.blit(surface_6_text, surface_6_text_rect)
                    surface_7.blit(surface_7_text, surface_7_text_rect)
                    surface_8.blit(surface_8_text, surface_8_text_rect)
                    surface_9.blit(surface_9_text, surface_9_text_rect)
                    find_survivor_surface.blit(find_survivor_text, find_survivor_text_rect)
                    return_home_surface.blit(return_home_text, return_home_text_rect)
                    
                    
                    # Draw the button on the screen
                    screen.blit(fire_button_surface, (fire_display.x, fire_display.y))
                    screen.blit(survivor_button_surface, (survivor_display.x, survivor_display.y))
                    screen.blit(hazardous_materials_button_surface, (hazardous_materials_display.x, hazardous_materials_display.y))
                    screen.blit(mapping_button_surface, (mapping_display.x, mapping_display.y))
                    screen.blit(start_handover_surface, (start_handover_display.x, start_handover_display.y))
                    screen.blit(validate_handover_surface, (validate_handover_display.x, validate_handover_display.y))
                    screen.blit(no_display_surface, (no_display_display.x, no_display_display.y))
                    screen.blit(surface_1, (display_1.x, display_1.y))
                    screen.blit(surface_2, (display_2.x, display_2.y))
                    screen.blit(surface_3, (display_3.x, display_3.y))
                    screen.blit(surface_4, (display_4.x, display_4.y))
                    screen.blit(surface_5, (display_5.x, display_5.y))
                    screen.blit(surface_6, (display_6.x, display_6.y))
                    screen.blit(surface_7, (display_7.x, display_7.y))
                    screen.blit(surface_8, (display_8.x, display_8.y))
                    screen.blit(surface_9, (display_9.x, display_9.y))
                    screen.blit(find_survivor_surface, (find_survivor_display.x, find_survivor_display.y))
                    screen.blit(return_home_surface, (return_home_display.x, return_home_display.y))
                    
                    # Update the game state
                    pygame.display.update()
                finally:
                    lock.release()
            start_interface = time.time()

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
    # receive the list of waypoints from a json file
    # load the misson

    
    global anim_state
    global traj_state
    global userNb
    global state
    log_ready.wait()
    logger = logging.getLogger('EXperience3Logger')
    handler = logging.FileHandler('expe3_{nombre}_mapping.log'.format(nombre = userNb), mode="a")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    file = open('expe3_mapping.json')
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

    epsilonDist = 0.2
    minepsilonAngle = 0.2
    maxepsilonAngle = 6.08
    sim_start_time = time.time()
    print("Current Tello Battery ",swarm.tellos[0].get_battery())
    #swarm.tellos[0].send_expansion_command("led 0 255 0")
    try:
        # swarm.turn_motor_off()
        swarm.send_expansion_command("mled sc")
        swarm.send_expansion_command("led 0 0 0")
        swarm.takeoff()
        traj_state = 'takeoff'
        endMission = False
        starttime = time.time()
        log_timer = time.time()
        while time.time()-sim_start_time < 720:
            if time.time()-log_timer > 0.2:
                bracelet_position_str = voliere.vehicles['245'].position
                drone_position_str = swarm.tellos[0].position_enu
                drone_heading_str = swarm.tellos[0].get_heading()
                logMessage = traj_state + ',' + anim_state + ',' + "{pose}".format(pose = bracelet_position_str) + ',' +  "{drone}".format(drone = drone_position_str) + ',' + "{heading}".format(heading = drone_heading_str)
                logger.info(logMessage)
                log_timer = time.time()
            if(endMission != False):
                print('end of experiment')
                break
            if ((time.time()-starttime > 0.025)):
                if(go_to_position.is_set()):
                    if(wP0.is_set()): 
                        dist = euclidean_distance(swarm.tellos[0].position_enu, [wPListPos[0][0], wPListPos[0][1], wPListPos[0][2]])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[0])
                        swarm.tellos[0].fly_to_enu([wPListPos[0][0], wPListPos[0][1], wPListPos[0][2]], wPListHeading[0])
                        if(dist <= epsilonDist and (angle %(2*math.pi)<= minepsilonAngle or angle%(2*math.pi) >= maxepsilonAngle)):                                                  
                            print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " distance to goal: ", dist, " angle to goal: ", angle)
                            print("WP number: 0")
                            wP0.clear()
                            traj_state = "go to position WP1"
                            wP1.set()                            
                    elif(wP1.is_set()): 
                        dist = euclidean_distance(swarm.tellos[0].position_enu, [wPListPos[1][0], wPListPos[1][1], wPListPos[1][2]])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[1])
                        swarm.tellos[0].fly_to_enu([wPListPos[1][0], wPListPos[1][1], wPListPos[1][2]], wPListHeading[1])
                        if(dist <= epsilonDist and (angle %(2*math.pi)<= minepsilonAngle or angle%(2*math.pi) >= maxepsilonAngle)):     
                            in_position.set()                                             
                            print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " distance to goal: ", dist, " angle to goal: ", angle)
                            print("WP number: 1")
                            wP1.clear()
                            traj_state = "go to position WP2"
                            wP2.set()                         
                            
                    
                elif(return_home.is_set()):
                    if(wP2.is_set()):
                        dist = euclidean_distance(swarm.tellos[0].position_enu, [wPListPos[2][0], wPListPos[2][1], wPListPos[2][2]])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[2])
                        swarm.tellos[0].fly_to_enu([wPListPos[2][0], wPListPos[2][1], wPListPos[2][2]], wPListHeading[2])
                        if(dist <= epsilonDist and (angle %(2*math.pi)<= minepsilonAngle or angle%(2*math.pi) >= maxepsilonAngle)):                                                  
                            print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " distance to goal: ", dist, " angle to goal: ", angle)
                            print("WP number: 2")
                            wP2.clear()
                            traj_state = "retrun home WP3"
                            wP3.set()
                    if(wP3.is_set()):
                        dist = euclidean_distance(swarm.tellos[0].position_enu, [wPListPos[3][0], wPListPos[3][1], wPListPos[3][2]])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[3])
                        swarm.tellos[0].fly_to_enu([wPListPos[3][0], wPListPos[3][1], wPListPos[3][2]], wPListHeading[3])
                        if(dist <= epsilonDist and (angle %(2*math.pi)<= minepsilonAngle or angle%(2*math.pi) >= maxepsilonAngle)):                                                  
                            print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " distance to goal: ", dist, " angle to goal: ", angle)
                            print("WP number: 3")
                            wP3.clear()
                            traj_state = "retrun home WP4"
                            wP4.set()
                    if(wP4.is_set()):
                        dist = euclidean_distance(swarm.tellos[0].position_enu, [wPListPos[4][0], wPListPos[4][1], wPListPos[4][2]])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[4])
                        swarm.tellos[0].fly_to_enu([wPListPos[4][0], wPListPos[4][1], wPListPos[4][2]], wPListHeading[4])
                        if(dist <= epsilonDist and (angle %(2*math.pi)<= minepsilonAngle or angle%(2*math.pi) >= maxepsilonAngle)):                                                  
                            print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " distance to goal: ", dist, " angle to goal: ", angle)
                            print("WP number: 4")
                            wP4.clear()
                            traj_state = "mission end"
                            endMission = True
                else:
                    dist = euclidean_distance(swarm.tellos[0].position_enu, [wPListPos[0][0], wPListPos[0][1], wPListPos[0][2]])
                    angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[0])
                    swarm.tellos[0].fly_to_enu([wPListPos[0][0], wPListPos[0][1], wPListPos[0][2]], wPListHeading[0])
                starttime= time.time()
        print("Current Tello Battery ",swarm.tellos[0].get_battery()) 
        fire.clear()
        survivor.clear()
        hazardous_material.clear()
        map.clear()
        start_handover.clear()
        validate_handover.clear()     
        swarm.send_expansion_command("mled sc")   
        swarm.send_expansion_command("led 0 0 0")    
        swarm.move_down(int(40))
        swarm.land()
        swarm.turn_motor_on()
        state = 'landed'
        voliere.stop()
        swarm.end()

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        swarm.land()  
        print("Current Tello Battery ",swarm.tellos[0].get_battery())  
        swarm.turn_motor_on()  
        voliere.stop()
        swarm.end()
        sleep(1)

    except (ValueError):
        swarm.land()
        swarm.turn_motor_on()
        print("Current Tello Battery ",swarm.tellos[0].get_battery())  
        voliere.stop()
        swarm.end()

    except OSError:
        print("Natnet connection error")
        swarm.move_down(int(40))
        swarm.land()
        swarm.turn_motor_on()
        print("Current Tello Battery ",swarm.tellos[0].get_battery())  
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

    id_dict = dict([('244','244'), ('888','888'), ('245', '245')]) # rigidbody_ID, aircraft_ID
    vehicles = dict([('244', swarm.tellos[0]), ('888', Vehicle(['888'])), ('245', Vehicle(['245']))])
    voliere = VolierePosition(id_dict, vehicles, freq=100, vel_samples=6)

    voliere.run()
    sleep(2)
    print("Starting Natnet3.x interface at %s" % ("1234567"))
    print('threading running')
    
    pygame_thread = threading.Thread(target=display_button, args=())
    pygame_thread.daemon = True
    pygame_thread.start()
    
    display_thread = threading.Thread(target=display_approach_pattern, args=(swarm.tellos[0],))
    display_thread.daemon = True
    display_thread.start()
    
    picture_thread = threading.Thread(target=take_picture, args=(swarm.tellos[0],))
    picture_thread.daemon = True
    picture_thread.start()

    flight_routine(swarm, voliere)





if __name__=="__main__":
    main()
