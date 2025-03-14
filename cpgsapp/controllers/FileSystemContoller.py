# Developed By Tecktrio At Liquidlab Infosystems
# Project: File System Contoller Methods
# Version: 1.0
# Date: 2025-03-08
# Description: A simple File System Controller to manage Files related activities

#Importing Functions
import json
import os
import time
import cv2
import numpy as np
from storage import Variables


# Function to save the image 
def save_image(filename, image):
    """
    Save an image to disk as JPEG with validation.
    
    Args:
        filename (str): Name of the file (without extension)
        image: OpenCV image (numpy array)
        
    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        # print('Saving image...')
        
        # Validate input image
        if not isinstance(image, np.ndarray):
            print("Error: Input is not a valid numpy array")
            return False
            
        if image.size == 0:
            print("Error: Image is empty")
            return False
            
        # Ensure storage directory exists
        os.makedirs('storage', exist_ok=True)
        
        # Encode image to JPEG
        success, buffer = cv2.imencode('.jpg', image)
        if not success:
            print("Error: Failed to encode image to JPEG")
            return False
            
        image_bytes = buffer.tobytes()
        
        # Save to file
        filepath = f'storage/{filename}.jpg'
        with open(filepath, 'wb') as file:
            file.write(image_bytes)
            
        # Verify the saved file
        with open(filepath, 'rb') as file:
            saved_data = file.read()
            if len(saved_data) == 0:
                print("Error: Saved file is empty")
                return False
        # print(f"Image saved successfully to {filepath}")
        return True
        
    except Exception as e:
        print(f"Error saving image: {e}")
        return False
    


def get_space_info(max_retries=5, delay=0.5):
    attempt = 0
    
    while attempt < max_retries:
        try:
            with open("storage/spaceInfo.json", "r") as spaces:
                # Read content first to avoid partial read issues
                content = spaces.read().strip()
                if not content:
                    print("Warning: JSON file is empty")
                    return {}
                
                # Try to parse the JSON
                SPACES = json.loads(content)
                if not SPACES:
                    print("Warning: File contains empty JSON structure")
                    return {}
                return SPACES
                
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt + 1}/{max_retries} - JSON error: {e}")
            attempt += 1
            if attempt == max_retries:
                print("Max retries reached, returning empty dict")
                return {}
            time.sleep(delay)  # Wait before next attempt
            
        except FileNotFoundError:
            print("File not found: storage/spaceInfo.json")
            return {}  # No point in retrying if file doesn't exist
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            attempt += 1
            if attempt == max_retries:
                print("Max retries reached due to unexpected errors")
                return {}
            time.sleep(delay)

            
    

def update_space_info(new_data):
    try:
        # Write new data to the file
        with open("storage/spaceInfo.json", "w") as spaces:
            json.dump(new_data, spaces)
            return True
            
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        return False
    except FileNotFoundError:
        print("File not found or directory doesn't exist")
        return False


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