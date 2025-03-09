from flask import Flask, Response
import cv2
import time
from fer import FER
import numpy as np

app = Flask(__name__)

def invert_colors(face):
    return cv2.bitwise_not(face)

def swirl_face(face, multiplier):
    rows, cols, _ = face.shape
    center_x, center_y = cols // 2, rows // 2

    y, x = np.indices((rows, cols))
    x = x - center_x
    y = y - center_y
    theta = np.arctan2(y, x)
    radius = np.sqrt(x**2 + y**2)

    swirl_strength = 0.05 * multiplier  # Adjust for desired effect strength
    swirl_map_x = (center_x + radius * np.cos(theta + swirl_strength * radius)).astype(np.float32)
    swirl_map_y = (center_y + radius * np.sin(theta + swirl_strength * radius)).astype(np.float32)

    return cv2.remap(face, swirl_map_x, swirl_map_y, interpolation=cv2.INTER_LINEAR)

def glitch_effect(face, multiplier):
    # Clamp multiplier between 0 and 1
    multiplier = max(0, min(multiplier, 1))
    intensity = int(10 + (multiplier ** 2) * 150)

    b, g, r = cv2.split(face)
    rows, cols = b.shape[:2]
    M_pos = np.float32([[1, 0, np.random.randint(0, intensity)],
                        [0, 1, np.random.randint(0, intensity)]])
    M_neg = np.float32([[1, 0, np.random.randint(-intensity, 0)],
                        [0, 1, np.random.randint(-intensity, 0)]])

    b_shifted = cv2.warpAffine(b, M_pos, (cols, rows))
    r_shifted = cv2.warpAffine(r, M_neg, (cols, rows))

    return cv2.merge((b_shifted, g, r_shifted))

def generate_frames():
    cap = cv2.VideoCapture(0)
    retry_count = 5

    # Try to initialize the camera
    while not cap.isOpened() and retry_count > 0:
        print(f"Retrying camera initialization... ({retry_count} attempts left)")
        time.sleep(1)
        cap = cv2.VideoCapture(0)
        retry_count -= 1

    if not cap.isOpened():
        print("❌ Error: Camera not accessible.")
        return

    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        print("❌ Error: Could not load face cascade classifier.")
        return

    # Initialize the emotion detector
    emotion_detector = FER()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Failed to capture frame.")
            break

        # Convert frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_roi = frame[y:y + h, x:x + w]
            emotions = emotion_detector.detect_emotions(face_roi)
            textEmotion = "neutral"
            score = 0

            if emotions:
                emotion, score = max(emotions[0]["emotions"].items(), key=lambda item: item[1])
                emotion = emotion.strip().lower()
                text = f"{emotion} ({round(score * 100)}%)"
                textEmotion = emotion
            else:
                text = "No emotion detected"

            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Apply effects based on detected emotion
            if textEmotion == "fear":
                face_effect = glitch_effect(face_roi, score)
                face_effect = cv2.resize(face_effect, (w, h))
            elif textEmotion == "happy":
                face_effect = invert_colors(face_roi)
            elif textEmotion in ["angry", "disgust", "surprise"]:
                face_effect = glitch_effect(face_roi, score * 1.5)
                face_effect = cv2.resize(face_effect, (w, h))
            else:
                face_effect = face_roi

            frame[y:y + h, x:x + w] = face_effect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield frame in HTTP multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return "Test server running. Use the /video_feed endpoint to access the video stream."

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Run on all interfaces for testing on the server
    app.run(host='0.0.0.0', port=5000, debug=True)
