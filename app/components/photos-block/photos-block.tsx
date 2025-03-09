// PhotosBlock.tsx
import React from "react";
import styles from "./photos-block.module.css";
import { WebcamBlock, AiBlock, LoadingBlock } from "~/components";

interface PhotosBlockProps {
  webcamRef: React.RefObject<any>;
}

const PhotosBlock: React.FC<PhotosBlockProps> = ({ webcamRef }) => {
  return (
    <div className={styles.photosBlock}>
      <WebcamBlock webcamRef={webcamRef} />
      <LoadingBlock />
      <AiBlock />
    </div>
  );
};

export default PhotosBlock;
