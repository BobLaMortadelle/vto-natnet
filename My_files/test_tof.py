from djitellopy import Tello


tello = Tello()
tello.connect()
while True:
    tello.send_expansion_command("tof?")