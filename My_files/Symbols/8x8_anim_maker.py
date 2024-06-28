import pygame
import time
from djitellopy import Tello
def main():
    tello = Tello()
    tello.connect()
    
    # # # bright
    # # # tello.send_expansion_command("led 255 255 255")
    # tello.send_expansion_command("mled g " + "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
    # time.sleep(5)
    
    # # Medkit
    # for i in range(5):
    #     tello.send_expansion_command("mled g " + "bbbbbbbbbbbrrbbbbbbrrbbbbrrrrrrbbrrrrrrbbbbrrbbbbbbrrbbbbbbbbbbb")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled g " + "bbbbbbbbbbb00bbbbbb00bbbb000000bb000000bbbb00bbbbbb00bbbbbbbbbbb")
    #     time.sleep(0.5)

    # # # power failure
    # tello.send_expansion_command("led 255 0 0")
    # tello.send_expansion_command("mled g " + "00ppp0000rrrrr000rppbr000rrrrr000rppbr000rrrrr000rppbr000rrrrr00")
    # time.sleep(2)
    # tello.send_expansion_command("led 0 0 0")
    # # #tello.send_expansion_command("led  br 2 255 0 0")
    # # # solid green
    # # tello.send_expansion_command("led 0 255 0")
    # # tello.send_expansion_command("mled l b 2.5 Ready ")
    # # time.sleep(5)
    
    # for i in range(4):
    #     # ?
    #     tello.send_expansion_command("mled g " + "00rrrr000rr00rr000000rr00000rr00000rr00000000000000rr00000000000")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled g " + "0000000000rrrr000rr00rr000000rr00000rr00000rr00000000000000rr000")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled g " + "00rrrr000rr00rr000000rr00000rr00000rr00000000000000rr00000000000")
    #     time.sleep(0.5)
    
    # # tello.send_expansion_command("led  br 2 255 128 0")
    
    # # # hazardous materials
    # # # Attention en |X|
    # for i in range(2):
    #     tello.send_expansion_command("mled g " + "000b000000brb00000brb0000bbrbb000bbbbb00bbbrbbb0bbbbbbb000000000")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled sc")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled g " + "00000000000b000000brb00000brb0000bbrbb000bbbbb00bbbrbbb0bbbbbbb0")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled sc")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled g " + "0000b000000brb00000brb0000bbrbb000bbbbb00bbbrbbb0bbbbbbb00000000")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled sc")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled g " + "000000000000b000000brb00000brb0000bbrbb000bbbbb00bbbrbbb0bbbbbbb")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled sc")
    #     time.sleep(0.5)
        
        
    # # for i in range(2):
    # #     tello.send_expansion_command("mled g " + "00000000000r000000rbr00000rbr0000rrbrr000rrrrr00rrrbrrr0rrrrrrr0")
    # #     time.sleep(0.5)
    # #     tello.send_expansion_command("mled sc")
    # #     time.sleep(0.5)

    # # tello.send_expansion_command("mled g " + "bbbrrbbbbbrrrrbbbbrbbrbbbrrbbrrbbrrbbrrbrrrbbrrrrrrrrrrrrrrbbrrr")
    # # time.sleep(0.5)
    # # tello.send_expansion_command("mled g " + "bbbrrbbbbbrbbrbbbbrbbrbbbrrbbrrbbrrbbrrbrrrrrrrrrrrbbrrrrrrrrrrr")
    # # time.sleep(0.5)
    # # tello.send_expansion_command("mled g " + "bbbrrbbbbbrrrrbbbbrbbrbbbrrbbrrbbrrbbrrbrrrbbrrrrrrrrrrrrrrbbrrr")
    # # time.sleep(0.5)
    # # tello.send_expansion_command("mled g " + "bbbrrbbbbbrbbrbbbbrbbrbbbrrbbrrbbrrbbrrbrrrrrrrrrrrbbrrrrrrrrrrr")
    # # time.sleep(0.5)
    # # tello.send_expansion_command("mled g " + "bbbrrbbbbbrrrrbbbbrbbrbbbrrbbrrbbrrbbrrbrrrbbrrrrrrrrrrrrrrbbrrr")
    # # time.sleep(0.5)
    # # tello.send_expansion_command("mled g " + "bbbrrbbbbbrbbrbbbbrbbrbbbrrbbrrbbrrbbrrbrrrrrrrrrrrbbrrrrrrrrrrr")
    # # time.sleep(0.5)
    
    # # # water flood
    # # tello.send_expansion_command("mled g " + "00b000b00b000b00bb00bb00bbb0bbb0bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
    # # time.sleep(2)
    # # # oil
    # # tello.send_expansion_command("mled g " + "00pppp000ppbbbp0pp00bbpppb0bbbbppbbb0bbpppbbbbpp0ppbbpp000pppp00")
    # # time.sleep(2)
    # # tello.send_expansion_command("mled g " + "00pppp000pp00pp0ppbb00ppp0b0000pp000b00ppp0000pp0pp00pp000pppp00")
    # # time.sleep(2)
    
    # chemicals
    # for i in range(2):
    #     tello.send_expansion_command("mled g " + "00bbbb00000bb000000bb000000bb00000bprb000bprrrb0bprrrrrb0bbbbbb0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00bbbb00000bb000000bb000000pb00000bprb000bprrrb0bprrrrrb0bbbbbb0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00bbbb00000bb000000bb000000pp00000bprb000bprrrb0bprrrrrb0bbbbbb0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00bbbb00000bb000000bp000000pr00000bprb000bprrrb0bprrrrrb0bbbbbb0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00bbbb00000bb000000pp000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00bbbb00000pb000000rp000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00bbbb00000pp000000rr000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00bbbb00000rr000000rr000000rr00000bprb000bprrrb0bprrrrrb0bbbbbb0")
    #     time.sleep(0.2)
        
    # # # tete de mort - danger
    # # tello.send_expansion_command("mled g " + "000000000bbbbp00bbbbbbp0bbrbrbp0bbbbbbp0bbb0bbp00bbbbp000b0b0p00")
    # # time.sleep(2)
    # # # locked
    # # tello.send_expansion_command("mled g " + "00rrr0000r000r000r000r00rrrrrrr0rrr0rrr0rrr0rrr0prrrrrp00ppppp00")
    # # time.sleep(2)
    
    # # tello.send_expansion_command("led  br 2 255 0 0")
    # # # full red
    # # tello.send_expansion_command("mled g " + "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
    # # time.sleep(3)
    # # red triangle
    # for i in range(4):
    #     tello.send_expansion_command("mled g 000rr000000rr00000rrrr0000rrrr000rrrrrr00rrrrrr0rrrrrrrrrrrrrrrr")
    #     time.sleep(1)
    #     tello.send_expansion_command("mled sc")
    #     time.sleep(0.5)
        
    # # fire
    # for i in range(10):
    #     tello.send_expansion_command("mled g " + "00000000000rr000000rpr0000rrppr000rpppr00rpppprr0rpprppr00rrrrr0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "0000r000000rrr0000rrpr0000rrprr000rpprr00rpppprr0rpprprr00rrrrr0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "000rr000000rpr0000rrpr0000rppr000rppppr00rpppprr0rpprppr00rrrrr0")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "000r000000rrr00000rprr000rrpprr00rppprr0rpppppr0rrprppr00rrrrr00")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled s p 5")
    #     time.sleep(1)
    
    # # # tello.send_expansion_command("led  br 2 0 0 255")
    # # survivor
    # for i in range(5):
    #     tello.send_expansion_command("mled g " + "bbbbbbbbbbbbbbbbbbrbbrbbbbrbbrbbbbbbbbbbbbrrrrbbbbbbbbbbbbbbbbbb")
    #     time.sleep(1)
    #     tello.send_expansion_command("mled g " + "bbbbbbbbbbbbbbbbbbbbbbbbbbrbbrbbbbbbbbbbbbrrrrbbbbbbbbbbbbbbbbbb")
    #     time.sleep(0.1)
        
    # for i in range(4):
    #     tello.send_expansion_command("mled g " + "00000000000r00000000r0000bb00b00bbbb0b00bbbb0b000bb0b000bbbb0000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000000r0000000r000bb00b00bbbb0b00bbbb0b000bb0b000bbbb0000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000000000000000r00bb000r0bbbb00b0bbbb00b00bb00b00bbbbb000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000000000000000000bb0000rbbbb000rbbbb00b00bb00b00bbbbb000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000000000000000r00bb000r0bbbb00b0bbbb00b00bb00b00bbbbb000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000000r0000000r000bb00b00bbbb0b00bbbb0b000bb0b000bbbb0000")
    #     time.sleep(0.1)
    # snail  
    # for i in range(4):
    #     tello.send_expansion_command("mled g " + "00000000000000000000r000000b0bb000b0bbbb00b0bbbb000b0bb00000bbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000r0000000b0000000b00bb000b0bbbb00b0bbbb000b0bb00000bbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "00000000000000000r0000000b000bb00b00bbbb0b00bbbb00b00bb0000bbbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "00000000000000000000000000000bb0r000bbbb0b00bbbb00b00bb0000bbbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "00000000000000000r0000000b000bb00b00bbbb0b00bbbb00b00bb0000bbbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000r0000000b0000000b00bb000b0bbbb00b0bbbb000b0bb00000bbbb")
    #     time.sleep(0.1)
    
    # for i in range(4):
    #     tello.send_expansion_command("mled g " + "0000000000000bb00000bbbbr000bbbb0b000bb000bbbbbb0000bbbb0000bbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000000bb00r00bbbb0b00bbbb0b000bb000bbbbbb0000bbbb0000bbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000r00bb000b0bbbb00b0bbbb00b00bb0000bbbbb0000bbbb0000bbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "00000000000r0bb000b0bbbb00b0bbbb00b00bb0000bbbbb0000bbbb0000bbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000r00bb000b0bbbb00b0bbbb00b00bb0000bbbbb0000bbbb0000bbbb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "0000000000000bb00r00bbbb0b00bbbb0b000bb000bbbbbb0000bbbb0000bbbb")
    #     time.sleep(0.1)
        
    # for i in range(4):
    #     tello.send_expansion_command("mled g " + "000bb00r000bb0b0000b0b000bbbb000b00b000000bbb00000b0b0000bb0bb00")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "000bb000000bb000000b0r000bbbb000b00b000000bbb00000b0b0000bb0bb00")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "000bb000000bb000000b00000bbbb000b00b000000rbb00000b0b0000bb0bb00")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g " + "000bb000000bb000000b0r000bbbb000b00b000000bbb00000b0b0000bb0bb00")
    #     time.sleep(0.1)
    
    # for i in range(4):
    #     tello.send_expansion_command("mled g " + "0000000000000000000000000000000000000000pppppppppppppppp00000000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00000000000000000000000000000000000bb000pppbb000pppbpppp0000pppp")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00000000000000000000000000bbbb0000bbbb00pppbbb00pppbpppp0000pppp")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "000000000b0bb000bbbbbb000bbbbbbb00bbbbbbpppbbb00pppbpppp0000pppp")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "0bb0bbbbbbbbbbbbbbbbbbbbbbbbbbbb00bbbbbbpppbbb00pppbpppp0000pppp")
    #     time.sleep(0.2)
        
    # for i in range(4):
    #     tello.send_expansion_command("mled g " + "00000000pppppppppppppppp0000000000000000000000000000000000000000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "0000000000bb0000pppbb000pppbpppp00bbpppp00bb00000000000000000000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00bbb00000bbbb00pppbbb00pppbpppp0bbbpppp0bbbb0000bbbb00000000000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "0bbbbbb000bbbb00pppbb000pppbpppp0bbbppppbbbbb000bbbbb0000bbb0000")
    #     time.sleep(0.2)
    #     for j in range(3):
    #         tello.send_expansion_command("mled g " + "bbbbbbbb0bbbbbbbpppbbb00pppbpppp0bbbppppbbbbbb00bbbbbb00bbbbbbb0")
    #         time.sleep(0.5)
    #         tello.send_expansion_command("mled g " + "rrrrrrrr0rrrrrrrppprrr00ppprpppp00rrpppprrrrrr00rrrrrr00rrrrrrr0")
    #         time.sleep(0.5)
           
    # # ok
    # tello.send_expansion_command("mled g " + "00000000bbbb0b00b00b0b0bb00b0b0bb00b0bb0b00b0b0bbbbb0b0b00000000")
    # time.sleep(1)
    # tello.send_expansion_command("mled l b 2.5 Handover... ")
    # time.sleep(6)
    
    # # # zoom
    # # tello.send_expansion_command("led  0 0 255")
    # for i in range (4):
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbb000000bb000000bb000000bb000000bb000000bb000000bbbbbbbbb")
    #     time.sleep(0.05)
    #     tello.send_expansion_command("mled g "  + "000000000bbbbbb00b0000b00b0000b00b0000b00b0000b00bbbbbb000000000")
    #     time.sleep(0.05)
    #     tello.send_expansion_command("mled g "  + "000000000000000000bbbb0000b00b0000b00b0000bbbb000000000000000000")
    #     time.sleep(0.05)
    #     tello.send_expansion_command("mled g "  + "000000000000000000000000000bb000000bb000000000000000000000000000")
    #     time.sleep(0.05)
    #     tello.send_expansion_command("mled g "  + "000000000000000000bbbb0000b00b0000b00b0000bbbb000000000000000000")
    #     time.sleep(0.05)
    #     tello.send_expansion_command("mled g "  + "000000000bbbbbb00b0000b00b0000b00b0000b00b0000b00bbbbbb000000000")
    #     time.sleep(0.05)
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbb000000bb000000bb000000bb000000bb000000bb000000bbbbbbbbb")
    #     time.sleep(0.05)
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbbr000p0bb000000bb00000rbbp00000bb000000bb0r00p0bbbbbbbbb")
    #     time.sleep(1)
    # # time.sleep(2)
    
    # # # unfolded map
    # # tello.send_expansion_command("mled g "  + "b000b0b0bb0bb0bbbb0bb0bbbb0bb0bbbb0bb0bbbb0bb0bbbb0bb0bb0b0b000b")
    # # time.sleep(1)
    
    # # # map marker
    # # tello.send_expansion_command("mled g "  + "0000000000bbbb000bbbbbb00bb00bb00bb00bb00bbbbbb000bbbb00000bb000")
    # # time.sleep(1)
    
    # # # magnifying glass
    # # tello.send_expansion_command("mled g "  + "00rrr0000rbbbr00rbppbbr0rbpbbbr0rbbbbbr00rbbbrr000rrrrrr000000rr")
    # # time.sleep(1)
    
    # # # From point A to B
    # # tello.send_expansion_command("mled g "  + "bb000000bbpppppp0000000p0ppppppp0p0000000p000r0r0pppppr000000r0r")
    # # time.sleep(1)
    
    # # replay
    # for i in range (4):
    #     tello.send_expansion_command("mled g "  + "000rr00000000000000000000000000000000000000000000000000000000000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g "  + "rbbbbbbr00000000000000000000000000000000000000000000000000000000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbb000000bb000000br000000r00000000000000000000000000000000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbb000000bb000000bb000000bb000000bb000000br000000r00000000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbb000000bb000000bb000000bb000000bb000000bb000000bbr0000rb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbbr000p0bb000000bb00000rbbp00000bb000000bb0r00p0bbbbbbbbb")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbb000000bb000000bb000000bb000000bb000000bb000000bbr0000rb")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbb000000bb000000bb000000bb000000bb000000br000000r00000000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g "  + "bbbbbbbbb000000bb000000br000000r00000000000000000000000000000000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g "  + "rbbbbbbr00000000000000000000000000000000000000000000000000000000")
    #     time.sleep(0.1)
    #     tello.send_expansion_command("mled g "  + "000rr00000000000000000000000000000000000000000000000000000000000")
    #     time.sleep(0.1)
        
    # tello.send_expansion_command("mled l b 2.5 RAS. ")
    # time.sleep(3)
    
    
    # # thumb-up pink
    # for i in range(4):
    #     tello.send_expansion_command("mled g "  + "000000000000000000pppp00bbppppp0bbppppp0bbppppp0bbppppp000000000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g "  + "000000000000pp0000ppp000bbppppp0bbppppp0bbppppp0bbppppp000000000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g "  + "0000p000000pp00000pp0000bbppppp0bbppppp0bbppppp0bbppppp000000000")
    #     time.sleep(1)
    
    # for i in range(4):
    #     tello.send_expansion_command("mled g "  + "0000000000pp00000pppp00r0pppp00b00pp00b00bppbb00bpppp000bpppp000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g "  + "0000000000pp00000pppp0r00pppp0b000pp00b00bppbb00bpppp000bpppp000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g "  + "0000000000pp00000ppppr000ppppb0000pp0b000bppbb00bpppp000bpppp000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g "  + "0000000000pp00000pprp0000pppb00000pp0b000bppbb00bpppp000bpppp000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g "  + "0000000000pp00000ppppr000ppppb0000pp0b000bppbb00bpppp000bpppp000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g "  + "0000000000pp00000pppp0r00pppp0b000pp00b00bppbb00bpppp000bpppp000")
    #     time.sleep(0.2)
    
    # # Spirale
    # tello.send_expansion_command("mled g "  + "r000000000000000000000000000000000000000000000000000000000000000")
    # time.sleep(0.2)
    # tello.send_expansion_command("mled g "  + "rbbbbbbb00000000000000000000000000000000000000000000000000000000")
    # time.sleep(0.2)
    # tello.send_expansion_command("mled g "  + "rbbbbbbb0000000b0000000b0000000b0000000b0000000b0000000b0000000b")
    # time.sleep(0.2)
    # tello.send_expansion_command("mled g "  + "rbbbbbbb0000000b0000000b0000000b0000000b0000000b0000000bbbbbbbbb")
    # time.sleep(0.2)
    # tello.send_expansion_command("mled g "  + "rbbbbbbb0000000bb000000bb000000bb000000bb000000bb000000bbbbbbbbb")
    # time.sleep(0.2)
    # tello.send_expansion_command("mled g "  + "rbbbbbbb0000000bbbbbbb0bb000000bb000000bb000000bb000000bbbbbbbbb:")
    # time.sleep(0.2)
    # tello.send_expansion_command("mled g "  + "rbbbbbbb0000000bbbbbbb0bb0000b0bb0000b0bb0000b0bb000000bbbbbbbbb:")
    # time.sleep(0.2)
    # tello.send_expansion_command("mled g "  + "rbbbbbbb0000000bbbbbbb0bb0000b0bb0000b0bb0bbbb0bb000000bbbbbbbbb:")
    # time.sleep(0.2)
    # tello.send_expansion_command("mled g "  + "rbbbbbbb0000000bbbbbbb0bb00rrb0bb0brrb0bb0bbbb0bb000000bbbbbbbbb:")
    # time.sleep(0.2)
        
   
    # for i in range(4):
    #     tello.send_expansion_command("mled g "  + "0000p000000pp00000pp0000bbppppp0bbppppp0bbppppp0bbppppp000000000")
    #     time.sleep(1)
    #     tello.send_expansion_command("mled sc")
    #     time.sleep(0.5)
    
    # # open hand pink 
    # for i in range(4):
    #     tello.send_expansion_command("mled g " + "00000000000000000000000000pppp0000ppppp00pppppp00pppppp000pppp00:")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "00000000000p00000p0p0p000p0p0p0000pppp0p00ppppp00pppppp000pppp00:")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "000p00000p0p0p000p0p0p000p0p0p0p00pppp0pp0ppppp00pppppp000pppp00:")
    #     time.sleep(0.5)
    
    # for i in range(4):
    #     tello.send_expansion_command("mled g "  + "000p00000p0p0p000p0p0p000p0p0p0p00pppp0pp0ppppp00pppppp000pppp00")
    #     time.sleep(1)
    #     tello.send_expansion_command("mled sc")
    #     time.sleep(0.5)
    
    # tello.send_expansion_command("mled g "  + "000000000000p000000pp00000pp0000bbppppp0bbp000p0bbp0ppp0bbp00pp0")
    # time.sleep(2)
    # tello.send_expansion_command("mled g "  + "000000000000p000000pp00000pp0000bbppppp0bbppppp0bbppppp0bbppppp0")
    # time.sleep(2)
    # tello.send_expansion_command("mled g "  + "000000000000p000000pp00000pp0000bbppppp0bb0000p0bb0000p0bb0pppp0")
    # time.sleep(2)
    # tello.send_expansion_command("mled g "  + "0000p000000pp00000pp0000bbpppp00bbppppp0bbppppp0bbpppp0000000000")
    # time.sleep(2)
    # tello.send_expansion_command("mled g "  + "0000p000000pp00000pp0000bbppppp0bb0000p0bb0pppp0bb00ppp000000pp0")
    # time.sleep(2)
    # tello.send_expansion_command("mled g "  + "0000p000000pp00000pp0000bbppppp0bb0000p0bb00ppp0bb000p0000000000")
    # time.sleep(2)
    # tello.send_expansion_command("mled g "  + "0000p000000pp00000pp0000bbppppp0bb0pppp0bb00ppp0bb000pp000pppp00")
    #time.sleep(2)
    #     ##################
        
    
    # for i in range(5):
    #     # ?
    #     tello.send_expansion_command("mled g " + "00rrrr000rr00rr000000rr00000rr00000rr00000000000000rr00000000000")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled g " + "0000000000rrrr000rr00rr000000rr00000rr00000rr00000000000000rr000")
    #     time.sleep(0.5)
    #     tello.send_expansion_command("mled g " + "00rrrr000rr00rr000000rr00000rr00000rr00000000000000rr00000000000")
    #     time.sleep(0.5)
    # # thumb up
    # tello.send_expansion_command("mled g " + "000rr000000rr0000000rr000rrrrr00rrrrrrbbrrrrrrbbrrrrrrbb0rrrrrbb")
    # time.sleep(1)
    # # ok
    # tello.send_expansion_command("mled g " + "00000000rrrr0r00r00r0r0rr00r0r0rr00r0rr0r00r0r0rrrrr0r0r00000000")
    # time.sleep(1)
    # tello.send_expansion_command("mled l b 2.5 BYE... ")
    # time.sleep(3)
    # tello.send_expansion_command("led 0 0 255")
    # time.sleep(2)
    # open hand
    # tello.send_expansion_command("mled g " + "000r00000r0r0r000r0r0r000r0r0r0r00rrrr0rr0rrrrr00rrrrrr000rrrr00")
    # time.sleep(2)
    # tello.send_expansion_command("mled g " + "000p00000p0p0p000p0p0p000p0p0p0p00pppp0pp0ppppp00pppppp000pppp00")
    # time.sleep(2)
    # tello.send_expansion_command("mled g " + "000b00000b0b0b000b0b0b000b0b0b0b00bbbb0bb0bbbbb00bbbbbb000bbbb00")
    # time.sleep(2)
    # tello.send_expansion_command("mled g " + "000r00000r0r0r000r0r0r000r0r0r0r00rrrr0rr0rrrrr00rrrrr0000bbbb00:")
    # time.sleep(1)
    # tello.send_expansion_command("mled g " + "000p00000p0p0p000p0p0p000p0p0p0p00pppp0pp0ppppp00ppppp0000bbbb00:")
    # time.sleep(1)
   
    # # heart
    # for i in range(5):
    #     tello.send_expansion_command("mled g " + "000000000rr0rr00rrrrrrr0rrrrrrp00rrrrp0000rrp000000p000000000000")
    #     time.sleep(0.75)
    #     tello.send_expansion_command("mled g " + "0000000000rr0rr00rrrrrrr0rrrrrrp0rrrrrrp00rrrrp0000rrp000000p000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "000000000rr0rr00rrrrrrr0rrrrrrp00rrrrp0000rrp000000p000000000000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "0000000000rr0rr00rrrrrrr0rrrrrrp0rrrrrrp00rrrrp0000rrp000000p000")
    #     time.sleep(0.2)
    #     tello.send_expansion_command("mled g " + "000000000rr0rr00rrrrrrr0rrrrrrp00rrrrp0000rrp000000p000000000000")
    #     time.sleep(0.75)
    #     tello.send_expansion_command("mled s p 5")
    #     time.sleep(1)
    
    #tello.send_expansion_command("mled sc")
    #tello.send_expansion_command("led 255 0 0")
    
    pygame.init()
    # Initializing surface
    surface = pygame.display.set_mode((780,780))
     
    # background = pygame.image.load('thumb_up.jpg')
    # background = pygame.transform.scale(background, (780, 780))
    
    # Initializing Color
    default_color = (128,128,128)
    r = (255, 0, 0)
    b = (0, 0, 255)
    p = (255, 0, 255)
    display = ['0']*64
    # Creating a dictionary to track the color of each rectangle
    rect_colors = {(i, j): default_color for i in range(8) for j in range(8)}
    
    pygame.display.flip()
    running = True
    while running:
        surface.fill((255, 255, 255))
        # surface.blit(background, (0,0))
        for i in range(8):
            for j in range(8):
                x, y = pygame.mouse.get_pos()
                left = i*100
                right = left +80
                top = j*100
                bottom = top +80
                width = 80
                height = 80
                color = rect_colors[(i, j)]
                pygame.draw.rect(surface, color, pygame.Rect(top, left, width, height))

                
        pygame.display.flip()
                
        for event in pygame.event.get():
            # check if quit
            if event.type == pygame.QUIT:
                running = False
            # checks if a mouse is clicked 
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                counter = 0
                for i in range(8):
                    for j in range(8):
                        left = j * 100
                        top = i * 100
                        right = left + 80
                        bottom = top + 80
                        
                        if (left <= x <= right) and (top <= y <= bottom):
                            if(rect_colors[(i, j)] == default_color):
                                rect_colors[(i, j)] = r 
                                display[counter] = 'r'
                            elif(rect_colors[(i, j)] == r):
                                rect_colors[(i, j)] = b
                                display[counter] = 'b'  
                            elif(rect_colors[(i, j)] == b):
                                rect_colors[(i, j)] = p 
                                display[counter] = 'p'
                            elif(rect_colors[(i, j)] == p):
                                rect_colors[(i, j)] = default_color  
                                display[counter] = '0'
                        counter += 1                               
    pygame.quit()
    print("".join(display))
    tello.send_expansion_command("mled g " + "".join(display))
    # time.sleep(2)
    
if __name__=="__main__":
    main()
    
