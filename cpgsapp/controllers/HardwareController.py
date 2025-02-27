
# HardwareConfiguration controller

import json
from cpgsserver.settings import IS_PI_CAMERA_SOURCE
from gpiozero import LED
import FileSystemContoller
from storage import Variables

if IS_PI_CAMERA_SOURCE:
    GREENLIGHT = LED(2) 
    REDLIGHT = LED(3) 
    MODEBUTTON = LED(4) 

def get_threshold(self, data):
    print('new thresh',data.threshold)
    with open('config.json','rb') as file:
        data = json.load(file)
    return True, data

def set_pilot_to_green(self):
    GREENLIGHT.off()
    REDLIGHT.on()

def set_pilot_to_red(self):
    GREENLIGHT.on()
    REDLIGHT.off()

def update_pilot(self):
    occupiedSpaceList = []
    for space in FileSystemContoller.get_space_info():
        if space['spaceStatus']=='occupied':
            occupiedSpaceList.append(space)
            NoOfOccupiedSpaces = len(occupiedSpaceList)
            AvailableVaccantSpaces = Variables.TOTALSPACES - NoOfOccupiedSpaces
            if AvailableVaccantSpaces == 0:
                print('Setting Pilot to Red')
                set_pilot_to_red()
            else:
                print('Setting pilot to Green')
                set_pilot_to_green()
