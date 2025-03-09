import React, { useState } from 'react';
import styles from './action-button.module.css';

export function ActionButton() {
  const [repeatState, setRepeatState] = useState(false);
  const [matchValue, setMatchValue] = useState(51);

  const handleClick = () => {
    if (!repeatState) {
      const randomVal = Math.floor(Math.random() * 100);
      setMatchValue(randomVal);
    } else {
      setMatchValue(51);
    }
    setRepeatState(!repeatState);
  };

  // Decide which variant class to apply based on state
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
