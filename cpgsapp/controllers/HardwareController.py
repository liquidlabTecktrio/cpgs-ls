
# HardwareConfiguration controller

import json
from cpgsapp.controllers import FileSystemContoller
from cpgsserver.settings import IS_PI_CAMERA_SOURCE
from gpiozero import LED
from storage import Variables

if IS_PI_CAMERA_SOURCE:
    GREENLIGHT = LED(2) 
    REDLIGHT = LED(3) 
    MODEBUTTON = LED(4) 

def get_threshold(data):
    print('new thresh',data.threshold)
    with open('config.json','rb') as file:
        data = json.load(file)
    return True, data

def set_pilot_to_green():
    GREENLIGHT.off()
    REDLIGHT.on()

def set_pilot_to_red():
    GREENLIGHT.on()
    REDLIGHT.off()

def update_pilot():
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
