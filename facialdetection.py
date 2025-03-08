import cv2
import time

def main():
    # opening tthe webcam
    cap = cv2.VideoCapture(0)
    retry_count = 5
    while not cap.isOpened() and retry_count > 0:
        print(f"Retrying camera initialization... ({retry_count} attempts left)")
        time.sleep(1)
        cap = cv2.VideoCapture(0)
        retry_count -= 1

    if not cap.isOpened():
        print(" Error: Camera not accessible.")
        return
    else:
        print(" Camera initialized successfully.")

    # Load the Haar Cascade for face detection.
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        print("❌ Error: Could not load face cascade classifier.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Failed to capture frame.")
            break

        # Convert frame to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale image
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Show the resulting frame
        cv2.imshow("Face Recognition", frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
