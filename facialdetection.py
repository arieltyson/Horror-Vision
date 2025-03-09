import cv2
import time
from fer import FER

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

            # Get the most likely emotion
            emotions = emotion_detector.detect_emotions(face_roi)
            if emotions:
                emotion, score = max(emotions[0]["emotions"].items(), key=lambda item: item[1])  # Get top emotion
                text = f"{emotion} ({round(score * 100)}%)"
            else:
                text = "No emotion detected"

            # Draw face box and emotion text
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Facial Expression Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
