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
fire = threading.Event()
hazardous_material = threading.Event()
survivor = threading.Event()
map = threading.Event()
start_handover = threading.Event()
validate_handover = threading.Event()
med_kit = threading.Event()
interrogation = threading.Event()
snail = threading.Event()
tall_blue_guy = threading.Event()
water_pipe = threading.Event()
dangerous_leak = threading.Event()
ok = threading.Event()
purple_guy = threading.Event()
handover_text = threading.Event()
digit_1 = threading.Event()
digit_2 = threading.Event()
digit_3 = threading.Event()
digit_4 = threading.Event()
digit_5 = threading.Event()
digit_6 = threading.Event()
digit_7 = threading.Event()
digit_8 = threading.Event()
digit_9 = threading.Event()


lock = threading.Lock()


lastLogMessage = ''
logMessage = ''
logWP = ''
lastLogWP = ''
fileNumber = ''

def display_approach_pattern(tello):
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
                              "0000p000000pp00000pp0000bbppppp0bbppppp0bbppppp0bbppppp000000000"]
    
    med_kit_anim = ["bbbbbbbbbbbrrbbbbbbrrbbbbrrrrrrbbrrrrrrbbbbrrbbbbbbrrbbbbbbbbbbb",
                    "bbbbbbbbbbb00bbbbbb00bbbb000000bb000000bbbb00bbbbbb00bbbbbbbbbbb"]
    
    interrogation_anim = ["00rrrr000rr00rr000000rr00000rr00000rr00000000000000rr00000000000",
                          "0000000000rrrr000rr00rr000000rr00000rr00000rr00000000000000rr000"]
    
    snail_anim = ["00000000000000000000r000000b0bb000b0bbbb00b0bbbb000b0bb00000bbbb",
             "0000000000r0000000b0000000b00bb000b0bbbb00b0bbbb000b0bb00000bbbb",
             "00000000000000000r0000000b000bb00b00bbbb0b00bbbb00b00bb0000bbbbb",
             "00000000000000000000000000000bb0r000bbbb0b00bbbb00b00bb0000bbbbb",
             "00000000000000000r0000000b000bb00b00bbbb0b00bbbb00b00bb0000bbbbb",
             "0000000000r0000000b0000000b00bb000b0bbbb00b0bbbb000b0bb00000bbbb"]
    
    tall_blue_guy_anim = ["0000000000000bb00000bbbbr000bbbb0b000bb000bbbbbb0000bbbb0000bbbb",
             "0000000000000bb00r00bbbb0b00bbbb0b000bb000bbbbbb0000bbbb0000bbbb",
             "0000000000r00bb000b0bbbb00b0bbbb00b00bb0000bbbbb0000bbbb0000bbbb",
             "00000000000r0bb000b0bbbb00b0bbbb00b00bb0000bbbbb0000bbbb0000bbbb",
             "0000000000r00bb000b0bbbb00b0bbbb00b00bb0000bbbbb0000bbbb0000bbbb",
             "0000000000000bb00r00bbbb0b00bbbb0b000bb000bbbbbb0000bbbb0000bbbb"]
    
    water_pipe_anim = ["0000000000000000000000000000000000000000pppppppppppppppp00000000",
                "00000000000000000000000000000000000bb000pppbb000pppbpppp0000pppp",
                "00000000000000000000000000bbbb0000bbbb00pppbbb00pppbpppp0000pppp",
                "000000000b0bb000bbbbbb000bbbbbbb00bbbbbbpppbbb00pppbpppp0000pppp",
                "0bb0bbbbbbbbbbbbbbbbbbbbbbbbbbbb00bbbbbbpppbbb00pppbpppp0000pppp",]
    
    dangerous_leak_anim = ["00000000pppppppppppppppp0000000000000000000000000000000000000000",
             "0000000000bb0000pppbb000pppbpppp00bbpppp00bb00000000000000000000",
             "00bbb00000bbbb00pppbbb00pppbpppp0bbbpppp0bbbb0000bbbb00000000000",
             "0bbbbbb000bbbb00pppbb000pppbpppp0bbbppppbbbbb000bbbbb0000bbb0000",
             "bbbbbbbb0bbbbbbbpppbbb00pppbpppp0bbbppppbbbbbb00bbbbbb00bbbbbbb0",
             "rrrrrrrr0rrrrrrrppprrr00ppprpppp00rrpppprrrrrr00rrrrrr00rrrrrrr0"]
    
    purple_guy_anim = ["0000000000pp00000pppp00r0pppp00b00pp00b00bppbb00bpppp000bpppp000",
                       "0000000000pp00000pppp0r00pppp0b000pp00b00bppbb00bpppp000bpppp000",
                       "0000000000pp00000ppppr000ppppb0000pp0b000bppbb00bpppp000bpppp000",
                       "0000000000pp00000pprp0000pppb00000pp0b000bppbb00bpppp000bpppp000",
                       "0000000000pp00000ppppr000ppppb0000pp0b000bppbb00bpppp000bpppp000",
                       "0000000000pp00000pppp0r00pppp0b000pp00b00bppbb00bpppp000bpppp000"]
    
    
    

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
                        tello.send_expansion_command("mled g " + fire_anim[cycleStep % 4])
                        start_pattern = time.time()
                        cycleStep += 1

                elif(survivor.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + survivor_anim[cycleStep % 5])
                        start_pattern = time.time()
                        cycleStep += 1  

                elif(hazardous_material.is_set()):        
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + hazardous_material_anim[cycleStep % 5])
                        start_pattern = time.time()
                        cycleStep += 1 

                elif(map.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + map_anim[cycleStep % 6])
                        start_pattern = time.time()
                        cycleStep += 1 
                
                elif(start_handover.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + start_handover_anim[cycleStep % 3])
                        start_pattern = time.time()
                        cycleStep += 1
                
                elif(validate_handover.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + validate_handover_anim[cycleStep % 3])
                        start_pattern = time.time()
                        cycleStep += 1
                        
                elif(med_kit.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + med_kit_anim[cycleStep % 2])
                        start_pattern = time.time()
                        cycleStep += 1
                
                elif(interrogation.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + interrogation_anim[cycleStep % 2])
                        start_pattern = time.time()
                        cycleStep += 1
                        
                elif(snail.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + snail_anim[cycleStep % 6])
                        start_pattern = time.time()
                        cycleStep += 1
                
                elif(tall_blue_guy.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + tall_blue_guy_anim[cycleStep % 6])
                        start_pattern = time.time()
                        cycleStep += 1
                        
                elif(water_pipe.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + water_pipe_anim[cycleStep % 5])
                        start_pattern = time.time()
                        cycleStep += 1
                        
                elif(dangerous_leak.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + dangerous_leak_anim[cycleStep % 6])
                        start_pattern = time.time()
                        cycleStep += 1
                
                elif(purple_guy.is_set()):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + purple_guy_anim[cycleStep % 6])
                        start_pattern = time.time()
                        cycleStep += 1
                        
                elif(ok.is_set()):
                    tello.send_expansion_command("mled g 00000000pppp0p00p00p0p0pp00p0p0pp00p0pp0p00p0p0ppppp0p0p00000000")
                    ok.clear()
                    standby.set()
                    
                elif(handover_text.is_set()):
                    tello.send_expansion_command("mled l p 2.5 Handover ")
                    handover_text.clear()
                    standby.set()
                    
                elif(digit_1.is_set()):
                    tello.send_expansion_command("mled s p 1")
                    digit_1.clear()
                    standby.set()
                    
                elif(digit_2.is_set()):
                    tello.send_expansion_command("mled s p 2")
                    digit_2.clear()
                    standby.set()
                    
                elif(digit_3.is_set()):
                    tello.send_expansion_command("mled s p 3")
                    digit_3.clear()
                    standby.set()
                
                elif(digit_4.is_set()):
                    tello.send_expansion_command("mled s p 4")
                    digit_4.clear()
                    standby.set()
                
                elif(digit_5.is_set()):
                    tello.send_expansion_command("mled s p 5")
                    digit_5.clear()
                    standby.set()
                
                elif(digit_6.is_set()):
                    tello.send_expansion_command("mled s p 6")
                    digit_6.clear()
                    standby.set()
                
                elif(digit_7.is_set()):
                    tello.send_expansion_command("mled s p 7")
                    digit_7.clear()
                    standby.set()
                
                elif(digit_8.is_set()):
                    tello.send_expansion_command("mled s p 8")
                    digit_8.clear()
                    standby.set()
                
                elif(digit_9.is_set()):
                    tello.send_expansion_command("mled s p 9")
                    digit_9.clear()
                    standby.set()
                        
                elif(nothing_detected.is_set()):
                    if not standby.is_set():
                        tello.send_expansion_command("mled sc")
                        standby.set()
                    nothing_detected.clear()
            finally:
                lock.release()
            start_light = time.time()
                
            

