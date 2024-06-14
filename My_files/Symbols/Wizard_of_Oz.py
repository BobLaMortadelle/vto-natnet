import pygame
import sys
import time
from djitellopy import Tello
import threading

pygam_ready = threading.Event()
fire = threading.Event()
hazardous_material = threading.Event()
survivor = threading.Event()
map = threading.Event()
failure = threading.Event()
nothing_detected = threading.Event()
standby = threading.Event()

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

def flight_routine():
    start_pattern = time.time()
    while(True):
        if(time.time() - start_pattern > 0.1):
            print("fly")
            start_pattern = time.time()

def main():
    tello = Tello()
    tello.connect()
    pygame_thread = threading.Thread(target=display_button, args=())
    pygame_thread.daemon = True
    pygame_thread.start()
    
    display_thread = threading.Thread(target=display_approach_pattern, args=(tello,))
    display_thread.daemon = True
    display_thread.start()
    
    flight_routine()
    
        



        
        
    
if __name__=="__main__":
    main()
    
