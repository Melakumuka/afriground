"use client";

import * as THREE from "three";
import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { satelliteWorldPosition } from "./useOrbitalMotion";

export default function Satellite() {
  const group = useRef<THREE.Group>(null);
  const tmp = useMemo(() => new THREE.Vector3(), []);
  const zenith = useMemo(() => new THREE.Vector3(0, 0, 0), []);

  useFrame((state) => {
    const g = group.current;
    if (!g) return;
    satelliteWorldPosition(state.clock.elapsedTime, tmp);
    g.position.copy(tmp);
    g.lookAt(zenith);
  });

  return (
    <group ref={group}>
      <group scale={2.4}>
        {/* Bus */}
        <mesh position={[0, 0, -0.05]}>
          <boxGeometry args={[0.4, 0.32, 0.6]} />
          <meshStandardMaterial color="#9AA2AC" roughness={0.35} metalness={0.75} />
        </mesh>
        {/* Solar panels */}
        <mesh position={[-0.58, 0, 0.08]}>
          <boxGeometry args={[0.75, 0.02, 0.34]} />
          <meshStandardMaterial color="#24303B" roughness={0.5} metalness={0.3} />
        </mesh>
        <mesh position={[0.58, 0, 0.08]}>
          <boxGeometry args={[0.75, 0.02, 0.34]} />
          <meshStandardMaterial color="#24303B" roughness={0.5} metalness={0.3} />
        </mesh>
        {/* Downlink antenna (points toward Earth via +Z after lookAt) */}
        <mesh position={[0, 0, 0.42]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.09, 0.09, 0.07, 24]} />
          <meshStandardMaterial color="#C9CED6" roughness={0.3} metalness={0.8} />
        </mesh>
        <mesh position={[0, 0, 0.44]}>
          <sphereGeometry args={[0.1, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
          <meshStandardMaterial color="#DDE3EA" roughness={0.25} metalness={0.6} />
        </mesh>
        {/* Signal indicator */}
        <mesh position={[0.22, 0.14, -0.25]}>
          <sphereGeometry args={[0.035, 12, 12]} />
          <meshStandardMaterial color="#E2662F" emissive="#E2662F" emissiveIntensity={2.4} />
        </mesh>
      </group>
    </group>
  );
}