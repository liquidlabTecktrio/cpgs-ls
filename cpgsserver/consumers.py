
import asyncio
import base64
import json
import math
import pickle
import threading
import time
import django
import base64
import numpy as np
from  multiprocessing import Pool
from channels.generic.websocket import AsyncWebsocketConsumer
import cv2
import easyocr
import imutils
import subprocess
from cpgsapp.models import NetworkSettings
from cpgsapp.serializers import NetworkSettingsSerializer
from ultralytics import YOLO
from cpgsserver.settings import  IS_PI_CAMERA_SOURCE, MAIN_SERVER_IP
from asgiref.sync import sync_to_async
from gpiozero import LED

# Load YOLO model once
model = YOLO("license_plate_detector.pt")
print('Initiating easyocr model')
# reader = easyocr.Reader(model_storage_directory = 'LanguageModels', lang_list = ['en'])
reader = easyocr.Reader(['en'], gpu=False, detector=True, recognizer=True, model_storage_directory='LanguageModels', download_enabled=False)

DEBUG = True
VACCENTSPACES = 0
TOTALSPACES = 0


# Global camera setup

if IS_PI_CAMERA_SOURCE:
    GREENLIGHT = LED(2) 
    REDLIGHT = LED(3) 
    MODEBUTTON = LED(4) 
    from picamera2 import Picamera2
    cap = Picamera2()
    cap.start()
    
else: cap = cv2.VideoCapture(0)

def saveFile(filename, image):
    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = buffer.tobytes() 
    with open(f'{filename}.jpg','wb') as file:
        file.write(image_bytes)

# GET ONE FRAME
def capture():
    """Synchronous capture function for threading or multiprocessing."""
    global cap
    print('camera started')
    while True:
        if IS_PI_CAMERA_SOURCE:
            frame = cap.capture_array()
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                print("Failed to capture frame from PiCamera")
                time.sleep(1)
                continue
        else:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame from VideoCapture")
                time.sleep(1)
                continue

        if frame is not None and frame.size > 0:  # Ensure frame is valid
            frame = cv2.resize(frame, (720, 480), interpolation=cv2.INTER_AREA)
            saveFile('camera_view', frame)
            # print("Frame captured and saved")
        else:
            print("Invalid frame received")

        time.sleep(1)  # Control frame rate
        
    


ShootCameraThread = threading.Thread(target=capture)
ShootCameraThread.start()

def network_handler():
    spaceInfo = SpaceInfo()
    timestamp = ""
    device_id = 20001
    mac_addr = "SDF34:34DFS:L#43:DF"
    ip_address = "192.168.1.25"
    ssid = "CPGSWIFI"
    device_mode = "LIVE"
    licenseNumber = "kl23f345"
    space_id = 1003
    '''
    Sends the slotData to the server in UDP protocol
    '''
    # slotData = f'{timestamp}:{device_id}:{mac_addr}:{space_id}:{ip_address}:{ssid}:{licenseNumber}:{device_mode}'
    slotData = {
    "data":f'{timestamp}-{device_id}-{mac_addr}-{space_id}-{ip_address}:{ssid}:{licenseNumber}:{device_mode}'
    }
        
    # try:
    #     url = MAIN_SERVER_IP
    #     requests.post(url, json=slotData)
    #     # UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    #     # UDPClientSocket.sendto(bytesToSend, serverSocketAddress)
    print('Updated to MS')
    # except Exception as e:
    #     print(e)

# VIDEO STREMER
async def video_stream():
  
    while True:
        frame  = capture('run')
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = cv2.flip(frame, 1)
        frame_bytes = buffer.tobytes()
        encoded_frame = base64.b64encode(frame_bytes).decode('utf-8')
        yield f"data:image/jpeg;base64,{encoded_frame}"

# VIDEO STREAMER FOR CALIBRATION
async def video_stream_for_calibrate():
    while True:
        frame  = await capture('run')
        with open('coordinates.txt','r')as data:
            for space_coordinates in json.load(data):
                    print("space - ",space_coordinates)
                    for index in range (0,len(space_coordinates)-1):
                        # print(int(space_coordinates[index][0]), "----------")
                        x1 = int(space_coordinates[index][0])
                        y1 = int(space_coordinates[index][1])
                        x2 = int(space_coordinates[index+1][0])
                        y2 = int(space_coordinates[index+1][1])    
                        cv2.line(frame,(x1,y1),(x2,y2), (0, 255, 0), 2)  # Draw line
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        encoded_frame = base64.b64encode(frame_bytes).decode('utf-8')
        readyToSendFrame = f"data:image/jpeg;base64,{encoded_frame}"
        yield readyToSendFrame


    # elif (task == 'stop'):
    #     if IS_PI_CAMERA_SOURCE:
    #       cap.close()
    #     else:
    #       cap.release()
          

