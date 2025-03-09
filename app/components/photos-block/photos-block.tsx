import React from 'react';
import styles from './photos-block.module.css';
import { WebcamBlock, AiBlock, LoadingBlock } from "~/components";

interface PhotosBlockProps {
  spinnerActive: boolean;
}

const PhotosBlock = ({ spinnerActive }: PhotosBlockProps) => {
  return (
    <div className={styles.photosBlock}>
      <WebcamBlock />
      <LoadingBlock spinnerActive={spinnerActive} />
      <AiBlock />
    </div>
  );
}

export default PhotosBlock;
