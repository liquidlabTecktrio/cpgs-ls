import cv2

# Load the pre-trained Haar Cascade for license plate detection
plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')

# Load image
image = cv2.imread('test3.jpg')  # Replace 'your_image.jpg' with your image file
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect plates
plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(25, 25))

# Loop through all detected plates and draw rectangles around them
for (x, y, w, h) in plates:
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw rectangle in green color

# Show the image with detected plates
cv2.imshow("Detected Number Plates", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
