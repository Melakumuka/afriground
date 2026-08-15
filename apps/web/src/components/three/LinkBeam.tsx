"use client";

import * as THREE from "three";
import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Line } from "@react-three/drei";
import { latLngToVector3 } from "./geo";
import { satelliteWorldPosition } from "./useOrbitalMotion";

type Props = {
  lat: number;
  lng: number;
  radius: number;
  elevationReq: number;
};

const PACKET_COUNT = 5;

type BeamLineRef = {
  geometry: { setPositions(position: number[]): void };
  material: { opacity: number; dashOffset: number };
};

export default function LinkBeam({ lat, lng, radius, elevationReq = 5 }: Props) {
  const lineRef = useRef<BeamLineRef>(null);
  const stationPos = useMemo(() => latLngToVector3(lat, lng, radius + 0.02), [lat, lng, radius]);
  const normal = useMemo(() => stationPos.clone().normalize(), [stationPos]);
  const satPos = useMemo(() => new THREE.Vector3(), []);
  const beamPoints = useMemo(() => [stationPos.clone(), satPos.clone()], [stationPos, satPos]);
  const packetRefs = useRef<THREE.Mesh[]>([]);
  const fade = useRef(0);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    satelliteWorldPosition(t, satPos);

    // Visibility: fade link in/out between elevation mask and mask + 12°
    const dir = satPos.clone().sub(stationPos);
    const d = dir.length() || 1;
    const elev = (Math.asin(THREE.MathUtils.clamp(dir.dot(normal) / d, -1, 1)) * 180) / Math.PI;
    const target = THREE.MathUtils.smoothstep(elev, elevationReq, elevationReq + 12);
    fade.current += (target - fade.current) * 0.06;

    // Dashed signal line
    beamPoints[0].copy(stationPos);
    beamPoints[1].copy(satPos);
    if (lineRef.current) {
      lineRef.current.geometry.setPositions(
        beamPoints.flatMap((p) => [p.x, p.y, p.z])
      );
      lineRef.current.material.opacity = 0.85 * fade.current;
      lineRef.current.material.dashOffset = -t * 4.5;
    }

    // Downlink packets travel satellite → ground
    for (let i = 0; i < PACKET_COUNT; i++) {
      const m = packetRefs.current[i];
      if (!m) continue;
      const progress = (t * 0.55 + i / PACKET_COUNT) % 1;
      m.position.lerpVectors(satPos, stationPos, progress);
      m.visible = fade.current > 0.02;
      const s = 0.028 + 0.02 * Math.sin(progress * Math.PI * 2);
      m.scale.setScalar(s);
      (m.material as THREE.MeshStandardMaterial).opacity = fade.current;
    }
  });

  return (
    <group>
      <Line
        ref={(el) => {
          lineRef.current = el as unknown as BeamLineRef;
        }}
        points={beamPoints}
        color="#E2662F"
        transparent
        opacity={0}
        lineWidth={1.6}
        dashed
        dashSize={0.5}
        gapSize={0.18}
        dashScale={0.55}
      />
      {Array.from({ length: PACKET_COUNT }).map((_, i) => (
        <mesh
          key={i}
          ref={(el) => {
            if (el) packetRefs.current[i] = el;
          }}
          visible={false}
        >
          <sphereGeometry args={[0.03, 10, 10]} />
          <meshStandardMaterial
            color="#E2662F"
            emissive="#E2662F"
            emissiveIntensity={3}
            transparent
            opacity={0}
          />
        </mesh>
      ))}
    </group>
  );
}