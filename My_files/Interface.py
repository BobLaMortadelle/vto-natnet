from time import sleep
import time
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
find_survivor_event = threading.Event()
wP0 = threading.Event()
wP1 = threading.Event()
wP2 = threading.Event()
wP3 = threading.Event()
wP4 = threading.Event()
wP5 = threading.Event()
fly_to_heat_pointe_1 = threading.Event()
fly_to_heat_pointe_2 = threading.Event()
fly_to_heat_pointe_3 = threading.Event()
fly_to_heat_pointe_4 = threading.Event()
fly_to_heat_pointe_5 = threading.Event()
fly_to_heat_pointe_6 = threading.Event()
fly_to_heat_pointe_7 = threading.Event()
return_home = threading.Event()
wP12 = threading.Event()
wP13 = threading.Event()
wP14 = threading.Event()
wP15 = threading.Event()



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

         
def display_button():
    global anim_state
    global traj_state
    global userNb
    global nbToDisplay
    
    
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
    heat_point_1_surface = pygame.Surface((200, 100))
    heat_point_2_surface = pygame.Surface((200, 100))
    heat_point_3_surface = pygame.Surface((200, 100))
    heat_point_4_surface = pygame.Surface((200, 100))
    heat_point_5_surface = pygame.Surface((200, 100))
    heat_point_6_surface = pygame.Surface((200, 100))
    heat_point_7_surface = pygame.Surface((200, 100))
    
    
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

    find_survivor_text = font.render("Find Heat Point", True, (255, 255, 255))
    find_survivor_text_rect = find_survivor_text.get_rect(center=(find_survivor_surface.get_width()/2, find_survivor_surface.get_height()/2))
    
    return_home_text = font.render("Return PRV", True, (255, 255, 255))
    return_home_text_rect = return_home_text.get_rect(center=(return_home_surface.get_width()/2, return_home_surface.get_height()/2))
    
    heat_point_1_text = font.render("heat point 1", True, (255, 255, 255))
    heat_point_1_text_rect = heat_point_1_text.get_rect(center=(heat_point_1_surface.get_width()/2, heat_point_1_surface.get_height()/2))
    
    heat_point_2_text = font.render("heat point 2", True, (255, 255, 255))
    heat_point_2_text_rect = heat_point_2_text.get_rect(center=(heat_point_2_surface.get_width()/2, heat_point_2_surface.get_height()/2))
    
    heat_point_3_text = font.render("heat point 3", True, (255, 255, 255))
    heat_point_3_text_rect = heat_point_3_text.get_rect(center=(heat_point_3_surface.get_width()/2, heat_point_3_surface.get_height()/2))
    
    heat_point_4_text = font.render("heat point 4", True, (255, 255, 255))
    heat_point_4_text_rect = heat_point_4_text.get_rect(center=(heat_point_4_surface.get_width()/2, heat_point_4_surface.get_height()/2))
    
    heat_point_5_text = font.render("heat point 5", True, (255, 255, 255))
    heat_point_5_text_rect = heat_point_5_text.get_rect(center=(heat_point_5_surface.get_width()/2, heat_point_5_surface.get_height()/2))
    
    heat_point_6_text = font.render("heat point 6", True, (255, 255, 255))
    heat_point_6_text_rect = heat_point_6_text.get_rect(center=(heat_point_6_surface.get_width()/2, heat_point_6_surface.get_height()/2))
    
    heat_point_7_text = font.render("heat point 7", True, (255, 255, 255))
    heat_point_7_text_rect = heat_point_7_text.get_rect(center=(heat_point_7_surface.get_width()/2, heat_point_7_surface.get_height()/2))
    
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
    heat_point_1_display = pygame.Rect(1580, 100, 200, 100)
    heat_point_2_display = pygame.Rect(1140, 250, 200, 100)
    heat_point_3_display = pygame.Rect(1360, 250, 200, 100)
    heat_point_4_display = pygame.Rect(1580, 250, 200, 100)
    heat_point_5_display = pygame.Rect(1140, 400, 200, 100)
    heat_point_6_display = pygame.Rect(1360, 400, 200, 100)
    heat_point_7_display = pygame.Rect(1580, 400, 200, 100)
    
    
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
                                print("Find heat point")
                                traj_state = "find heat point WP0"
                                find_survivor_event.set()
                                wP0.set()
                                wP1.clear()
                                wP2.clear()
                                wP3.clear()
                                wP4.clear()
                                wP5.clear()
                                return_home.clear()
                                fly_to_heat_pointe_1.clear()
                                fly_to_heat_pointe_2.clear()
                                fly_to_heat_pointe_3.clear()
                                
                            if return_home_display.collidepoint(event.pos):
                                print("Return home")
                                traj_state = "retrun home WP12"
                                nothing_detected.set()
                                fire.clear()
                                survivor.clear()
                                hazardous_material.clear()
                                map.clear()
                                start_handover.clear()
                                validate_handover.clear()
                                return_home.set()
                                wP12.set()
                                wP13.clear()
                                find_survivor_event.clear()
                                fly_to_heat_pointe_1.clear()
                                fly_to_heat_pointe_2.clear()
                                fly_to_heat_pointe_3.clear()
                                fly_to_heat_pointe_5.clear()
                                fly_to_heat_pointe_6.clear()
                                fly_to_heat_pointe_7.clear()
                                
                            if heat_point_1_display.collidepoint(event.pos):
                                print("heat_point 1")
                                traj_state = "heat_point 1"
                                fly_to_heat_pointe_1.set()
                                find_survivor_event.clear()
                                return_home.clear()
                                fly_to_heat_pointe_2.clear()
                                fly_to_heat_pointe_3.clear()
                                fly_to_heat_pointe_4.clear()
                                fly_to_heat_pointe_5.clear()
                                fly_to_heat_pointe_6.clear()
                                fly_to_heat_pointe_7.clear()
                                
                            if heat_point_2_display.collidepoint(event.pos):
                                print("heat_point 2")
                                traj_state = "heat_point 2"
                                fly_to_heat_pointe_2.set()
                                find_survivor_event.clear()
                                return_home.clear()
                                fly_to_heat_pointe_1.clear()
                                fly_to_heat_pointe_3.clear()
                                fly_to_heat_pointe_4.clear()
                                fly_to_heat_pointe_5.clear()
                                fly_to_heat_pointe_6.clear()
                                fly_to_heat_pointe_7.clear()
                                
                            if heat_point_3_display.collidepoint(event.pos):
                                print("heat_point 3")
                                traj_state = "heat_point 3"
                                fly_to_heat_pointe_3.set()
                                find_survivor_event.clear()
                                return_home.clear()
                                fly_to_heat_pointe_1.clear()
                                fly_to_heat_pointe_2.clear()
                                fly_to_heat_pointe_4.clear()
                                fly_to_heat_pointe_5.clear()
                                fly_to_heat_pointe_6.clear()
                                fly_to_heat_pointe_7.clear()
                                
                            if heat_point_4_display.collidepoint(event.pos):
                                print("heat_point 4")
                                traj_state = "heat_point 4"
                                fly_to_heat_pointe_4.set()
                                find_survivor_event.clear()
                                return_home.clear()
                                fly_to_heat_pointe_1.clear()
                                fly_to_heat_pointe_2.clear()
                                fly_to_heat_pointe_3.clear()
                                fly_to_heat_pointe_5.clear()
                                fly_to_heat_pointe_6.clear()
                                fly_to_heat_pointe_7.clear()
                                
                            if heat_point_5_display.collidepoint(event.pos):
                                print("heat_point 5")
                                traj_state = "heat_point 5"
                                fly_to_heat_pointe_5.set()
                                find_survivor_event.clear()
                                return_home.clear()
                                fly_to_heat_pointe_1.clear()
                                fly_to_heat_pointe_2.clear()
                                fly_to_heat_pointe_3.clear()
                                fly_to_heat_pointe_4.clear()
                                fly_to_heat_pointe_6.clear()
                                fly_to_heat_pointe_7.clear()
                            
                            if heat_point_6_display.collidepoint(event.pos):
                                print("heat_point 6")
                                traj_state = "heat_point 6"
                                fly_to_heat_pointe_6.set()
                                find_survivor_event.clear()
                                return_home.clear()
                                fly_to_heat_pointe_1.clear()
                                fly_to_heat_pointe_2.clear()
                                fly_to_heat_pointe_3.clear()
                                fly_to_heat_pointe_4.clear()
                                fly_to_heat_pointe_5.clear()
                                fly_to_heat_pointe_7.clear()
                            
                            if heat_point_7_display.collidepoint(event.pos):
                                print("heat_point 7")
                                traj_state = "heat_point 7"
                                fly_to_heat_pointe_7.set()
                                find_survivor_event.clear()
                                return_home.clear()
                                fly_to_heat_pointe_1.clear()
                                fly_to_heat_pointe_2.clear()
                                fly_to_heat_pointe_3.clear()
                                fly_to_heat_pointe_4.clear()
                                fly_to_heat_pointe_5.clear()
                                fly_to_heat_pointe_6.clear()
                                
                                
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
                            
                        if heat_point_1_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(heat_point_1_surface, (0, 0, 255), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(heat_point_1_surface, (0, 0, 128), (1, 1, 198, 98))
                        
                        if heat_point_2_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(heat_point_2_surface, (0, 0, 255), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(heat_point_2_surface, (0, 0, 128), (1, 1, 198, 98))
                            
                        if heat_point_3_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(heat_point_3_surface, (0, 0, 255), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(heat_point_3_surface, (0, 0, 128), (1, 1, 198, 98))
                        
                        if heat_point_4_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(heat_point_4_surface, (0, 0, 255), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(heat_point_4_surface, (0, 0, 128), (1, 1, 198, 98))
                        
                        if heat_point_5_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(heat_point_5_surface, (0, 0, 255), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(heat_point_5_surface, (0, 0, 128), (1, 1, 198, 98))
                            
                        if heat_point_6_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(heat_point_6_surface, (0, 0, 255), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(heat_point_6_surface, (0, 0, 128), (1, 1, 198, 98))
                            
                        if heat_point_7_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(heat_point_7_surface, (0, 0, 255), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(heat_point_7_surface, (0, 0, 128), (1, 1, 198, 98))
                             
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
                    heat_point_1_surface.blit(heat_point_1_text, heat_point_1_text_rect)
                    heat_point_2_surface.blit(heat_point_2_text, heat_point_2_text_rect)
                    heat_point_3_surface.blit(heat_point_3_text, heat_point_3_text_rect)
                    heat_point_4_surface.blit(heat_point_4_text, heat_point_4_text_rect)
                    heat_point_5_surface.blit(heat_point_5_text, heat_point_5_text_rect)
                    heat_point_6_surface.blit(heat_point_6_text, heat_point_6_text_rect)
                    heat_point_7_surface.blit(heat_point_7_text, heat_point_7_text_rect)
                    
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
                    screen.blit(heat_point_1_surface, (heat_point_1_display.x, heat_point_1_display.y))
                    screen.blit(heat_point_2_surface, (heat_point_2_display.x, heat_point_2_display.y))
                    screen.blit(heat_point_3_surface, (heat_point_3_display.x, heat_point_3_display.y))
                    screen.blit(heat_point_4_surface, (heat_point_4_display.x, heat_point_4_display.y))
                    screen.blit(heat_point_5_surface, (heat_point_5_display.x, heat_point_5_display.y))
                    screen.blit(heat_point_6_surface, (heat_point_6_display.x, heat_point_6_display.y))
                    screen.blit(heat_point_7_surface, (heat_point_7_display.x, heat_point_7_display.y))
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


        
     
        
def main():
    
    display_button()





if __name__=="__main__":
    main()
