import React from "react";
import Webcam from "react-webcam";
import styles from "./webcam-block.module.css";

export function WebcamBlock() {
  return (
    <div>
      <div className={styles.camera}>
        <Webcam />
      </div>
    </div>
  )
}

export default WebcamBlock
