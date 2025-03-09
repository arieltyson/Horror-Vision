from flask import Flask, request, Response, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import io
import logging
from fer import FER  # For emotion detection

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# ---- Distortion Helper Functions ----

def invert_colors(face):
    """Inverts the colors of the face region."""
    return cv2.bitwise_not(face)

def glitch_effect(face, multiplier):
    """
    Applies a glitch effect by shifting color channels.
    The multiplier adjusts the intensity of the glitch.
    """
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

# (Optional: Retained in case needed for future effects)
def swirl_face(face, multiplier):
    rows, cols, _ = face.shape
    center_x, center_y = cols // 2, rows // 2
    y, x = np.indices((rows, cols))
    x = x - center_x
    y = y - center_y
    theta = np.arctan2(y, x)
    radius = np.sqrt(x**2 + y**2)
    swirl_strength = 0.05 * multiplier
    swirl_map_x = (center_x + radius * np.cos(theta + swirl_strength * radius)).astype(np.float32)
    swirl_map_y = (center_y + radius * np.sin(theta + swirl_strength * radius)).astype(np.float32)
    return cv2.remap(face, swirl_map_x, swirl_map_y, interpolation=cv2.INTER_LINEAR)

def face_swap(face_img_path, frame, face_coords):
    face_img = cv2.imread(face_img_path, cv2.IMREAD_UNCHANGED)
    x, y, w, h = face_coords
    resized_face = cv2.resize(face_img, (w, h))
    return resized_face

# ---- Main Processing Function ----

def process_emotion_distortion(image):
    """
    Detects faces and emotions in the image and applies distortions based on emotion:
      - "fear": glitch effect with raw score.
      - "happy": invert colors.
      - "angry", "disgust", "surprise", or "sad": glitch effect with amplified multiplier (score * 1.5).
      - Otherwise, no change is applied.
    """
    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        app.logger.error("Could not load face cascade classifier.")
        return image

    # Initialize FER emotion detector
    emotion_detector = FER()

    # Convert image to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    app.logger.info("Detected %d faces", len(faces))

    for (x, y, w, h) in faces:
        face_roi = image[y:y+h, x:x+w]
        emotions = emotion_detector.detect_emotions(face_roi)
        textEmotion = "neutral"
        score = 0

        if emotions and len(emotions) > 0 and "emotions" in emotions[0]:
            emotion, score = max(emotions[0]["emotions"].items(), key=lambda item: item[1])
            emotion = emotion.strip().lower()
            textEmotion = emotion
        else:
            textEmotion = "neutral"

        # Overlay the detected emotion text
        cv2.putText(image, f"{textEmotion}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if textEmotion == "fear":
            face_modified = glitch_effect(face_roi, score)
            face_modified = cv2.resize(face_modified, (w, h))
        elif textEmotion == "happy":
            face_modified = invert_colors(face_roi)
        elif textEmotion in ["angry", "disgust", "surprise", "sad"]:
            face_modified = glitch_effect(face_roi, score * 1.5)
            face_modified = cv2.resize(face_modified, (w, h))
        else:
            face_modified = face_roi  # No change for neutral or other emotions

        image[y:y+h, x:x+w] = face_modified
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 0), 2)

    return image

# ---- Flask Endpoints ----

@app.route('/')
def index():
    app.logger.info("Index route accessed")
    return "Welcome to CV Descent – the real-time image distortion application!"

@app.route('/upload', methods=['POST'])
def upload():
    app.logger.info("Upload route accessed from %s", request.remote_addr)
    
    if 'file' not in request.files:
        app.logger.error("No file part in the request")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    try:
        app.logger.info("Reading uploaded file")
        file_bytes = file.read()
        np_img = np.frombuffer(file_bytes, np.uint8)
        
        app.logger.info("Decoding image")
        img_cv = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if img_cv is None:
            app.logger.error("Failed to decode image")
            return jsonify({"error": "Invalid image file"}), 400
        
        app.logger.info("Image decoded successfully: shape=%s", img_cv.shape)
        
        # Process the image with emotion-based distortions
        distorted_img = process_emotion_distortion(img_cv)
        
        app.logger.info("Encoding distorted image")
        ret, buffer = cv2.imencode('.jpg', distorted_img)
        if not ret or buffer.size == 0:
            app.logger.error("Failed to encode image or encoded image is empty")
            return jsonify({"error": "Failed to encode image"}), 500
        
        app.logger.info("Encoded image size: %d bytes", buffer.size)
        
        # Save the distorted image locally for debugging (test_image.jpg)
        with open('test_image.jpg', 'wb') as f:
            f.write(buffer.tobytes())
        app.logger.info("Saved distorted image locally as test_image.jpg")
        
        app.logger.info("Sending distorted image back to client")
        return Response(buffer.tobytes(), mimetype='image/jpeg')
    except Exception as e:
        app.logger.exception("An error occurred while processing the image")
        return jsonify({"error": str(e)}), 500

@app.route('/test_image', methods=['GET'])
def test_image():
    try:
        app.logger.info("Serving test_image.jpg")
        return send_file('test_image.jpg', mimetype='image/jpeg')
    except Exception as e:
        app.logger.exception("Error serving test image")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)