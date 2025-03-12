# Developed By Tecktrio At Liquidlab Infosystems
# Project: File System Contoller Methods
# Version: 1.0
# Date: 2025-03-08
# Description: A simple File System Controller to manage Files related activities

#Importing Functions
import json
import os
import shutil
import tempfile
import cv2
from storage import Variables


# Function to save the image 
def save_image(filename, image):
    """Save an image safely with basic error handling."""
    try:
        os.makedirs("storage", exist_ok=True)
        file_path = os.path.join("storage", f"{filename}.jpg")
        with tempfile.NamedTemporaryFile(delete=False, dir="storage") as tmp:
            if not cv2.imwrite(tmp.name, image):
                raise Exception("Failed to write image")
            shutil.move(tmp.name, file_path)
        return True, f"Image saved to {file_path}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_space_info():
    try:
        with open("storage/spaceinfo.txt", "r") as spaces:
            content = spaces.read().strip()
            if not content:
                print("Warning: File is empty")
                return {}  # Return a default value
            SPACES = json.loads(content)
            return SPACES
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        return {}  # Fallback to avoid crashing
    except FileNotFoundError:
        print("File not found")
        return {}


# Function to get to know which mode is being used (live/config)
def get_mode_info():
    with open('storage/mode.txt','r') as modeData:
        mode = modeData.read()
    return mode


# Function called to change from config to live
def change_mode_to_live():
    with open('storage/mode.txt','w') as modeData:
        modeData.write("live")


# Function called to change from live to config
def change_mode_to_config():
    with open('storage/mode.txt','w') as modeData:
        modeData.write("config")


# Function to save space coordinates
def save_space_coordinates(x, y):
    Variables.points.append((x, y))
    if len(Variables.points)%5 == 0:
        Variables.coordinates.append(Variables.points)
        with open('storage/coordinates.txt','w') as coordinate:
            json.dump(Variables.coordinates, coordinate, indent=4)
        Variables.points = []


# Function to get space coordinates
def get_space_coordinates():
        with open('storage/coordinates.txt','r')as data:
            return json.load(data)
        

# To clear the space coordinates
def clear_space_coordinates():
    Variables.coordinates = []
    with open('storage/coordinates.txt','w') as coordinate:
        json.dump(Variables.coordinates, coordinate, indent=4)
    return True