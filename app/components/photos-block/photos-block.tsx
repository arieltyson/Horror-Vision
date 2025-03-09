import React from "react";
import styles from "./photos-block.module.css";
import { WebcamBlock, AiBlock, LoadingBlock } from "~/components";

interface PhotosBlockProps {
  webcamRef: React.RefObject<any>;
  distortedImageUrl: string;
}

const PhotosBlock: React.FC<PhotosBlockProps> = ({ webcamRef, distortedImageUrl }) => {
  return (
    <div className={styles.photosBlock}>
      <WebcamBlock webcamRef={webcamRef} />
      <LoadingBlock spinnerActive={false} />
      <AiBlock distortedImageUrl={distortedImageUrl} />
    </div>
  );
};

export default PhotosBlock;
