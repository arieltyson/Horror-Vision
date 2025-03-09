import {Title} from "~/title/title";
import {useState} from "react";

export function Main() {
  const madnessState = useState(true);

  return (
    <main>
      <Title title={ madnessState ? 'Descend into Madness' : 'Maintain Sanity' } />
    </main>
  );
}
