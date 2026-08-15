import * as THREE from "three";

export const EARTH_RADIUS = 2.2;
export const ORBIT_ALTITUDE = 1.28;

export function latLngToVector3(
  lat: number,
  lng: number,
  radius: number,
  target?: THREE.Vector3
): THREE.Vector3 {
  const phi = ((90 - lat) * Math.PI) / 180;
  const theta = ((lng + 180) * Math.PI) / 180;
  const v = target ?? new THREE.Vector3();
  v.set(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
  return v;
}

export function yawForLng(lng: number): number {
  return (-lng * Math.PI) / 180;
}