@sync_to_async
def get_network_settings():
    currentNetworkSettings = NetworkSettings.objects.first()
    print(currentNetworkSettings)
    serialized_settings = NetworkSettingsSerializer(currentNetworkSettings)
    return serialized_settings.data




def SpaceInfo():
    with open('spaceDataForServer.txt','r') as spaces:
        SPACES = json.load(spaces)
    return SPACES

def SpaceMonitoringInfo():
    with open('spaceDataForClient.txt','r') as space_views:
        SPACES = json.load(space_views)
    return SPACES

def PilotToGreen():
    GREENLIGHT.off()
    REDLIGHT.on()

def PilotToRed():
    GREENLIGHT.on()
    REDLIGHT.off()

def image_to_base64(frame):
    try:
        # Ensure frame is C-contiguous
        frame_contiguous = np.ascontiguousarray(frame)
        success, encoded_img = cv2.imencode('.jpg', frame_contiguous)
        if not success:
            print("Failed to encode frame to JPEG")
            return None
        
        # Convert NumPy array to bytes
        image_bytes = encoded_img.tobytes()
        
        # Convert bytes to base64 string
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{base64_string}"
        
        return data_url
    except Exception as e:
        print(f"Error converting frame to base64: {str(e)}")
        return None

def pilot_handler():
    occupiedSpaceList = []
    for space in SpaceInfo():
        if space['spaceStatus']=='occupied':
            occupiedSpaceList.append(space)
    NoOfOccupiedSpaces = len(occupiedSpaceList)
    AvailableVaccantSpaces = TOTALSPACES - NoOfOccupiedSpaces
    if AvailableVaccantSpaces == 0:
        print('Setting Pilot to Red')
        PilotToRed()
    else:
        print('Setting pilot to Green')
        PilotToGreen()
    return 