# To set a random animation use a random variable as choice
def choose_animation(choice):
    global logMessage
    if choice == 1:
        logMessage = "fire displayed"
        fire.set()
    
    elif choice == 2:
        logMessage = "survivor displayed"
        survivor.set()
        
    elif choice == 3:
        logMessage = "hazardous materials displayed"
        hazardous_material.set()
        
    elif choice == 4:
        logMessage = "mapping displayed"
        map.set()

    elif choice == 5:
        logMessage = "start handover displayed"
        start_handover.set()
        
    elif choice == 6:
        logMessage = "validate handover displayed"
        validate_handover.set()
        
    elif choice == 7:
        logMessage = "med kit displayed"
        med_kit.set()
        
    elif choice == 8:
        logMessage = "interrogation displayed"
        interrogation.set()
        
    elif choice == 9:
        logMessage = "snail displayed"
        snail.set()
        
    elif choice == 10:
        logMessage = "tall blue guy displayed"
        tall_blue_guy.set()
        
    elif choice == 11:
        logMessage = "water pipe displayed"
        water_pipe.set()
        
    elif choice == 12:
        logMessage = "dangerous leak displayed"
        dangerous_leak.set()
        
    elif choice == 13:
        logMessage = "purple guy displayed"
        purple_guy.set()
    
    elif choice == 14:
        logMessage = "ok displayed"
        ok.set()
                
    elif choice == 15:
        logMessage = "handover text displayed"
        handover_text.set()
        
    elif choice == 16:
        logMessage = "1 displayed"
        digit_1.set()
        
    elif choice == 17:
        logMessage = "2 displayed"
        digit_2.set()
        
    elif choice == 18:
        logMessage = "3 displayed"
        digit_3.set()
        
    elif choice == 19:
        logMessage = "4 displayed"
        digit_4.set()
        
    elif choice == 20:
        logMessage = "5 displayed"
        digit_5.set()
        
    elif choice == 21:
        logMessage = "6 displayed"
        digit_6.set()
        
    elif choice == 22:
        logMessage = "7 displayed"
        digit_7.set()
        
    elif choice == 23:
        logMessage = "8 displayed"
        digit_8.set()
        
    elif choice == 24:
        logMessage = "9 displayed"
        digit_9.set()
        
    else:
        print("warning choice out of range")
        

