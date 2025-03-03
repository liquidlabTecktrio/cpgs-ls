import json
import cv2
from storage import Variables

def save_image(filename, image):
    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = buffer.tobytes() 
    with open(f'storage/{filename}.jpg','wb') as file:
        file.write(image_bytes)
    return True

def get_space_info():
    with open('storage/spaceInfo.txt','r') as spaces:
        SPACES = json.load(spaces)
    return SPACES


def get_mode_info():
    with open('storage/mode.txt','r') as modeData:
        mode = modeData.read()
    return mode

def change_mode_to_live():
    with open('storage/mode.txt','w') as modeData:
        modeData.write("live")

def change_mode_to_config():
    with open('storage/mode.txt','w') as modeData:
        modeData.write("config")


    # print(modeData)
    
# def get_space_info_for_client():
#     with open('spaceDataForClient.txt','r') as space_views:
#         SPACES = json.load(space_views)
#     return SPACES


def save_space_coordinates(x, y):
    Variables.points.append((x, y))
    if len(Variables.points)%5 == 0:
        Variables.coordinates.append(Variables.points)
        with open('storage/coordinates.txt','w') as coordinate:
            json.dump(Variables.coordinates, coordinate, indent=4)
        Variables.points = []

def get_space_coordinates():
        with open('storage/coordinates.txt','r')as data:
            return json.load(data)

def clear_space_coordinates():
    Variables.coordinates = []
    with open('storage/coordinates.txt','w') as coordinate:
        json.dump(Variables.coordinates, coordinate, indent=4)
    return True