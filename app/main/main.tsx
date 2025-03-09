// Main.tsx
import React, { useRef, useState } from "react";
import { ActionButton, Title, PhotosBlock } from "~/components";
import styles from "./main.module.css";
import Webcam from "react-webcam";

export function Main() {
  const [madness, setMadness] = useState<boolean>(false);
  const webcamRef = useRef<Webcam>(null);

  const capturePhoto = async () => {
    if (!webcamRef.current) return;
    const screenshotDataUrl = webcamRef.current.getScreenshot();
    if (!screenshotDataUrl) return;
    const response = await fetch(screenshotDataUrl);
    const blob = await response.blob();
    const formData = new FormData();
    formData.append("file", blob, "capture.jpg");
    const uploadResponse = await fetch("https://render-cvflask.onrender.com/upload", {
      method: "POST",
      body: formData,
    });
    if (!uploadResponse.ok) {
      throw new Error("Upload failed");
    }
    await uploadResponse.json();
  };

  return (
    <main className={styles.main}>
      <Title title={madness ? "Descend into Madness" : "Maintain Sanity"} />
      <PhotosBlock webcamRef={webcamRef} />
      <ActionButton capturePhoto={capturePhoto} setMadness={setMadness} />
    </main>
  );
}

export default Main;