def DectectLicensePlate(frame):
    """Detects license plates in a frame and returns the cropped license plate image."""
    results = model.predict(frame, conf=0.5)
    license_plate = None 

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            
            if cls == 0: 
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(frame, "License Plate", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                license_plate = frame[y1:y2, x1:x2]
    return license_plate

def DectectLicensePlateWithSpaceView(space_view):
    """Detects license plates in a frame and returns the cropped license plate image."""
    results = model.predict(space_view, conf=0.5)
    license_plate = None 

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            
            if cls == 0: 
                cv2.rectangle(space_view, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(space_view, "License Plate", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                license_plate = space_view[y1:y2, x1:x2]

    return space_view, license_plate


def RecognizeLicensePlate(licensePlate):
        
        scanRound = 0
        maxConfidence = 0
        licenseNumberWithMoreConfidence = ""

        if licensePlate is not None:
            while scanRound < 5: 
                scanRound  = scanRound + 1
                gray = cv2.cvtColor(licensePlate, cv2.COLOR_BAYER_BG2GRAY)
                bfilter = cv2.bilateralFilter(gray, 11, 11, 17)
                edged = cv2.Canny(bfilter, 30,200)
                keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                contours = imutils.grab_contours(keypoints)
                contours = sorted(contours, key = cv2.contourArea, reverse=True)[:10]
                
                result = reader.readtext(licensePlate)
                result = [(entry[1],entry[2]) for entry in result][0]
                licenseNumber, confidence = result
                if confidence > maxConfidence:
                    maxConfidence = confidence
                    licenseNumberWithMoreConfidence = licenseNumber
            print('Captured', licenseNumberWithMoreConfidence,"with confidence", confidence)
            return licenseNumberWithMoreConfidence
        
        return licenseNumberWithMoreConfidence
        

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

    # if len(space_coordinate_list) > 0:
    #     with Pool(initializer=django.setup) as pool: 
    #         pool.map(getSpaceMonitors, space_coordinate_list)


# SCAN EACH SPACE/SLOT FOR VEHICLE DECTECTION
async def scan_spaces():
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
                'licenseNumber':''
            }
            SPACES.append(obj)
        
        
        with open('spaceDataForServer.txt', 'w') as spaces_file:
            json.dump(SPACES, spaces_file,indent=4)

        camera_view = await capture('run')
        saveFile('camera_view',camera_view)
        await capture('stop')

        space_coordinate_list = []

        for spaceID, pos in enumerate(poslist):
            SpaceCoordinates = np.array([[pos[0][0], pos[0][1]], [pos[1][0], pos[1][1]], [pos[2][0], pos[2][1]], [pos[3][0], pos[3][1]]])
            pts = np.array(SpaceCoordinates, np.int32)
            x, y, w, h = cv2.boundingRect(pts)
            space_coordinate_list.append((spaceID,x,y,w,h))

        if len(space_coordinate_list) > 0:
            with Pool(initializer=django.setup) as pool: 
                pool.map(getLicensePlate, space_coordinate_list)

        pilot_handler()
        network_handler()

    
# CONSUMER FOR HANDLING ALL REQUESTS FROM CLIENT
class ServerConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.streaming = False
        self.stream_task = None 
        self.coordinates = []
        self.points = [] 

    async def connect(self):
        await self.accept()
        if DEBUG:print('client connected :)')

    async def disconnect(self, close_code):
        if self.streaming:
            if self.stream_task:
                self.stream_task.cancel()
        await super().disconnect(close_code)
        if DEBUG:print('client disconnected :(')

    async def receive(self, text_data=None, bytes_data=None):
        if DEBUG:print('Received Message: ', text_data)
        req = json.loads(text_data)

        # HANDLE LIVESTREAM START REQUESTS
        if req.get("task") == 'start' and not self.streaming:
            self.streaming = True
            self.stream_task = asyncio.create_task(self._stream_frames())
            await asyncio.sleep(.1)

        # HANDLE LIVESTREAM STOP REQUESTS
        elif req.get("task") == 'stopstream':
            pass
            # if self.streaming:
            #     self.streaming = False
            #     if self.stream_task:
            #         self.stream_task.cancel()
            #         try:
            #             await self.stream_task
            #         except asyncio.CancelledError:
            #             print("Stream canceled")
            # await capture('stop')

        # HANDLE REQUEST FOR THE MANUAL CALIBRATION FRAMES
        elif req.get("task") == 'get_calibrating_frame':
            # frame  = await capture('run')

            frame = cv2.imread("camera_view.jpg")
            with open('coordinates.txt','r')as data:
                for space_coordinates in json.load(data):
                        print("space - ",space_coordinates)
                        for index in range (0,len(space_coordinates)-1):
                            # print(int(space_coordinates[index][0]), "----------")
                            x1 = int(space_coordinates[index][0])
                            y1 = int(space_coordinates[index][1])
                            x2 = int(space_coordinates[index+1][0])
                            y2 = int(space_coordinates[index+1][1])    
                            cv2.line(frame,(x1,y1),(x2,y2), (0, 255, 0), 2)  # Draw line
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            encoded_frame = base64.b64encode(frame_bytes).decode('utf-8')
            readyToSendFrame = f"data:image/jpeg;base64,{encoded_frame}"

            data = {'frame':readyToSendFrame,'task':'calibrate_stream'}
            await self.send(json.dumps(data))

        # HANDLE REQUEST TO UPDATE THE SPACE COORDINATES IN MANUAL CALIBRATION FRAMES
        elif req.get("task") == 'update_calibrating_frame':

                x = req.get('x')
                y = req.get('y')
                self.points.append((x, y))
                
                if len(self.points)%5 == 0:
                    self.coordinates.append(self.points)
                    with open('coordinates.txt','w') as coordinate:
                        json.dump(self.coordinates, coordinate, indent=4)
                    self.points = []

        # HANDLE REQUEST TO RESET THE SPACE COORDINATES IN CPGS DB
        elif req.get("task") == 'reset_calibrating_frame':
            self.coordinates = []
            with open('coordinates.txt','w') as coordinate:
                json.dump(self.coordinates, coordinate, indent=4)

            frame = await capture('run')
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = await capture('stop')
            frame_bytes = buffer.tobytes()
            encoded_frame = base64.b64encode(frame_bytes).decode('utf-8')
            readyToSendFrame = f"data:image/jpeg;base64,{encoded_frame}"

            data = {'frame':readyToSendFrame,'task':'calibrate_stream'}
            await self.send(json.dumps(data))

        # HANDLE REQUEST FOR AUTOCALIBRATION 
        elif req.get('task') == 'auto_calibrate':
            frameInGray = cv2.cvtColor(await capture(), cv2.COLOR_BGR2GRAY)
            frameInGrayAndBlur = cv2.GaussianBlur(frameInGray, (3, 3), 2)
            with open("config.json","rb") as configurations:
                config = json.load(configurations)
                configuration_data = {
                    "CameraFilterThresh" : config["threshold"],
                    "serverIP" :config["server_ip"],
                    "serverPort" : config["server_port"],
                    "DEBUG" : config["DEBUG"],
                    "CameraFilterMaximumThresh" : 255,
                    "CameraFilterThreshOnCalibrate" : config["threshold"],
                    "CameraFilterMaximumThreshOnCalibrate" : 255,
                    "BoostThreshAT":2,
                }
            _,ThreshHoldedFrame  = cv2.threshold(frameInGrayAndBlur,
                                                  configuration_data["CameraFilterThreshOnCalibrate"], 
                                                  configuration_data["CameraFilterMaximumThreshOnCalibrate"], 
                                                  cv2.THRESH_BINARY_INV)
            imgmedian = cv2.medianBlur(ThreshHoldedFrame, 3 )
            kernal = np.ones((3, 3), np.uint8)
            imgdilate = cv2.dilate(imgmedian, kernel=kernal, iterations=configuration_data["BoostThreshAT"])
            contours, _ = cv2.findContours(imgdilate, cv2.INTER_AREA, cv2.CHAIN_APPROX_SIMPLE)
            self.coordinate_data = []
            for slotIndex, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                area_threshold = 500
                perimeter_threshold = 200
                if area > area_threshold and perimeter > perimeter_threshold:
                    epsilon = 0.02 * perimeter 
                    approx_polygon = cv2.approxPolyDP(contour, epsilon, True)
                    x, y, w, h = cv2.boundingRect(approx_polygon)
                    if len(approx_polygon) == 4 and h > w :
                        corners = [tuple(coord[0]) for coord in approx_polygon]
                        vector1 = (corners[1][0] - corners[0][0], corners[1][1] - corners[0][1])
                        vector2 = (corners[2][0] - corners[1][0], corners[2][1] - corners[1][1])
                        dot_product = sum(a * b for a, b in zip(vector1, vector2))
                        magnitude1 = math.sqrt(sum(a * a for a in vector1))
                        magnitude2 = math.sqrt(sum(b * b for b in vector2))
                        cosine_angle = dot_product / (magnitude1 * magnitude2)
                        angle = math.degrees(math.acos(cosine_angle))
                        if angle >70 and angle <110:
                            self.coordinate_data.append(corners)
            with open('coordinates.txt','w') as coordinates:
                    json.dump(self.coordinates, coordinate, indent=4)



        elif req.get('task') == 'save_network_settings':
            newnetworksettings = req.get('data')
            print(newnetworksettings)

            command = f"""
            nmcli con modify $(nmcli -g UUID con show --active | head -n 1) \
            ipv4.method manual \
            ipv4.addresses {newnetworksettings['ipv4_address']}/24 \
            ipv4.gateway {newnetworksettings['gateway_address']} \
            ipv4.dns "8.8.8.8 8.8.4.4"
            """

            NetworkSettings.objects.update(ipv4_address=newnetworksettings['ipv4_address'], gateway_address=newnetworksettings['gateway_address'])

            # Run the command with sudo
            subprocess.run(["sudo", "bash", "-c", command], capture_output=True, text=True)
            connection_name = "preconfigured"

        
            # Bring the connection down
            subprocess.run(
                ["sudo", "nmcli", "connection", "down", connection_name],
                check=True,
                capture_output=True,
                text=True
            )

            # Bring the connection up
            subprocess.run(
                ["sudo", "nmcli", "connection", "up", connection_name],
                check=True,
                capture_output=True,
                text=True
            )

              # Bring the connection up
            subprocess.run(
                ["sudo", "reboot", "now"],
                check=True,
                capture_output=True,
                text=True
            )

        elif req.get('task') == 'get_network_settings':
            currentNetworkSettings = await get_network_settings()
            print(currentNetworkSettings)
            await self.send(text_data = json.dumps(currentNetworkSettings))




        # HANDLE REQUEST TO MAKE THE SYSTEM LIVE
        elif req.get('task') == 'monitor':
            # THIS FUNCTION WILL UPDATE THE SPACE_VEIWS.TXT WITH NEW SPACE FRAMES ON EACH CALL
            await monitor_spaces()
            with open('spaceDataForClient.txt','r') as space_views:
                SPACEVIEWS = json.load(space_views)
                await self.send(json.dumps(SPACEVIEWS)) 
            
            

            
    async def _stream_frames(self):
        try:
            async for frame in video_stream():
                await asyncio.sleep(0.1) 
                await self.send(frame) 
        except Exception as e:
            if DEBUG:print(f"Error sending frame: {e}")
        finally:
            self.streaming = False 
            self.stream_task = None 

    async def _stream_calibration_frames(self):
        async for frame in video_stream_for_calibrate():
            await asyncio.sleep(0.1) 
            data = {'frame':frame,'task':'calibrate_stream'}
            await self.send(json.dumps(data)) 
   