import {useState} from "react";
import {ActionButton, Title} from "~/components";
import styles from "./main.module.css"

export function Main() {
  const madnessState = useState(true);

  return (
    <main className={styles.main}>
      <Title title={ madnessState ? 'Descend into Madness' : 'Maintain Sanity' } />
      {/*<PhotosBlock />*/}
      <ActionButton />
    </main>
  );
}
