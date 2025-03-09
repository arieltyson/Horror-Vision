import React from "react";
import styles from "./photos-block.module.css";
import { WebcamBlock, AiBlock, LoadingBlock } from "~/components";

interface PhotosBlockProps {
  webcamRef: React.RefObject<any>;
  distortedImageUrl: string;
  spinnerActive: boolean;
}

const PhotosBlock: React.FC<PhotosBlockProps> = ({ webcamRef, distortedImageUrl, spinnerActive }) => {
  return (
    <div className={styles.photosBlock}>
      <WebcamBlock webcamRef={webcamRef} />
      <LoadingBlock spinnerActive={spinnerActive} />
      <AiBlock distortedImageUrl={distortedImageUrl} />
    </div>
  );
};

export default PhotosBlock;
