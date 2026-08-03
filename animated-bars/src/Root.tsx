import "./index.css";
import { Composition } from "remotion";
import { AnimatedBars } from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AnimatedBars"
        component={AnimatedBars}
        durationInFrames={120}
        fps={30}
        width={1280}
        height={720}
      />
    </>
  );
};
