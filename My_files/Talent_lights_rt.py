from djitellopy import Tello
import time

class LightsOn:
    def __init__(self, pattern='searching', iteration=5):
        self.pattern = pattern
        self.iteration = iteration

    def display_approach_pattern(self, tello):
        tello.send_expansion_command("led 0 0 0")
        tello.send_expansion_command("mled sc")

        if(self.pattern == 'searching'):
            # chase for searching
            chase = ["{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(66)+"{0:08b}".format(132),
            "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(34)+"{0:08b}".format(17),
            "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(17)+"{0:08b}".format(34),
            "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(132)+"{0:08b}".format(66)]
            start_pattern = time.time()
            tello.send_expansion_command("led br 2.5 75 75 255")
            nbcycle = 0
            cycleStep = 0
            while(nbcycle < self.iteration):
                while(cycleStep <4):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + chase[cycleStep].replace('1', 'b'))
                        start_pattern = time.time()
                        cycleStep += 1
                cycleStep = 0
                nbcycle += 1
            tello.send_expansion_command("mled sc")
            tello.send_expansion_command("led 0 0 0")

        elif(self.pattern == 'spotting'):
            # morse for spotting
            morse = "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102)
            nbcycle = 0
            cycleStep = 0
            start_pattern = time.time()
            gapMorse = time.time()
            matriceOn = False
            tello.send_expansion_command("led br 2.5 255 0 0")
            while(nbcycle < self.iteration):
                if(time.time() - gapMorse > 1):
                    while(cycleStep <5):
                        delay = time.time() - start_pattern
                        if(delay > 0.1 and delay < 0.3 and matriceOn == False):
                            tello.send_expansion_command("mled g " + morse.replace('1', 'r'))
                            matriceOn = True
                        elif(delay > 0.3 and delay < 0.4 and matriceOn == True):
                            tello.send_expansion_command("mled sc")
                            matriceOn = False
                        elif(delay > 0.4):
                            start_pattern = time.time()
                            cycleStep += 1
                    gapMorse = time.time()
                    cycleStep = 0
                    nbcycle += 1
            tello.send_expansion_command("mled sc")
            tello.send_expansion_command("led 0 0 0")    

        elif(self.pattern == 'approaching'):        
            # onedecent for approaching
            onedecent = ["{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102),
                        "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153),
                        "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153),
                        "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)]
            start_pattern = time.time()
            tello.send_expansion_command("led br 0.15 255 100 0")
            nbcycle = 0
            cycleStep = 0
            while(nbcycle < self.iteration):
                while(cycleStep < 4):
                    if(time.time() - start_pattern > 0.1):
                        tello.send_expansion_command("mled g " + onedecent[cycleStep].replace('1', 'p'))
                        start_pattern = time.time()
                        cycleStep += 1
                cycleStep = 0
                nbcycle += 1
            tello.send_expansion_command("mled sc")
            tello.send_expansion_command("led 0 0 0")

        elif(self.pattern == 'interacting'):
            # solid for ready to interact
            solid = "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102)
            start_pattern = time.time()
            tello.send_expansion_command("led 0 255 0")
            tello.send_expansion_command("mled g " + solid.replace('1', 'b'))
            solidLightOn = True
            while(solidLightOn == True):
                if(time.time() - start_pattern > self.iteration):
                    tello.send_expansion_command("mled sc")
                    tello.send_expansion_command("led 0 0 0")
                    solidLightOn = False
        else:
            print('The following pattern does not exist: ', self.pattern)

# tello = Tello()
# tello.connect()
# display_approach_pattern(tello, 'searching')
# display_approach_pattern(tello, 'spotting')
# display_approach_pattern(tello, 'approaching')
# display_approach_pattern(tello, 'interacting')