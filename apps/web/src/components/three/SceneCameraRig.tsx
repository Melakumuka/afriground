"use client";

import * as THREE from "three";
import { useCallback, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";

export default function SceneCameraRig({ children }: { children: React.ReactNode }) {
  const group = useRef<THREE.Group>(null);
  const { pointer } = useThree();
  const state = useRef({ tx: 0, ty: 0, drift: 0, breath: 0 });

  const prefersReducedMotion = useCallback(() => {
    return typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }, []);

  useFrame((root, delta) => {
    const g = group.current;
    if (!g) return;
    const f = state.current;
    const reduced = prefersReducedMotion();

    f.tx += (pointer.x * 0.055 - f.tx) * 0.045;
    f.ty += (pointer.y * 0.04 - f.ty) * 0.045;
    if (!reduced) f.drift += delta * 0.055;

    g.rotation.y = f.drift + f.tx;
    g.rotation.x = f.ty * 0.6;
    g.rotation.z = f.tx * 0.22;

    // Ken Burns: slow breathing zoom on the whole viewport
    if (!reduced) {
      f.breath += delta * 0.12;
      root.camera.position.z = -8 * (1 + 0.018 * Math.sin(f.breath));
    }
  });

  return <group ref={group}>{children}</group>;
}