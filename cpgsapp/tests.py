import cv2
import numpy as np
from paddleocr import PaddleOCR

# Load image
image = cv2.imread("0.jpg")

# # Convert to grayscale
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# # Apply Gaussian blur
# blurred = cv2.GaussianBlur(gray, (5,5), 0)

# # Apply Adaptive Thresholding
# thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

# # Save processed image and run OCR
ocr = PaddleOCR(
    lang="en",  
    det_model_dir="models/ch_PP-OCRv3_det_infer",  
    rec_model_dir="models/ch_PP-OCRv3_rec_infer",  
    use_angle_cls=False,  # Disable angle classification for speed
    use_gpu=False
)

# cv2.imwrite("processed_car.jpg", thresh)
while True:
    results = ocr.ocr("0.jpg", cls=True)
    
    # Print results
    for line in results[0]:
        print(line[1][0])  # Extracted text

# Show image
# cv2.imshow("Processed Image", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
