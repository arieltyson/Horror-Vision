from flask import Flask, request, Response, jsonify
import cv2
import numpy as np
import io
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def barrel_distortion(image, k=0.1):
    app.logger.info("Starting barrel distortion with k=%s", k)
    h, w = image.shape[:2]
    app.logger.info("Input image dimensions: %sx%s", w, h)
    
    # Create a coordinate grid for mapping
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    x_c = w / 2
    y_c = h / 2
    
    # Normalize coordinates to center of image
    x_norm = (x - x_c) / x_c
    y_norm = (y - y_c) / y_c
    
    # Compute radial distance from center
    r = np.sqrt(x_norm**2 + y_norm**2)
    
    # Apply the distortion factor
    factor = 1 + k * r**2
    
    # Compute new coordinates
    x_distorted = x_c + x_norm * x_c * factor
    y_distorted = y_c + y_norm * y_c * factor

    map_x = x_distorted.astype(np.float32)
    map_y = y_distorted.astype(np.float32)
    
    # Remap the original image to the new coordinates
    distorted = cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR)
    app.logger.info("Finished applying barrel distortion")
    return distorted

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
        
        # Apply distortion
        distorted_img = barrel_distortion(img_cv, k=0.1)
        
        app.logger.info("Encoding distorted image")
        ret, buffer = cv2.imencode('.jpg', distorted_img)
        if not ret or buffer.size == 0:
            app.logger.error("Failed to encode image or encoded image is empty")
            return jsonify({"error": "Failed to encode image"}), 500
        
        app.logger.info("Encoded image size: %d bytes", buffer.size)
        
        # Return the distorted image using Response
        app.logger.info("Sending distorted image back to client")
        return Response(buffer.tobytes(), mimetype='image/jpeg')
    except Exception as e:
        app.logger.exception("An error occurred while processing the image")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)