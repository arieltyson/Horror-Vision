import React from "react";
import styles from "./ai-block.module.css";

interface AiBlockProps {
  distortedImageUrl: string;
}

export function AiBlock({ distortedImageUrl }: AiBlockProps) {
  return (
    <div className={styles.camera}>
      <img src={distortedImageUrl || "../../../public/img/photoStub.jpeg"} alt="AI Block" />
    </div>
  );
}

export default AiBlock;
