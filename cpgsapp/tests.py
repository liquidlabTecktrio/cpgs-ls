import cv2
import numpy as np
from paddleocr import PaddleOCR

# Load image

from picamera2 import Picamera2
cap = Picamera2()
cap.start()

frame = cap.capture_array()
# # Convert to grayscale
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# # Apply Gaussian blur
# blurred = cv2.GaussianBlur(gray, (5,5), 0)

# # Apply Adaptive Thresholding
# thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

# # Save processed image and run OCR
# cv2.imwrite("processed_car.jpg", thresh)
while True:
    ocr = PaddleOCR(use_angle_cls=True, use_gpu=False)
    results = ocr.ocr(frame, cls=True)
    
    # Print results
    for line in results[0]:
        print(line[1][0])  # Extracted text

