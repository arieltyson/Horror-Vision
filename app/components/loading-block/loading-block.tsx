import React from "react";
import styles from "./loading-block.module.css";

interface LoadingBlockProps {
  spinnerActive: boolean | undefined;
}

export function LoadingBlock({ spinnerActive }: LoadingBlockProps) {
  return (
    <div className={styles.loadingBlock}>
      {spinnerActive && (
        <svg className={styles.loaderArc} viewBox="0 0 200 200">
          <circle cx="100" cy="100" r="85" />
        </svg>
      )}

      <div className={styles.innerBlock}>
        <div className={styles.infoText}>Your emotion</div>
      </div>
    </div>
  );
}

export default LoadingBlock;
