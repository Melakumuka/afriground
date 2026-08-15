"use client";

import { Stars } from "@react-three/drei";

export default function Starfield() {
  return (
    <group>
      <Stars
        radius={48}
        depth={26}
        count={1300}
        factor={2.1}
        saturation={0}
        fade
        speed={0.4}
      />
    </group>
  );
}
