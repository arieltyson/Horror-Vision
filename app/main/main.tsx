import React, { useRef, useState } from "react";
import { ActionButton, Title, PhotosBlock } from "~/components";
import styles from "./main.module.css";
import Webcam from "react-webcam";

export function Main() {
  const [madness, setMadness] = useState<boolean>(false);
  const [distortedImageUrl, setDistortedImageUrl] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const webcamRef = useRef<Webcam>(null);

  const capturePhoto = async () => {
    if (!webcamRef.current) return;
    const screenshotDataUrl = webcamRef.current.getScreenshot();
    if (!screenshotDataUrl) return;
    const response = await fetch(screenshotDataUrl);
    const blob = await response.blob();
    const formData = new FormData();
    formData.append("file", blob, "capture.jpg");
    setLoading(true);
    try {
      const uploadResponse = await fetch("https://render-cvflask.onrender.com/upload", {
        method: "POST",
        body: formData,
      });
      if (!uploadResponse.ok) {
        throw new Error("Upload failed");
      }
      const distortedBlob = await uploadResponse.blob();
      if (distortedBlob.size === 0) {
        console.error("Received empty image blob");
        return;
      }
      const url = URL.createObjectURL(distortedBlob);
      setDistortedImageUrl(url);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className={styles.main}>
      <Title title="Descend into Madness" />
      <PhotosBlock webcamRef={webcamRef} distortedImageUrl={distortedImageUrl} spinnerActive={loading} />
      <ActionButton capturePhoto={capturePhoto} setMadness={setMadness} />
    </main>
  );
}

export default Main;
