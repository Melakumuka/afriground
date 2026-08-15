"use client";

import * as THREE from "three";
import { useMemo } from "react";
import { createEarthTexture } from "./earthTexture";

export default function Earth() {
  const texture = useMemo(() => createEarthTexture(), []);
  return (
    <mesh>
      <sphereGeometry args={[2.2, 96, 96]} />
      <meshStandardMaterial
        map={texture}
        roughness={0.92}
        metalness={0.08}
        emissive={new THREE.Color("#101015")}
        emissiveIntensity={0.6}
      />
    </mesh>
  );
}
