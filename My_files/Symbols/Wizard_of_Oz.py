import pygame
import sys
import time
from djitellopy import Tello
import threading
import logging 
import random
from logging_filter import ExcludeFilter
pygam_ready = threading.Event()
fire = threading.Event()
hazardous_material = threading.Event()
survivor = threading.Event()
map = threading.Event()
failure = threading.Event()
nothing_detected = threading.Event()
standby = threading.Event()

# system event
next_pose = threading.Event()
anim_set = threading.Event()
log_ready = threading.Event()

lastLogMessage = ''
logMessage = ''

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

def choose_animation(choice):
    global logMessage
    if choice == 1:
        print("fire seen!")
        logMessage ="fire displayed"
        standby.clear()
        survivor.clear()
        hazardous_material.clear()
        map.clear()
        fire.set()
    
    elif choice == 2:
        print("survivor seen!")
        logMessage = "survivor displayed"
        standby.clear()
        fire.clear()
        hazardous_material.clear()
        map.clear()
        survivor.set()
        
    elif choice == 3:
        print("hazardous materials seen!")
        logMessage = "hazardous materials displayed"
        standby.clear()
        fire.clear()
        survivor.clear()                    
        map.clear()
        hazardous_material.set()
        
    elif choice == 4:
        print("mapping seen!")
        logMessage = "mapping displayed"
        standby.clear()
        fire.clear()
        survivor.clear()
        hazardous_material.clear()
        map.set()
        
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
    text =''
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
    pygame_handler = logging.FileHandler('wizard_of_Oz_{expeNb}.log'.format(expeNb = text), mode="w")
    pygame_handler.setLevel(logging.DEBUG)
    pygame_formatter = logging.Formatter('%(asctime)s - %(message)s')
    pygame_handler.setFormatter(pygame_formatter)
    pygame_logger.addHandler(pygame_handler)
    pygame_logger.setLevel(logging.DEBUG)
    # Add the custom logging filter
    # exclude_filter = ExcludeFilter()
    # pygame_logger.addFilter(exclude_filter)
    
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
    global logMessage
    global lastLogMessage
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
                    # print("fire seen!")
                    # standby.clear()
                    # survivor.clear()
                    # hazardous_material.clear()
                    # map.clear()
                    # fire.set()
                    logMessage = "fire button clicked"
                    
                    
                if survivor_display.collidepoint(event.pos):
                    print("survivor seen!")
                    # standby.clear()
                    # fire.clear()
                    # hazardous_material.clear()
                    # map.clear()
                    # survivor.set()
                    logMessage = "survivor button clicked"
                    
                if hazardous_materials_display.collidepoint(event.pos):
                    print("hazardous materials seen!")
                    # standby.clear()
                    # fire.clear()
                    # survivor.clear()                    
                    # map.clear()
                    # hazardous_material.set()
                    logMessage = "hazardous materials button clicked"
                    
                if mapping_display.collidepoint(event.pos):
                    print("mapping seen!")
                    # standby.clear()
                    # fire.clear()
                    # survivor.clear()
                    # hazardous_material.clear()
                    # map.set()
                    logMessage = "mapping button button clicked"
                
                if nothing_detected_display.collidepoint(event.pos):
                    print("Next WP!")
                    logMessage = "next waypoint button clicked"
                    next_pose.set()
                    standby.clear()
                    fire.clear()
                    survivor.clear()
                    hazardous_material.clear()
                    map.clear()

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

def flight_routine():
    log_ready.wait()
    start_pattern = time.time()
    checkpoint = time.time() + 3
    lastPointReached = False
    wPCounter = 0
    while(True):
        if(lastPointReached == True):
            break
        if(time.time() - start_pattern > 0.1):
            start_pattern = time.time()
            print("fly")
            if(wPCounter <= 10):
                if next_pose.is_set():
                    wPCounter += 1
                    nothing_detected.set()
                    next_pose.clear()
                    anim_set.clear()
                if(checkpoint < time.time()):
                    checkpoint = time.time() + 3
                    if (not anim_set.is_set()):
                        anim_set.set()
                        choose_animation(random.randint(1, 4))
            
                    
            

def main():
    tello = Tello()
    tello.connect()
    pygame_thread = threading.Thread(target=display_button, args=())
    pygame_thread.daemon = True
    pygame_thread.start()
    # display_button()
    display_thread = threading.Thread(target=display_approach_pattern, args=(tello,))
    display_thread.daemon = True
    display_thread.start()
    
    flight_routine()
    
        



        
        
    
if __name__=="__main__":
    main()
    
