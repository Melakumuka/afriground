"use client";

import * as THREE from "three";
import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { latLngToVector3 } from "./geo";
import { satelliteWorldPosition } from "./useOrbitalMotion";

type Props = {
  lat: number;
  lng: number;
  radius: number;
  elevationReq: number;
};

export default function GroundStation({ lat, lng, radius, elevationReq = 5 }: Props) {
  const rig = useRef<THREE.Group>(null);
  const led = useRef<THREE.MeshStandardMaterial>(null);
  const base = useMemo(() => latLngToVector3(lat, lng, radius + 0.008), [lat, lng, radius]);
  const normal = useMemo(() => base.clone().normalize(), [base]);

  const satPos = useMemo(() => new THREE.Vector3(), []);

  useFrame((state) => {
    const g = rig.current;
    if (!g) return;
    satelliteWorldPosition(state.clock.elapsedTime, satPos);
    g.lookAt(satPos);

    // Status LED: nominal when the satellite is above the elevation mask
    const up = normal;
    const dir = satPos.clone().sub(base);
    const elev = Math.asin(
      THREE.MathUtils.clamp(dir.dot(up) / (dir.length() || 1), -1, 1)
    );
    const active = (elev * 180) / Math.PI >= elevationReq;
    if (led.current) {
      led.current.color.set(active ? "#5C7D62" : "#E2662F");
    }
  });

  const dishProfile = useMemo(() => {
    const pts: THREE.Vector2[] = [new THREE.Vector2(0, 0)];
    const R = 0.42;
    const f = 0.34;
    const N = 28;
    for (let i = 1; i <= N; i++) {
      const r = (i / N) * R;
      pts.push(new THREE.Vector2(r, (r * r) / (4 * f)));
    }
    return pts;
  }, []);

  return (
    <group position={base} quaternion={new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal)}>
      {/* Pedestal */}
      <mesh position={[0, 0.06, 0]}>
        <cylinderGeometry args={[0.06, 0.09, 0.14, 20]} />
        <meshStandardMaterial color="#3A4048" roughness={0.55} metalness={0.5} />
      </mesh>
      {/* Platform */}
      <mesh position={[0, 0.012, 0]}>
        <cylinderGeometry args={[0.22, 0.28, 0.03, 24]} />
        <meshStandardMaterial color="#23272D" roughness={0.7} metalness={0.35} />
      </mesh>
      {/* Tracking rig */}
      <group ref={rig} position={[0, 0.13, 0]}>
        {/* Yoke/mast */}
        <mesh position={[0, 0.02, 0]}>
          <cylinderGeometry args={[0.028, 0.042, 0.1, 16]} />
          <meshStandardMaterial color="#4A515B" roughness={0.45} metalness={0.65} />
        </mesh>
        {/* Dish — paraboloid lathe, opening faces +Z (lookAt target) */}
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <latheGeometry args={[dishProfile, 36]} />
          <meshStandardMaterial
            color="#C6CBD3"
            roughness={0.28}
            metalness={0.8}
            side={THREE.DoubleSide}
          />
        </mesh>
        {/* Dish rim */}
        <mesh position={[0, 0, 0.028]} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.42, 0.014, 10, 48]} />
          <meshStandardMaterial color="#7C828C" roughness={0.4} metalness={0.75} />
        </mesh>
        {/* Feed support + feed */}
        <mesh position={[0, 0, 0.12]}>
          <cylinderGeometry args={[0.012, 0.012, 0.18, 12]} />
          <meshStandardMaterial color="#4A515B" roughness={0.45} metalness={0.6} />
        </mesh>
        <mesh position={[0, 0, 0.22]}>
          <sphereGeometry args={[0.03, 16, 12]} />
          <meshStandardMaterial color="#DDE3EA" roughness={0.3} metalness={0.6} />
        </mesh>
      </group>
      {/* Operational status LED */}
      <mesh position={[0.16, 0.05, 0]}>
        <boxGeometry args={[0.03, 0.03, 0.03]} />
        <meshStandardMaterial
          ref={led}
          color="#5C7D62"
          emissive="#5C7D62"
          emissiveIntensity={1.8}
        />
      </mesh>
    </group>
  );
}