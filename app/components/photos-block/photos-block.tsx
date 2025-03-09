import React from 'react'
import styles from './photos-block.module.css'
import {WebcamBlock} from "~/components";
import AiBlock from "~/components/ai-block/ai-block";

const PhotosBlock = () => {
  return (
    <div className={styles.photosBlock}>
      <WebcamBlock />
      {/*<LoadingBlock />*/}
      <AiBlock />
    </div>
  )
}

export default PhotosBlock
