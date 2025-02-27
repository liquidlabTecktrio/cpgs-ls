# ImageProcessingController
import base64
import json
import math
from multiprocessing import Pool
import threading
import time
import cv2
import django
import numpy as np
from cpgsapp.controllers.FileSystemContoller import get_space_coordinates, get_space_info, save_image
from cpgsapp.controllers.HardwareController import update_pilot
from cpgsapp.controllers.NetworkController import update_server
from cpgsserver.settings import IS_PI_CAMERA_SOURCE
from storage import Variables
# from ultralytics import YOLO
# from paddleocr import PaddleOCR

# model = YOLO("storage/best.pt")
# ocr = PaddleOCR(
#     lang="en",  
#     det_model_dir="models/ch_PP-OCRv3_det_infer",  
#     rec_model_dir="models/ch_PP-OCRv3_rec_infer",  
#     use_angle_cls=False,  # Disable angle classification for speed
#     use_gpu=False
# )
if IS_PI_CAMERA_SOURCE:
    from picamera2 import Picamera2
    Variables.cap = Picamera2()
    Variables.cap.start()
    
else: Variables.cap = cv2.VideoCapture(0)

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

# def dectect_license_plate(space):
#     """Detects license plates in a frame and returns the cropped license plate image."""
#     isLicensePlate = False
#     results = model.predict(space, conf=0.5)
#     license_plate = None
#     for result in results:
#         for box in result.boxes:
#             x1, y1, x2, y2 = map(int, box.xyxy[0])
#             cls = int(box.cls[0])
#             if cls == 0: 
#                 isLicensePlate = True 
#                 cv2.rectangle(space, (x1, y1), (x2, y2), (0, 255, 0), 3)
#                 cv2.putText(space, "License Plate", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
#                 license_plate = space[y1:y2, x1:x2]
#     return space, license_plate, isLicensePlate


