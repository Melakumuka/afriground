import * as THREE from "three";
import { EARTH_RADIUS, ORBIT_ALTITUDE } from "./geo";

export type OrbitConfig = {
  semiMajor: number;
  inclinationDeg: number;
  raanDeg: number;
  periodSec: number;
  phaseOffset: number;
};

/**
 * LEO-like visualization orbit. This is a visualisation, not a claim of a real
 * spacecraft orbit.
 */
export const DEFAULT_ORBIT: OrbitConfig = {
  semiMajor: EARTH_RADIUS * ORBIT_ALTITUDE,
  inclinationDeg: 51.6,
  raanDeg: -39,
  periodSec: 90,
  phaseOffset: 0
};

const DEG = Math.PI / 180;

export function orbitPosition(
  cfg: OrbitConfig,
  timeSec: number,
  target: THREE.Vector3
): THREE.Vector3 {
  const u = (timeSec / cfg.periodSec) * Math.PI * 2 + cfg.phaseOffset;
  const x = cfg.semiMajor * Math.cos(u);
  const z = cfg.semiMajor * Math.sin(u);
  const v = target ?? new THREE.Vector3();
  v.set(x, 0, z);
  v.applyAxisAngle(new THREE.Vector3(1, 0, 0), cfg.inclinationDeg * DEG);
  v.applyAxisAngle(new THREE.Vector3(0, 1, 0), cfg.raanDeg * DEG);
  return v;
}

/** World position of the visualization satellite at time `timeSec`. */
export function satelliteWorldPosition(
  timeSec: number,
  target: THREE.Vector3
): THREE.Vector3 {
  return orbitPosition(DEFAULT_ORBIT, timeSec, target);
}

/** Sample `segments` points of the orbit path into `array` of Vector3. */
export function buildOrbitPath(
  cfg: OrbitConfig,
  segments: number,
  array: THREE.Vector3[]
): THREE.Vector3[] {
  const tmp = new THREE.Vector3();
  for (let i = 0; i < segments; i++) {
    orbitPosition(cfg, (i / segments) * cfg.periodSec, tmp);
    array[i] = (array[i] ?? new THREE.Vector3()).copy(tmp);
  }
  return array;
}

/** Elevation of `p` above the local horizon at `groundPoint` (0 = horizon). */
export function elevationAt(point: THREE.Vector3, groundPoint: THREE.Vector3): number {
  const up = groundPoint.clone().normalize();
  const dir = point.clone().sub(groundPoint);
  const denom = dir.length();
  if (denom < 1e-5) return -90;
  const elev = Math.asin(THREE.MathUtils.clamp(dir.dot(up) / denom, -1, 1));
  return (elev * 180) / Math.PI;
}
