import React, { useState } from "react";
import styles from "./action-button.module.css";

interface ActionButtonProps {
  setSpinnerActive: React.Dispatch<React.SetStateAction<boolean>>;
}

export function ActionButton({ setSpinnerActive }: ActionButtonProps) {
  const [repeatState, setRepeatState] = useState<boolean>(false);
  const [matchValue, setMatchValue] = useState<number>(51);

  const handleClick = () => {
    if (!repeatState) {
      const randomVal = Math.floor(Math.random() * 100);
      setMatchValue(randomVal);
      setSpinnerActive(true);
    } else {
      setMatchValue(51);
      setSpinnerActive(false);
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
