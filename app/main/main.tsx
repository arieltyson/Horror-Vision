import React, { useState } from "react";
import { ActionButton, Title, PhotosBlock } from "~/components";
import styles from "./main.module.css";

export function Main() {
  const [spinnerActive, setSpinnerActive] = useState<boolean>(false);

  return (
    <main className={styles.main}>
      <Title title='Descend into Madness' />
      <PhotosBlock spinnerActive={spinnerActive} />
      <ActionButton setSpinnerActive={setSpinnerActive} />
    </main>
  );
}

export default Main;
