from djitellopy import Tello
import time
import os


tello = Tello()
tello.connect()


neutralbin = "{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102)+"{0:08b}".format(0)+"{0:08b}".format(60)
happy = "{0:08b}".format(0)+"{0:08b}".format(66)+"{0:08b}".format(165)+"{0:08b}".format(165)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(60)+"{0:08b}".format(24)
emotion = happy.replace('1', 'b')
leftArrow = "{0:08b}".format(8)+"{0:08b}".format(12)+"{0:08b}".format(254)+"{0:08b}".format(255)+"{0:08b}".format(255)+"{0:08b}".format(254)+"{0:08b}".format(12)+"{0:08b}".format(8)
rightArrow = "{0:08b}".format(16)+"{0:08b}".format(48)+"{0:08b}".format(127)+"{0:08b}".format(255)+"{0:08b}".format(255)+"{0:08b}".format(127)+"{0:08b}".format(48)+"{0:08b}".format(16)
frontArrow = "{0:08b}".format(24)+"{0:08b}".format(60)+"{0:08b}".format(126)+"{0:08b}".format(255)+"{0:08b}".format(60)+"{0:08b}".format(60)+"{0:08b}".format(60)+"{0:08b}".format(60)
cross = "{0:08b}".format(129)+"{0:08b}".format(66)+"{0:08b}".format(36)+"{0:08b}".format(24)+"{0:08b}".format(24)+"{0:08b}".format(36)+"{0:08b}".format(66)+"{0:08b}".format(129)

tello.send_expansion_command("mled sc")


# start_time_tof = time.time()
# while(start_time_tof + 10 > time.time()):
#tello.send_expansion_command("tof?")


# tof test
# tello.takeoff()



# display arrows
for i in range(4):
    tello.send_expansion_command("mled g " + leftArrow.replace('1', 'b'))
    tello.send_expansion_command("led 0 0 255")
    time.sleep(1)
    tello.send_expansion_command("mled sc")
    tello.send_expansion_command("led 0 0 0")
    time.sleep(1)

for i in range(4):
    tello.send_expansion_command("mled g " + rightArrow.replace('1', 'b'))
    tello.send_expansion_command("led 0 0 255")
    time.sleep(1)
    tello.send_expansion_command("mled sc")
    tello.send_expansion_command("led 0 0 0")
    time.sleep(1)

for i in range(4):
    tello.send_expansion_command("mled g " + frontArrow.replace('1', 'b'))
    tello.send_expansion_command("led 0 0 255")
    time.sleep(1)
    tello.send_expansion_command("mled sc")
    tello.send_expansion_command("led 0 0 0")
    time.sleep(1)

# red cross
for i in range(4):
    tello.send_expansion_command("mled g " + cross.replace('1', 'r'))
    tello.send_expansion_command("led 255 0 0")
    time.sleep(1)
    tello.send_expansion_command("mled sc")
    tello.send_expansion_command("led 0 0 0")
    time.sleep(1)


# chase for searching
chase = ["{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(66)+"{0:08b}".format(132),
"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(34)+"{0:08b}".format(17),
"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(17)+"{0:08b}".format(34),
"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(132)+"{0:08b}".format(66)]

# blink upper lED blue
tello.send_expansion_command("led 75 75 255")
for i in range(5):
    for j in range(4):
        tello.send_expansion_command("led 75 75 255")
        time.sleep(0.075)
        tello.send_expansion_command("mled g " + chase[j].replace('1', 'b'))
        tello.send_expansion_command("led 0 0 0")
        time.sleep(0.075)

# morse for spotting
morse = "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102)
for i in range(5):
    for j in range(4):
        tello.send_expansion_command("led 255 0 0")
        tello.send_expansion_command("mled g " + morse.replace('1', 'r'))
        time.sleep(0.1)
        tello.send_expansion_command("led 0 0 0")
        tello.send_expansion_command("mled sc")
        time.sleep(0.1)
    time.sleep(0.5)

# onedecent for approaching
onedecent = ["{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153)+"{0:08b}".format(102), "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153)+"{0:08b}".format(153), "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)+"{0:08b}".format(153), "{0:08b}".format(0)+"{0:08b}".format(0)+"{0:08b}".format(102)]
tello.send_expansion_command("led br 0.15 255 100 0")
for i in range(5):
    for j in range(4):
        tello.send_expansion_command("mled g " + onedecent[j].replace('1', 'p'))
        time.sleep(0.15)
    
# solid for ready to interact
solid = morse
tello.send_expansion_command("led 0 255 0")
tello.send_expansion_command("mled g " + solid.replace('1', 'b'))
time.sleep(5)


tello.send_expansion_command("mled sc")

tello.send_expansion_command("mled g " + emotion)
time.sleep(3)
tello.land()

