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

# system event
pygame_ready = threading.Event()
failure = threading.Event()
anim_set = threading.Event()
log_ready = threading.Event()

#trajectory event
next_pose = threading.Event()

#animation event
fire = threading.Event()
hazardous_material = threading.Event()
survivor = threading.Event()
map = threading.Event()
start_handover = threading.Event()
validate_handover = threading.Event()
nothing_detected = threading.Event()
standby = threading.Event()

lastLogMessage = ''
logMessage = ''

def display_approach_pattern(tello):
    pygame_ready.wait()
    print("entered display thread!")
    # tello.send_expansion_command("mled sc")

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
                               "00bbbb00000bb000000bb000000pb00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000bb000000bb000000pp00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000bb000000bp000000pr00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000bb000000pp000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000pb000000rp000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000pp000000rr000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0",
                               "00bbbb00000rr000000rr000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0"]
    
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
    
    start_handover_anim = ["00000000000000000000000000pppp0000ppppp00pppppp00pppppp000pppp00",
                           "00000000000p00000p0p0p000p0p0p0000pppp0p00ppppp00pppppp000pppp00",
                           "000p00000p0p0p000p0p0p000p0p0p0p00pppp0pp0ppppp00pppppp000pppp00"]
    
    validate_handover_anim = ["000000000000000000pppp00bbppppp0bbppppp0bbppppp0bbppppp000000000",
                              "000000000000pp0000ppp000bbppppp0bbppppp0bbppppp0bbppppp000000000",
                              "0000p000000pp00000pp0000bbppppp0bbppppp0bbppppp0bbppppp000000000"]
    
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
                tello.send_expansion_command("mled g " + survivor_anim[cycleStep % 5])
                start_pattern = time.time()
                cycleStep += 1  

        elif(hazardous_material.is_set()):        
            if(time.time() - start_pattern > 0.1):
                tello.send_expansion_command("mled g " + hazardous_material_anim[cycleStep % 8])
                start_pattern = time.time()
                cycleStep += 1 

        elif(map.is_set()):
            if(time.time() - start_pattern > 0.1):
                tello.send_expansion_command("mled g " + map_anim[cycleStep % 11])
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
        
        elif(nothing_detected.is_set()):
            tello.send_expansion_command("mled sc")
            nothing_detected.clear()
            standby.set()
            
        # else:
        #     print('The pattern does not exist')


# To set a random animation use a random variable as choice
def choose_animation(choice):
    global logMessage
    if choice == 1:
        #print("fire seen!")
        logMessage = "fire displayed"
        standby.clear()
        survivor.clear()
        hazardous_material.clear()
        map.clear()
        start_handover.clear()
        validate_handover.clear()
        fire.set()
    
    elif choice == 2:
        #print("survivor seen!")
        logMessage = "survivor displayed"
        standby.clear()
        fire.clear()
        hazardous_material.clear()
        map.clear()
        start_handover.clear()
        validate_handover.clear()
        survivor.set()
        
    elif choice == 3:
        #print("hazardous materials seen!")
        logMessage = "hazardous materials displayed"
        standby.clear()
        fire.clear()
        survivor.clear()                    
        map.clear()
        start_handover.clear()
        validate_handover.clear()
        hazardous_material.set()
        
    elif choice == 4:
        #print("mapping seen!")
        logMessage = "mapping displayed"
        standby.clear()
        fire.clear()
        survivor.clear()
        hazardous_material.clear()
        start_handover.clear()
        validate_handover.clear()
        map.set()

    elif choice == 5:
        #print("start handover seen!")
        logMessage = "start handover displayed"
        standby.clear()
        fire.clear()
        survivor.clear()
        hazardous_material.clear()
        map.clear()
        validate_handover.clear()
        start_handover.set()
        
    elif choice == 6:
        #print("validate handover seen!")
        logMessage = "validate handover displayed"
        standby.clear()
        fire.clear()
        survivor.clear()
        hazardous_material.clear()
        map.clear()
        start_handover.clear()
        validate_handover.set()
    else:
        print("warning choice out of range")
        

def display_button():
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
    log_ready.set()
    pygame.init()
    clock = pygame.time.Clock()    
    
    pygame_logger = logging.getLogger('PygameLogger')
    pygame_handler = logging.FileHandler('Log_proxemics_angles_{expeNb}.log'.format(expeNb = text), mode="w")
    pygame_handler.setLevel(logging.DEBUG)
    pygame_formatter = logging.Formatter('%(asctime)s - %(message)s')
    pygame_handler.setFormatter(pygame_formatter)
    pygame_logger.addHandler(pygame_handler)
    pygame_logger.setLevel(logging.DEBUG)
    
    global logMessage
    global lastLogMessage
    
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
                    
        if(logMessage != lastLogMessage):
            pygame_logger.info(logMessage)
            lastLogMessage = logMessage
                    
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
    log_ready.wait()
    file = open('proxemics_angles_sequence_1.json')
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
            if ((time.time()-starttime > 0.01)):
                if(lastPointReached == False):
                    # tester ces trois prochaines lignes dans la condition if(wPCounter <= lengthWPs-1):
                    swarm.tellos[0].fly_to_enu([wPListPos[wPCounter][0], wPListPos[wPCounter][1], wPListPos[wPCounter][2]], wPListHeading[wPCounter])
                    dist = euclidean_distance(swarm.tellos[0].position_enu, wPListPos[wPCounter])
                    angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[wPCounter])
                
                    
                # reaches the position of the currently loaded waypoint close enough in distance and angle
                
                if(wPCounter < lengthWPs-1):
                    if next_pose.is_set():
                        wPCounter += 1
                        nothing_detected.set()
                        next_pose.clear()
                        anim_set.clear()
                        dist = euclidean_distance(swarm.tellos[0].position_enu, wPListPos[wPCounter])
                        angle = heading_distance(swarm.tellos[0].get_heading(), wPListHeading[wPCounter])
                    
                    if(dist <= epsilonDist and (angle %(2*math.pi)<= minepsilonAngle or angle%(2*math.pi) >= maxepsilonAngle)):                            
                        if (not anim_set.is_set()):
                            anim_set.set()
                            choose_animation(random.randint(1, 6))
                            
                        print("position: ",swarm.tellos[0].position_enu," battery: ",swarm.tellos[0].get_battery(), " way point number: ", wPCounter, " distance to goal: ", dist, " angle to goal: ", angle)
                        print("WP number: ", wPCounter)
                else:
                    lastPointReached = True
                    logMessage = 'end of mission'
                    
                starttime= time.time()
                        
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
    vehicles = dict([(ac_id, swarm.tellos[i]) for i,ac_id in enumerate(id_dict.keys())])
    voliere = VolierePosition(id_dict, vehicles, freq=100, vel_samples=6)

    voliere.run()
    sleep(2)
    print("Starting Natnet3.x interface at %s" % ("1234567"))
    print('threading running')
    
    pygame_thread = threading.Thread(target=display_button, args=())
    pygame_thread.daemon = True
    pygame_thread.start()
    # # flight_routine()
    # # display_button()
    display_thread = threading.Thread(target=display_approach_pattern, args=(swarm.tellos[0],))
    display_thread.daemon = True
    display_thread.start()

    flight_routine(swarm, voliere)





if __name__=="__main__":
    main()
