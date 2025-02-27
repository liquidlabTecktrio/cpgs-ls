
# SCAN EACH SPACE/SLOT FOR VEHICLE DECTECTION
import json
from multiprocessing import Pool
import cv2
import django
import numpy as np
from cpgsapp.controllers.CameraViewController import dectect_license_plate


def scan_spaces():
    '''
    SCAN the parking slot FOR VEHICLE
    '''             
    poslist =[]
    with open('coordinates.txt','r')as data:
        poslist = json.load(data)
    
    global TOTALSPACES, SPACES
    SPACES = []
    TOTALSPACES = len(poslist)
    print('Found ',TOTALSPACES , "space")
    for spaceID in range(TOTALSPACES):
        obj = {
            'spaceID':spaceID,
            'spaceStatus':'vaccant',
            'licenseNumber':''
        }
        SPACES.append(obj)
    
    
    with open('spaceDataForServer.txt', 'w') as spaces_file:
        json.dump(SPACES, spaces_file,indent=4)

    space_coordinate_list = []

    for spaceID, pos in enumerate(poslist):
        SpaceCoordinates = np.array([[pos[0][0], pos[0][1]], [pos[1][0], pos[1][1]], [pos[2][0], pos[2][1]], [pos[3][0], pos[3][1]]])
        pts = np.array(SpaceCoordinates, np.int32)
        x, y, w, h = cv2.boundingRect(pts)
        space_coordinate_list.append((spaceID,x,y,w,h))

    if len(space_coordinate_list) > 0:
        with Pool(initializer=django.setup) as pool: 
            pool.map(dectect_license_plate, space_coordinate_list)

      

def getLicensePlate(spaceDetails):
        spaceID, x, y, w, h = spaceDetails
        print(f'Scanning spaceID {spaceID}')
        camera_view = cv2.imread("camera_view.jpg")  
        space_view = camera_view[y:y+h, x:x+w]
        print('dectecting')
        licensePlate=DectectLicensePlate(space_view)

        SPACES = SpaceInfo()
        if licensePlate is not None:
            print('recognising')
            licenseNumber = RecognizeLicensePlate(licensePlate)
            for space in SPACES:
                if space['spaceID'] == spaceID:
                    space['licenseNumber'] = licenseNumber
                    space['spaceStatus'] = 'occupied'
            
            
            with open('spaceDataForServer.txt', 'w') as spaces_file:
                json.dump(SPACES, spaces_file, indent=4)

            saveFile(spaceID, licensePlate)


def getSpaceMonitors(spaceID, x, y, w, h ):

        # spaceID, x, y, w, h = spaceDetails
        print(f'Scanning spaceID {spaceID}')
        camera_view = cv2.imread("camera_view.jpg")  
        space_view = camera_view[y:y+h, x:x+w]
        print('dectecting')

        licensePlateinSpace, licensePlate = DectectLicensePlateWithSpaceView(space_view)
        print('recognize')
        licenseNumber = RecognizeLicensePlate(licensePlate)
        # licenseNumber = "test"
        print("license Number is ",licenseNumber)

        saveFile(f'spaceViewOfSpaceID{spaceID}',licensePlateinSpace)
        licensePlateinSpaceInBase64 = image_to_base64(licensePlateinSpace)
        SPACES = SpaceMonitoringInfo()

        for space in SPACES:
            if space['spaceID'] == spaceID:
                space['spaceFrame'] = licensePlateinSpaceInBase64
                space['licenseNumber'] = licenseNumber
        
            
        with open('spaceDataForClient.txt', 'w') as space_views:
            json.dump(SPACES, space_views, indent=4)
        return



async def monitor_spaces():
    '''
    SCAN the parking slot FOR VEHICLE
    '''             
    poslist =[]
    await asyncio.sleep(.1)

    with open('coordinates.txt','r')as data:
        poslist = json.load(data)
    
    global TOTALSPACES, SPACES
    SPACES = []
    TOTALSPACES = len(poslist)
    print('Found ',TOTALSPACES , "space")
    for spaceID in range(TOTALSPACES):
        obj = {
            'spaceID':spaceID,
            'spaceStatus':'vaccant',
            'spaceFrame':'',
            'licenseNumber':""
        }
        SPACES.append(obj)
    
    
    with open('spaceDataForClient.txt', 'w') as spaces:
        json.dump(SPACES, spaces,indent=4)

    # camera_view = await capture('run')
    # camera_view = cv2.imread("camera_view.jpg")
    # saveFile('camera_view',camera_view)
    # await capture('stop')

    space_coordinate_list = []

    for spaceID, pos in enumerate(poslist):
        SpaceCoordinates = np.array([[pos[0][0], pos[0][1]], [pos[1][0], pos[1][1]], [pos[2][0], pos[2][1]], [pos[3][0], pos[3][1]]])
        pts = np.array(SpaceCoordinates, np.int32)
        x, y, w, h = cv2.boundingRect(pts)
        space_coordinate_list.append((spaceID,x,y,w,h))

        getSpaceMonitors(spaceID, x, y, w, h)