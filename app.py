from flask import Flask, Response, render_template_string
import cv2
import numpy as np
import time
from fer import FER

app = Flask(__name__)

# ---------------- Distortion Functions ----------------

def invert_colors(face):
    """Invert the colors of the face."""
    return cv2.bitwise_not(face)

def swirl_face(face):
    """Apply a swirl effect to the face region."""
    rows, cols, _ = face.shape
    center_x, center_y = cols / 2.0, rows / 2.0
    y, x = np.indices((rows, cols))
    x = x - center_x
    y = y - center_y
    theta = np.arctan2(y, x)
    radius = np.sqrt(x**2 + y**2)
    swirl_strength = 0.05  # adjust for effect strength
    swirl_map_x = (center_x + radius * np.cos(theta + swirl_strength * radius)).astype(np.float32)
    swirl_map_y = (center_y + radius * np.sin(theta + swirl_strength * radius)).astype(np.float32)
    return cv2.remap(face, swirl_map_x, swirl_map_y, interpolation=cv2.INTER_LINEAR)

def glitch_effect(face, strength=10):
    """Apply a glitch effect by shifting color channels with a random offset."""
    offset = np.random.randint(-50, 50)
    b, g, r = cv2.split(face)
    rows, cols = b.shape[:2]
    M_pos = np.float32([[1, 0, offset], [0, 1, offset]])
    M_neg = np.float32([[1, 0, -offset], [0, 1, -offset]])
    b_shifted = cv2.warpAffine(b, M_pos, (cols, rows))
    r_shifted = cv2.warpAffine(r, M_neg, (cols, rows))
    return cv2.merge((b_shifted, g, r_shifted))

def face_swap(face_img_path, frame, face_coords):
    """
    Swap the detected face with a static image.
    Ensure that 'photoStub.jpeg' exists in your project directory.
    """
    face_img = cv2.imread(face_img_path, cv2.IMREAD_UNCHANGED)
    x, y, w, h = face_coords
    if face_img is None:
        return frame[y:y+h, x:x+w]
    return cv2.resize(face_img, (w, h))

# ---------------- Emotion Processing ----------------

def process_face(face_roi):
    """
    Use FER to detect the dominant emotion on the face ROI.
    Returns the dominant emotion (in lowercase) and its confidence score.
    """
    emotion_detector = FER()  # Optionally use FER(mtcnn=True)
    result = emotion_detector.detect_emotions(face_roi)
    if result:
        top_emotion, score = max(result[0]["emotions"].items(), key=lambda item: item[1])
        return top_emotion.strip().lower(), score
    return "neutral", 0

# ---------------- Frame Generation for Live Streaming ----------------

def generate_normal_frames():
    """Capture and stream normal frames from the webcam."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not accessible")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    cap.release()

def generate_distorted_frames():
    """
    Capture frames from the webcam, detect the first face, process it using FER,
    apply a distortion effect based on the detected emotion, and stream the frame.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not accessible")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    emotion_detector = FER()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_roi = frame[y:y+h, x:x+w].copy()
            top_emotion, score = process_face(face_roi)
            text = f"{top_emotion} ({round(score*100)}%)"
            print(f"Detected emotion: {top_emotion}, score: {score:.2f}")
            
            # Apply distortion based on emotion
            if top_emotion == "fear":
                transformed_face = glitch_effect(face_roi, strength=10)
            elif top_emotion == "happy":
                transformed_face = invert_colors(face_roi)
            elif top_emotion == "angry":
                transformed_face = swirl_face(face_roi)
            elif top_emotion == "surprise":
                transformed_face = face_swap('photoStub.jpeg', frame, (x, y, w, h))
            else:
                transformed_face = face_roi  # No distortion for neutral
            
            transformed_face = cv2.resize(transformed_face, (w, h))
            frame[y:y+h, x:x+w] = transformed_face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 0), 2)
            cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    cap.release()

# ---------------- Flask Endpoints & Frontend ----------------

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Live Video Feeds</title>
    <style>
        body { 
            background-color: #222; 
            color: white; 
            text-align: center; 
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1 { color: #e74c3c; }
        .video-container { 
            display: flex; 
            justify-content: center; 
            gap: 20px;
            flex-wrap: wrap;
        }
        .video-container div {
            flex: 1 1 45%;
        }
        img { 
            width: 100%; 
            max-width: 600px; 
            border: 5px solid #e74c3c; 
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(231,76,60,0.8);
        }
    </style>
</head>
<body>
    <h1>Live Video Feeds</h1>
    <div class="video-container">
        <div>
            <h3>Sanity</h3>
            <img src="/normal_video" alt="Normal Feed">
        </div>
        <div>
            <h3>Madness</h3>
            <img src="/distorted_video" alt="Distorted Feed">
        </div>
    </div>
    <p>Press CTRL+C in the terminal to stop the server.</p>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/normal_video')
def normal_video():
    return Response(generate_normal_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/distorted_video')
def distorted_video():
    return Response(generate_distorted_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
