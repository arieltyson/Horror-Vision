// ActionButton.tsx
import React, { useState } from "react";
import styles from "./action-button.module.css";

interface ActionButtonProps {
  capturePhoto: () => void | Promise<void>;
  setMadness: React.Dispatch<React.SetStateAction<boolean>>;
}

export function ActionButton({ capturePhoto, setMadness }: ActionButtonProps) {
  const [repeatState, setRepeatState] = useState(false);
  const [matchValue, setMatchValue] = useState(51);

  const handleClick = async () => {
    if (!repeatState) {
      const randomVal = Math.floor(Math.random() * 100);
      setMatchValue(randomVal);
      await capturePhoto();
      setMadness(true);
    } else {
      setMatchValue(51);
      setMadness(false);
    }
    setRepeatState(!repeatState);
  };

  let variantClass = styles.btnDefault;
  if (repeatState) {
    variantClass = matchValue > 50 ? styles.btnGreen : styles.btnRed;
  }

  return (
    <button onClick={handleClick} className={`${styles.btnGeneric} ${variantClass}`}>
      {repeatState ? "Retake a Selfie" : "Take a Selfie"}
    </button>
  );
}

export default ActionButton;
