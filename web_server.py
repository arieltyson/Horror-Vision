from flask import Flask, request, send_file, jsonify
import cv2
import numpy as np
import io

app = Flask(__name__)

def barrel_distortion(image, k=0.1):
    """
    Applies a simple barrel distortion effect.
    
    Parameters:
        image (numpy.ndarray): The input image in BGR format.
        k (float): Distortion coefficient. Increase for stronger distortion.
        
    Returns:
        numpy.ndarray: The distorted image.
    """
    h, w = image.shape[:2]
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
    return distorted

@app.route('/')
def index():
    return "Welcome to CV Descent – the real-time image distortion application!"

@app.route('/upload', methods=['POST'])
def upload():
    # Ensure the file part is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    # Validate that a file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read the uploaded file as bytes and convert it into a NumPy array
        file_bytes = file.read()
        np_img = np.frombuffer(file_bytes, np.uint8)
        # Decode the image using OpenCV
        img_cv = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if img_cv is None:
            return jsonify({"error": "Invalid image file"}), 400
        
        # Apply the barrel distortion effect using OpenCV
        distorted_img = barrel_distortion(img_cv, k=0.1)
        
        # Encode the processed image to JPEG format in memory
        ret, buffer = cv2.imencode('.jpg', distorted_img)
        if not ret:
            return jsonify({"error": "Failed to encode image"}), 500
        
        # Create a BytesIO stream from the encoded image
        img_io = io.BytesIO(buffer.tobytes())
        img_io.seek(0)
        
        # Return the distorted image to the client
        return send_file(img_io, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)