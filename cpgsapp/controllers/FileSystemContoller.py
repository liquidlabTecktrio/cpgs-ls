import json
import cv2
import os
from storage import Variables

STORAGE_PATH = 'storage/'

# Function to save the image
def save_image(filename, image):
    """Save an image in JPG format to the storage directory."""
    _, buffer = cv2.imencode('.jpg', image)
    with open(f'{STORAGE_PATH}{filename}.jpg', 'wb') as file:
        file.write(buffer.tobytes())
    return True


def get_space_info():
    """Retrieve space information from a file."""
    file_path = f'{STORAGE_PATH}spaceInfo.txt'
    
    if not os.path.exists(file_path):
        return {}  # Return an empty dict if file does not exist

    with open(file_path, 'r') as spaces:
        try:
            return json.load(spaces)  # Try parsing JSON
        except json.JSONDecodeError as e:
            print(f"Error loading JSON: {e}")
            return {}  # Return an empty dictionary instead of crashing


# Function to get current mode (live/config)
def get_mode_info():
    """Retrieve the current mode (live/config) from a file."""
    file_path = f'{STORAGE_PATH}mode.txt'
    if not os.path.exists(file_path):
        return "config"  # Default mode if file is missing

    with open(file_path, 'r') as modeData:
        return modeData.read().strip()

# Function to change mode to live
def change_mode_to_live():
    """Change the mode to 'live'."""
    with open(f'{STORAGE_PATH}mode.txt', 'w') as modeData:
        modeData.write("live")

# Function to change mode to config
def change_mode_to_config():
    """Change the mode to 'config'."""
    with open(f'{STORAGE_PATH}mode.txt', 'w') as modeData:
        modeData.write("config")

# Function to save space coordinates
def save_space_coordinates(x, y):
    """Save space coordinates in batches of 5."""
    Variables.points.append((x, y))
    
    if len(Variables.points) % 5 == 0:
        Variables.coordinates.append(Variables.points)
        with open(f'{STORAGE_PATH}coordinates.txt', 'w') as coordinate:
            json.dump(Variables.coordinates, coordinate, indent=4)
        Variables.points.clear()  # Clear only if written to file

# Function to get space coordinates
def get_space_coordinates():
    """Retrieve space coordinates from a file."""
    file_path = f'{STORAGE_PATH}coordinates.txt'
    if not os.path.exists(file_path):
        return []  # Return empty list if file does not exist

    with open(file_path, 'r') as data:
        return json.load(data)

# Function to clear space coordinates
def clear_space_coordinates():
    """Clear stored space coordinates."""
    Variables.coordinates.clear()
    with open(f'{STORAGE_PATH}coordinates.txt', 'w') as coordinate:
        json.dump([], coordinate, indent=4)
    return True
