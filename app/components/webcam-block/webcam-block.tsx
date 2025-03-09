// WebcamBlock.tsx
import React from "react";
import Webcam from "react-webcam";
import styles from "./webcam-block.module.css";

interface WebcamBlockProps {
  webcamRef: React.RefObject<Webcam>;
}

export function WebcamBlock({ webcamRef }: WebcamBlockProps) {
  return (
    <div>
      <div className={styles.camera}>
        <Webcam ref={webcamRef} audio={false} screenshotFormat="image/jpeg" />
      </div>
    </div>
  );
}

export default WebcamBlock;