import cv2
def dectect_license_plate(space):
    # Load the pre-trained Haar Cascade for license plate detection
    plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')

    # Load image
    isLicensePlate = False
    # image = cv2.imread('test3.jpg')  # Replace 'your_image.jpg' with your image file
    gray = cv2.cvtColor(space, cv2.COLOR_BGR2GRAY)

    # Detect plates
    license_plate = None
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(25, 25))

    # Loop through all detected plates and draw rectangles around them
    for (x, y, w, h) in plates:
        isLicensePlate = True 
        cv2.rectangle(space, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw rectangle in green color
        license_plate = space[y:y+h, x:x+w]
    
    return space, license_plate, isLicensePlate

# # Show the image with detected plates
# cv2.imshow("Detected Number Plates", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


def RecognizeLicensePlate(licensePlate):
    scanRound = 0
    maxConfidence = 0
    licenseNumberWithMoreConfidence = ""
    if licensePlate is not None:
        while scanRound < 5: 
            scanRound  = scanRound + 1
            results = ocr.ocr(licensePlate, cls=True)
            if results:
                for line in results[0]:
                    licenseNumber  = line[1][0]
                    confidence =  line[1][1]
                    if confidence > maxConfidence:
                        maxConfidence = confidence
                        licenseNumberWithMoreConfidence = licenseNumber
        print('Captured', licenseNumberWithMoreConfidence,"with confidence", confidence)
        return licenseNumberWithMoreConfidence
    return licenseNumberWithMoreConfidence


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

def capture():
    """Synchronous capture function for threading or multiprocessing."""
    print('camera started')
    while True:
        if IS_PI_CAMERA_SOURCE:
            frame = Variables.cap.capture_array()
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                print("Failed to capture frame from PiCamera")
                time.sleep(0.1)
                continue
        else:
            ret, frame = Variables.cap.read()
            if not ret:
                print("Failed to capture frame from VideoCapture")
                time.sleep(0.1)
                continue

        if frame is not None and frame.size > 0:  # Ensure frame is valid
            frame = cv2.resize(frame, (720,576 ), interpolation=cv2.INTER_AREA)
            save_image('camera_view', frame)
            # print("Frame captured and saved")
        else:
            print("Invalid frame received")

        time.sleep(0.1)  # Control frame rate
        
    

def get_camera_view_with_space_coordinates():
    frame = cv2.imread("storage/camera_view.jpg")
    
    with open('storage/coordinates.txt','r')as data:
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

    # data = {'frame':readyToSendFrame,'task':'calibrate_stream'}
    return readyToSendFrame



def getSpaceMonitorWithLicensePlateDectection(spaceID, x, y, w, h ):
        
        print(f'Scanning spaceID {spaceID}')
        camera_view = cv2.imread("storage/camera_view.jpg")  
        space_view = camera_view[y:y+h, x:x+w]

        Variables.licensePlateinSpace, Variables.licensePlate, isLicensePlate =  dectect_license_plate(space_view)
        Variables.licensePlateinSpaceInBase64 = image_to_base64(Variables.licensePlateinSpace)

        

        for space in Variables.SPACES:
            if space['spaceID'] == spaceID:
                if isLicensePlate:
                    Variables.licensePlateBase64 = image_to_base64(Variables.licensePlate)
                    space['spaceStatus'] = "occupied"
                space['spaceFrame'] = Variables.licensePlateinSpaceInBase64
                space['licensePlate'] = Variables.licensePlateBase64
                

        
        with open('storage/spaceInfo.txt', 'w') as space_views:
            json.dump(Variables.SPACES, space_views, indent=4)

        return {"status":"done"}


def get_monitoring_spaces():
    '''
    SCAN the parking slot FOR VEHICLE
    '''      

    # print("started")       
    poslist = get_space_coordinates()

    Variables.SPACES = []
    
    Variables.TOTALSPACES = len(poslist)
    print('Found ',Variables.TOTALSPACES , "space")
    for spaceID in range(Variables.TOTALSPACES):

        obj = {
            'spaceID':spaceID,
            'spaceStatus':'vaccant',
            'spaceFrame':'',
            'licenseNumber':""
        }

        Variables.SPACES.append(obj)
    
    
    with open('storage/spaceInfo.txt', 'w') as spaces:
        json.dump(Variables.SPACES, spaces,indent=4)

    for spaceID, pos in enumerate(poslist):
        SpaceCoordinates = np.array([[pos[0][0], pos[0][1]], [pos[1][0], pos[1][1]], [pos[2][0], pos[2][1]], [pos[3][0], pos[3][1]]])
        pts = np.array(SpaceCoordinates, np.int32)
        x, y, w, h = cv2.boundingRect(pts)
        # Variables.space_coordinate_list.append((spaceID,x,y,w,h))

        getSpaceMonitorWithLicensePlateDectection(spaceID, x, y, w, h)

    # if len(Variables.space_coordinate_list) > 0:
    #     with Pool(initializer=django.setup) as pool: 
    #         pool.map(getSpaceMonitorWithLicensePlateDectection, Variables.space_coordinate_list)

    # print("space info", get_space_info())
    if IS_PI_CAMERA_SOURCE:
        update_pilot()
        
    update_server()
    return get_space_info()



# def auto_calibrate(frame):
#     frameInGray = cv2.cvtColor((frame), cv2.COLOR_BGR2GRAY)
#     frameInGrayAndBlur = cv2.GaussianBlur(frameInGray, (3, 3), 2)
#     with open("config.json","rb") as configurations:
#         config = json.load(configurations)
#         configuration_data = {
#             "CameraFilterThresh" : config["threshold"],
#             "serverIP" :config["server_ip"],
#             "serverPort" : config["server_port"],
#             "DEBUG" : config["DEBUG"],
#             "CameraFilterMaximumThresh" : 255,
#             "CameraFilterThreshOnCalibrate" : config["threshold"],
#             "CameraFilterMaximumThreshOnCalibrate" : 255,
#             "BoostThreshAT":2,
#         }
#     _,ThreshHoldedFrame  = cv2.threshold(frameInGrayAndBlur,
#                                             configuration_data["CameraFilterThreshOnCalibrate"], 
#                                             configuration_data["CameraFilterMaximumThreshOnCalibrate"], 
#                                             cv2.THRESH_BINARY_INV)
#     imgmedian = cv2.medianBlur(ThreshHoldedFrame, 3 )
#     kernal = np.ones((3, 3), np.uint8)
#     imgdilate = cv2.dilate(imgmedian, kernel=kernal, iterations=configuration_data["BoostThreshAT"])
#     contours, _ = cv2.findContours(imgdilate, cv2.INTER_AREA, cv2.CHAIN_APPROX_SIMPLE)
#     self.coordinate_data = []
#     for slotIndex, contour in enumerate(contours):
#         area = cv2.contourArea(contour)
#         perimeter = cv2.arcLength(contour, True)
#         area_threshold = 500
#         perimeter_threshold = 200
#         if area > area_threshold and perimeter > perimeter_threshold:
#             epsilon = 0.02 * perimeter 
#             approx_polygon = cv2.approxPolyDP(contour, epsilon, True)
#             x, y, w, h = cv2.boundingRect(approx_polygon)
#             if len(approx_polygon) == 4 and h > w :
#                 corners = [tuple(coord[0]) for coord in approx_polygon]
#                 vector1 = (corners[1][0] - corners[0][0], corners[1][1] - corners[0][1])
#                 vector2 = (corners[2][0] - corners[1][0], corners[2][1] - corners[1][1])
#                 dot_product = sum(a * b for a, b in zip(vector1, vector2))
#                 magnitude1 = math.sqrt(sum(a * a for a in vector1))
#                 magnitude2 = math.sqrt(sum(b * b for b in vector2))
#                 cosine_angle = dot_product / (magnitude1 * magnitude2)
#                 angle = math.degrees(math.acos(cosine_angle))
#                 if angle >70 and angle <110:
#                     self.coordinate_data.append(corners)
#     with open('coordinates.txt','w') as coordinates:
#             json.dump(self.coordinates, coordinate, indent=4)