def display_button():
    global logMessage
    global lastLogMessage
    global logWP
    global lastLogWP    
    global fileNumber
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
    
    
    pygame.init()
    clock = pygame.time.Clock()
    is_display = True
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    window_size = (220,50)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('File number: ')
    # Create a font object
    font = pygame.font.Font(None, 32)
    # Input box
    input_box = pygame.Rect(10, 10, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
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
                        print(fileNumber)
                        pygame.quit()
                        is_display = False
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        fileNumber = fileNumber[:-1]
                    else:
                        fileNumber += event.unicode
        if(is_display):
            screen.fill(WHITE)
            # Render the current text
            txt_surface = font.render(fileNumber, True, BLACK)
            # Resize the box if the text is too long
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            # Blit the text
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            # Blit the input_box rect
            pygame.draw.rect(screen, color, input_box, 2)

            pygame.display.flip()
            clock.tick(30)
            
            
    pygame_logger = logging.getLogger('PygameLogger')
    pygame_handler = logging.FileHandler('Log_proxemics_angles_{userNb}_{expeNb}.log'.format(userNb = text, expeNb = fileNumber), mode="w")
    pygame_handler.setLevel(logging.DEBUG)
    pygame_formatter = logging.Formatter('%(asctime)s - %(message)s')
    pygame_handler.setFormatter(pygame_formatter)
    pygame_logger.addHandler(pygame_handler)
    pygame_logger.setLevel(logging.DEBUG)
    log_ready.set()
    
    
    pygame.init()
    clock = pygame.time.Clock() 
    # Initializing surface
    window_size = (800,800)
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
    next_WP_surface = pygame.Surface((200, 100))
    
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
    
    next_WP_text = font.render("Next WP", True, (255, 255, 255))
    next_WP_text_rect = next_WP_text.get_rect(center=(next_WP_surface.get_width()/2, next_WP_surface.get_height()/2))
    
    # Create a pygame.Rect object that represents the button's boundaries
    fire_display = pygame.Rect(125, 100, 200, 100)  # Adjust the position as needed
    survivor_display  = pygame.Rect(475, 100, 200, 100) 
    hazardous_materials_display  = pygame.Rect(125, 250, 200, 100)
    mapping_display  = pygame.Rect(475, 250, 200, 100)
    start_handover_display  = pygame.Rect(125, 400, 200, 100)
    validate_handover_display  = pygame.Rect(475, 400, 200, 100)
    next_WP_display = pygame.Rect(300, 550, 200, 100)
    
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
                                print("fire seen!")
                                logMessage = "fire button clicked"
                                # standby.clear()
                                # survivor.clear()
                                # hazardous_material.clear()
                                # map.clear()
                                # fire.set()
                                
                            if survivor_display.collidepoint(event.pos):
                                print("survivor seen!")
                                logMessage = "survivor button clicked"
                                # standby.clear()
                                # fire.clear()
                                # hazardous_material.clear()
                                # map.clear()
                                # survivor.set()
                                
                            if hazardous_materials_display.collidepoint(event.pos):
                                print("hazardous materials seen!")
                                logMessage = "hazardous materials button clicked"
                                # standby.clear()
                                # fire.clear()
                                # survivor.clear()                    
                                # map.clear()
                                # hazardous_material.set()
                                
                            if mapping_display.collidepoint(event.pos):
                                print("mapping seen!")
                                logMessage = "mapping button button clicked"
                                # standby.clear()
                                # fire.clear()
                                # survivor.clear()
                                # hazardous_material.clear()
                                # map.set()
                            
                            if start_handover_display.collidepoint(event.pos):
                                print("start handover seen!")
                                logMessage = "start handover button clicked"
                                # standby.clear()
                                # fire.clear()
                                # survivor.clear()
                                # hazardous_material.clear()
                                # map.set()
                                
                            if validate_handover_display.collidepoint(event.pos):
                                print("validate handover seen!")
                                logMessage = "validate handover button clicked"
                                # standby.clear()
                                # fire.clear()
                                # survivor.clear()
                                # hazardous_material.clear()
                                # map.set()
                            
                            if next_WP_display.collidepoint(event.pos):
                                print("Next WP!")
                                logMessage = "next waypoint button clicked"
                                # placer les lignes suivantes avec une indentation de moins, en dehors de ce if pour que chaque boutton passe à un autre WP.
                                next_pose.set()
                                standby.clear()
                                fire.clear()
                                survivor.clear()
                                hazardous_material.clear()
                                map.clear()
                                start_handover.clear()
                                validate_handover.clear()                    
                                med_kit.clear()
                                interrogation.clear()
                                snail.clear()
                                tall_blue_guy.clear()
                                water_pipe.clear()
                                dangerous_leak.clear()
                                ok.clear()
                                purple_guy.clear()
                                handover_text.clear()
                                digit_1.clear()
                                digit_2.clear()
                                digit_3.clear()
                                digit_4.clear()
                                digit_5.clear()
                                digit_6.clear()
                                digit_7.clear()
                                digit_8.clear()
                                digit_9.clear()
                                
                    if(logMessage != lastLogMessage):
                        pygame_logger.info(logMessage)
                        lastLogMessage = logMessage
                    if(logWP != lastLogWP):
                        pygame_logger.info(logWP)
                        lastLogWP = logWP
                                
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
                            
                        if next_WP_display.collidepoint(pygame.mouse.get_pos()):
                            pygame.draw.rect(next_WP_surface, (128, 128, 128), (1, 1, 198, 98))
                        else:
                            pygame.draw.rect(next_WP_surface, (0, 0, 0), (1, 1, 198, 98))
                            
                    # Show the button text
                    fire_button_surface.blit(fire_text, fire_text_rect)
                    survivor_button_surface.blit(survivor_text, survivor_text_rect)
                    hazardous_materials_button_surface.blit(hazardous_materials_text, hazardous_materials_text_rect)
                    mapping_button_surface.blit(mapping_text, mapping_text_rect)
                    start_handover_surface.blit(start_handover_text, start_handover_text_rect)
                    validate_handover_surface.blit(validate_handover_text, validate_handover_text_rect)
                    next_WP_surface.blit(next_WP_text, next_WP_text_rect)
                    # Draw the button on the screen
                    screen.blit(fire_button_surface, (fire_display.x, fire_display.y))
                    screen.blit(survivor_button_surface, (survivor_display.x, survivor_display.y))
                    screen.blit(hazardous_materials_button_surface, (hazardous_materials_display.x, hazardous_materials_display.y))
                    screen.blit(mapping_button_surface, (mapping_display.x, mapping_display.y))
                    screen.blit(start_handover_surface, (start_handover_display.x, start_handover_display.y))
                    screen.blit(validate_handover_surface, (validate_handover_display.x, validate_handover_display.y))
                    screen.blit(next_WP_surface, (next_WP_display.x, next_WP_display.y))
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
    global fileNumber
    global logWP
    log_ready.wait()
    file = open('proxemics_angles_sequence_{expeNb}.json'.format(expeNb = fileNumber))
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
 
    global logMessage
    positionsTello = []
    positionsUser = []
    all_animations = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    file_path = 'animations_left.json'
    tmp_animations = (json.load(open(file_path)) if os.path.exists(file_path) else all_animations)

    # Simulation starts
    sim_start_time = time.time()
    print("Current Tello Battery ",swarm.tellos[0].get_battery())
    swarm.tellos[0].send_expansion_command("led 0 255 0")
    try:
        swarm.takeoff()
        lastPointReached = False
        starttime= time.time()
        actualize_height = time.time()
        z = voliere.vehicles['888'].position[2]
        while time.time()-sim_start_time < 720:
            if(lastPointReached == True):
                break
            if ((time.time()-starttime > 0.01)):
                if(lastPointReached == False):
                    # tester ces trois prochaines lignes dans la condition if(wPCounter <= lengthWPs-1):
                    if time.time() - actualize_height > 3 :
                        z = voliere.vehicles['888'].position[2] 
                        if z < 0.40:
                            z = 0.40
                        actualize_height = time.time()
                    positionsTello.append(swarm.tellos[0].position_enu)
                    positionsUser.append(voliere.vehicles['888'].position)
                    swarm.tellos[0].fly_to_enu([wPListPos[wPCounter][0], wPListPos[wPCounter][1], z], wPListHeading[wPCounter])
                    dist = euclidean_distance(swarm.tellos[0].position_enu, [wPListPos[wPCounter][0], wPListPos[wPCounter][1], z])
                    angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[wPCounter])
                
                    
                # reaches the position of the currently loaded waypoint close enough in distance and angle
                
                if(wPCounter < lengthWPs-1):
                    if next_pose.is_set():
                        wPCounter += 1
                        nothing_detected.set()
                        next_pose.clear()
                        anim_set.clear()
                        dist = euclidean_distance(swarm.tellos[0].position_enu, [wPListPos[wPCounter][0], wPListPos[wPCounter][1], z])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[wPCounter])
                    
                    if(dist <= epsilonDist and (angle %(2*math.pi)<= minepsilonAngle or angle%(2*math.pi) >= maxepsilonAngle)):                            
                        if (not anim_set.is_set()):
                            logWP = "Way point number {wPNb} at position {pos}".format(wPNb = wPCounter, pos = swarm.tellos[0].position_enu)
                            anim_set.set()
                            if not tmp_animations:
                                tmp_animations.extend(all_animations)
                            randomIndex = random.randint(0, len(tmp_animations)-1)
                            choose_animation(tmp_animations[randomIndex])
                            tmp_animations.pop(randomIndex)
                            print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " way point number: ", wPCounter, " distance to goal: ", dist, " angle to goal: ", angle)
                            print("WP number: ", wPCounter)
                else:
                    lastPointReached = True
                    logWP = 'end of mission'
                    
                starttime= time.time()
        print("Current Tello Battery ",swarm.tellos[0].get_battery())            
        swarm.move_down(int(40))
        swarm.land()
        with open('animations_left.json', 'w') as file:
            json.dump(tmp_animations, file)
        plt.figure(figsize=(12, 8))
        plt.plot(positionsTello)
        plt.title('Positions')
        plt.show()
        voliere.stop()
        swarm.end()

    except (KeyboardInterrupt, SystemExit):
        print("Shutting down natnet interfaces...")
        # log.save(flight_type='Tello')
        #swarm.move_down(int(40))
        with open('animations_left.json', 'w') as file:
            json.dump(tmp_animations, file)
        swarm.land()    
        plt.figure(figsize=(12, 8))
        plt.plot(positionsTello)
        plt.title('Positions')
        plt.show()
        voliere.stop()
        swarm.end()
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
        
        
# def flight_routine():
#     pygame_ready.wait()
#     start = time.time()
#     balise = start
#     while True:
#         if start + 0.5 < time.time():
#             print(".")
#             start = time.time()
#         if balise + 10 < time.time():
#             logging.warning("temp balise")
#             balise = start
            
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

    id_dict = dict([('244','244'), ('888','888')]) # rigidbody_ID, aircraft_ID
    vehicles = dict([('244', swarm.tellos[0]), ('888', Vehicle(['888']))])
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

    flight_routine(swarm, voliere)





if __name__=="__main__":
    main()
