"use client";

import * as THREE from "three";
import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Line } from "@react-three/drei";
import { DEFAULT_ORBIT, buildOrbitPath, orbitPosition } from "./useOrbitalMotion";

const SEGMENTS = 180;

type TrailLineRef = {
  geometry: {
    setPositions(position: number[]): void;
    attributes: { position: { needsUpdate: boolean } };
  };
};

export default function OrbitPath() {
  const points = useMemo(() => {
    const arr: THREE.Vector3[] = [];
    buildOrbitPath(DEFAULT_ORBIT, SEGMENTS, arr);
    return arr;
  }, []);

  const trail = useMemo(() => {
    const arr: THREE.Vector3[] = [];
    const origin = new THREE.Vector3();
    orbitPosition(DEFAULT_ORBIT, 0, origin);
    arr.push(origin.clone(), origin.clone());
    return arr;
  }, []);
  const trailRef = useRef<THREE.Vector3[]>([]);
  const trailLineRef = useRef<TrailLineRef>(null);
  const tmp = useMemo(() => new THREE.Vector3(), []);

  useFrame((state) => {
    orbitPosition(DEFAULT_ORBIT, state.clock.elapsedTime, tmp);
    const trailPoints = trailRef.current;
    trailPoints.push(tmp.clone());
    if (trailPoints.length > 26) trailPoints.shift();

    const line = trailLineRef.current;
    if (line) {
      line.geometry.setPositions(trailPoints.flatMap((p) => [p.x, p.y, p.z]));
      line.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <group>
      <Line
        points={points}
        color="#7A828C"
        transparent
        opacity={0.35}
        lineWidth={0.5}
        dashed
        dashSize={1.1}
        gapSize={0.45}
        dashScale={0.9}
      />
      <Line
        ref={(el) => {
          trailLineRef.current = el as unknown as TrailLineRef;
        }}
        points={trail}
        color="#E2662F"
        transparent
        opacity={0.55}
        lineWidth={1.4}
      />
    </group>
  );
}