import cv2
import time
from fer import FER
import numpy as np

def main():
    # Initialize webcam
    
    cap = cv2.VideoCapture(0)
    retry_count = 5

    while not cap.isOpened() and retry_count > 0:
        print(f"Retrying camera initialization... ({retry_count} attempts left)")
        time.sleep(1)
        cap = cv2.VideoCapture(0)
        retry_count -= 1

    if not cap.isOpened():
        print("❌ Error: Camera not accessible.")
        return
    else:
        print("✅ Camera initialized successfully.")

    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        print("❌ Error: Could not load face cascade classifier.")
        return

    # Initialize FER (Facial Expression Recognizer)
    emotion_detector = FER()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Failed to capture frame.")
            break

        # Convert frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Analyze emotions
        results = emotion_detector.detect_emotions(frame)

        # Draw rectangles around detected faces and display emotions
        for (x, y, w, h) in faces:
            face_roi = frame[y:y + h, x:x + w]  # Extract face region
            face = swirl_face(face_roi)
            frame[y:y + h, x:x + w] = face

            # Draw face box and emotion text
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)

        cv2.imshow("Facial Expression Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def invert_colors(face):
    return cv2.bitwise_not(face)

def swirl_face(face):
    rows, cols, _ = face.shape
    center_x, center_y = cols // 2, rows // 2

    y, x = np.indices((rows, cols))
    x = x - center_x
    y = y - center_y
    theta = np.arctan2(y, x)
    radius = np.sqrt(x**2 + y**2)

    swirl_strength = 0.05  # Increase for stronger effect
    swirl_map_x = (center_x + radius * np.cos(theta + swirl_strength * radius)).astype(np.float32)
    swirl_map_y = (center_y + radius * np.sin(theta + swirl_strength * radius)).astype(np.float32)

    return cv2.remap(face, swirl_map_x, swirl_map_y, interpolation=cv2.INTER_LINEAR)

if __name__ == "__main__":
    main()