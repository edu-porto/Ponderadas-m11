import cv2
import urllib.request
import numpy as np

# Replace with the IP address of your ESP32-CAM
ESP32_CAM_URL = 'http://10.128.0.35:81/stream'

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Open a connection to the video stream
stream = urllib.request.urlopen(ESP32_CAM_URL)

# Initialize the byte array for image frames
bytes_data = b''

while True:
    # Read in chunks of the stream
    bytes_data += stream.read(1024)
    
    # Look for the start and end markers of a JPEG frame
    a = bytes_data.find(b'\xff\xd8')  # JPEG start
    b = bytes_data.find(b'\xff\xd9')  # JPEG end
    
    if a != -1 and b != -1:
        # Extract the JPEG image and convert it to a NumPy array
        jpg_data = bytes_data[a:b + 2]
        bytes_data = bytes_data[b + 2:]
        img = cv2.imdecode(np.frombuffer(jpg_data, dtype=np.uint8), cv2.IMREAD_COLOR)
        
        # Convert the image to grayscale for Haar Cascade processing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Perform face detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Draw bounding boxes around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Display the processed frame
        cv2.imshow('ESP32-CAM Face Detection', img)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Clean up
cv2.destroyAllWindows()
