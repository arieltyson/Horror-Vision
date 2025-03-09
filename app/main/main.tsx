import {useState} from "react";
import {ActionButton, Title} from "~/components";
import styles from "./main.module.css"
import PhotosBlock from "~/components/photos-block/photos-block";

export function Main() {
  const madnessState = useState(true);

  return (
    <main className={styles.main}>
      <Title title={madnessState ? 'Descend into Madness' : 'Maintain Sanity'}/>
      <PhotosBlock/>
      <ActionButton/>
    </main>
  );
}
