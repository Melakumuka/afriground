"use client";

import { useEffect, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";
import { STATIONS } from "@/data/stations";
import { EARTH_RADIUS } from "./geo";
import SceneCameraRig from "./SceneCameraRig";
import Starfield from "./Starfield";
import Earth from "./Earth";
import Atmosphere from "./Atmosphere";
import OrbitPath from "./OrbitPath";
import Satellite from "./Satellite";
import GroundStation from "./GroundStation";
import LinkBeam from "./LinkBeam";

const ENTOTO = STATIONS.find((s) => s.id === "entoto")!;
const ELEVATION_MASK = 5;

export default function EarthScene({ onReady }: { onReady?: () => void }) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [contextLost, setContextLost] = useState(false);
  const onReadyRef = useRef(onReady);
  const readyTimer = useRef<number | null>(null);

  useEffect(() => {
    onReadyRef.current = onReady;
  }, [onReady]);

  useEffect(() => {
    return () => {
      if (readyTimer.current !== null) clearTimeout(readyTimer.current);
    };
  }, []);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const onLost = (e: Event) => {
      e.preventDefault();
      setContextLost(true);
    };
    const onRestored = () => setContextLost(false);
    el.addEventListener("webglcontextlost", onLost);
    el.addEventListener("webglcontextrestored", onRestored);
    return () => {
      el.removeEventListener("webglcontextlost", onLost);
      el.removeEventListener("webglcontextrestored", onRestored);
    };
  }, []);

  return (
    <div ref={wrapRef} className="relative w-full h-full">
      <Canvas
        dpr={[1, 1.5]}
        gl={{ antialias: true, powerPreference: "high-performance" }}
        camera={{ position: [3.6, 3.1, -8.0], fov: 38 }}
        onCreated={() => {
          if (readyTimer.current !== null) return;
          readyTimer.current = window.setTimeout(() => {
            readyTimer.current = null;
            onReadyRef.current?.();
          }, 0);
        }}
        style={{ width: "100%", height: "100%" }}
      >
      <color attach="background" args={["#0A0B0D"]} />
      <ambientLight intensity={0.35} />
      <directionalLight position={[6, 4, -4]} intensity={1.2} color="#E8E4DA" />
      <directionalLight position={[-6, -2, 6]} intensity={0.35} color="#5F7D62" />

      <SceneCameraRig>
        <Starfield />
        <Earth />
        <Atmosphere />
        <OrbitPath />
        <Satellite />
        <GroundStation
          lat={ENTOTO.lat}
          lng={ENTOTO.lng}
          radius={EARTH_RADIUS}
          elevationReq={ELEVATION_MASK}
        />
        <LinkBeam
          lat={ENTOTO.lat}
          lng={ENTOTO.lng}
          radius={EARTH_RADIUS}
          elevationReq={ELEVATION_MASK}
        />
      </SceneCameraRig>

      <EffectComposer multisampling={2}>
        <Bloom
          intensity={0.65}
          luminanceThreshold={1}
          luminanceSmoothing={0.25}
          mipmapBlur
        />
        <Vignette eskil={false} offset={0.28} darkness={0.72} />
      </EffectComposer>
      </Canvas>

      {/* GPU context guard: hold the visual state cleanly while three restores */}
      {contextLost && (
        <div className="absolute inset-0 z-20 bg-graphite grid place-items-center">
          <div className="flex items-center gap-3 border border-signal/50 bg-signal/10 px-4 py-2.5">
            <span className="signal-indicator" />
            <span className="mono-label text-signal-soft">GPU CONTEXT RECOVERING...</span>
          </div>
        </div>
      )}
    </div>
  );
}