"use client";

import { Component, useState, type ReactNode } from "react";
import dynamic from "next/dynamic";
import Image from "next/image";

const EarthScene = dynamic(
  () => import("@/components/three/EarthScene"),
  { ssr: false }
);

class SceneBoundary extends Component<
  { fallback: ReactNode; children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (this.state.failed) return this.props.fallback;
    return this.props.children;
  }
}

const STATIC_FALLBACK = (
  <div className="relative w-full h-full">
    <Image
      src="/hero_ground_station.jpg"
      alt="AfriGround ground station dish array"
      fill
      priority
      className="object-cover opacity-25"
    />
    <div className="absolute inset-0 bg-gradient-to-b from-graphite/60 via-graphite/30 to-graphite" />
  </div>
);

export default function CinematicBackground() {
  const [sceneReady, setSceneReady] = useState(false);

  return (
    <div
      className="fixed inset-0 z-0 pointer-events-none bg-graphite"
      aria-hidden="true"
    >
      {/* 3D orbital scene */}
      <div
        className={`absolute inset-0 transition-opacity duration-1000 ${
          sceneReady ? "opacity-100" : "opacity-0"
        }`}
      >
        <SceneBoundary fallback={STATIC_FALLBACK}>
          <EarthScene onReady={() => setSceneReady(true)} />
        </SceneBoundary>
      </div>

      {/* Keep fallback visible until the scene is ready */}
      {!sceneReady && <div className="absolute inset-0">{STATIC_FALLBACK}</div>}

      {/* Readability film: fades content panels into the scene */}
      <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-graphite/60 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-72 bg-gradient-to-t from-graphite/80 to-transparent" />
    </div>
  );
}