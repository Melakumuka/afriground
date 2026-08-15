import { NextRequest, NextResponse } from "next/server";
import {
  twoline2satrec,
  propagate,
  gstime,
  type EciVec3,
  type Kilometer,
} from "satellite.js";
import { getTleByNorad } from "@/lib/celestrak";
import { STATIONS } from "@/data/stations";

export type PassInfo = {
  aosIso: string;
  losIso: string;
  durationMin: number;
  maxElevationDeg: number;
  aosAzimuthDeg: number;
};

const A = 6378.137; // WGS84 semi-major axis (km)
const F = 1 / 298.257223563;
const E2 = F * (2 - F);
const STEP_SEC = 10;

function geodeticToEcf(latDeg: number, lngDeg: number, altKm: number): [number, number, number] {
  const lat = (latDeg * Math.PI) / 180;
  const lng = (lngDeg * Math.PI) / 180;
  const sinLat = Math.sin(lat);
  const cosLat = Math.cos(lat);
  const n = A / Math.sqrt(1 - E2 * sinLat * sinLat);
  return [
    (n + altKm) * cosLat * Math.cos(lng),
    (n + altKm) * cosLat * Math.sin(lng),
    (n * (1 - E2) + altKm) * sinLat,
  ];
}

function eciToEcf(pos: EciVec3<Kilometer>, gmst: number): [number, number, number] {
  const c = Math.cos(gmst);
  const s = Math.sin(gmst);
  return [c * pos.x + s * pos.y, -s * pos.x + c * pos.y, pos.z];
}

function computePasses(
  line1: string,
  line2: string,
  latDeg: number,
  lngDeg: number,
  elevMaskDeg: number,
  days: number
): PassInfo[] {
  const satrec = twoline2satrec(line1, line2);

  const [ox, oy, oz] = geodeticToEcf(latDeg, lngDeg, 0);
  const [ux, uy, uz] = geodeticToEcf(latDeg, lngDeg, 1);
  const up: [number, number, number] = [ux - ox, uy - oy, uz - oz];
  const upLen = Math.hypot(up[0], up[1], up[2]) || 1;

  const lat = (latDeg * Math.PI) / 180;
  const lng = (lngDeg * Math.PI) / 180;
  const north: [number, number, number] = [
    -Math.sin(lat) * Math.cos(lng),
    -Math.sin(lat) * Math.sin(lng),
    Math.cos(lat),
  ];
  const east: [number, number, number] = [-Math.sin(lng), Math.cos(lng), 0];

  const total = Math.round((days * 86400) / STEP_SEC);
  const start = Date.now();

  const passes: PassInfo[] = [];
  let current: { aos: number; maxEl: number; maxAz: number } | null = null;
  let lastAbove: number | null = null;

  for (let i = 0; i < total; i++) {
    const t = new Date(start + i * STEP_SEC * 1000);
    const pv = propagate(satrec, t);
    if (!pv || !pv.position) continue;

    const gmst = gstime(t);
    const [sx, sy, sz] = eciToEcf(pv.position, gmst);
    const rho = [sx - ox, sy - oy, sz - oz];
    const rhoLen = Math.hypot(rho[0], rho[1], rho[2]) || 1;

    const elev = (Math.asin((rho[0] * up[0] + rho[1] * up[1] + rho[2] * up[2]) / (rhoLen * upLen)) * 180) / Math.PI;
    const azRaw = (Math.atan2(
      rho[0] * east[0] + rho[1] * east[1] + rho[2] * east[2],
      rho[0] * north[0] + rho[1] * north[1] + rho[2] * north[2]
    ) * 180) / Math.PI;
    const az = (azRaw + 360) % 360;

    if (elev >= elevMaskDeg) {
      if (!current) {
        current = { aos: t.getTime(), maxEl: elev, maxAz: az };
      } else if (elev > current.maxEl) {
        current.maxEl = elev;
        current.maxAz = az;
      }
      lastAbove = t.getTime();
    } else if (current && lastAbove) {
      const durationMin = (lastAbove - current.aos) / 60000;
      if (durationMin >= 1) {
        passes.push({
          aosIso: new Date(current.aos).toISOString(),
          losIso: new Date(lastAbove).toISOString(),
          durationMin: Math.round(durationMin * 10) / 10,
          maxElevationDeg: Math.round(current.maxEl * 10) / 10,
          aosAzimuthDeg: Math.round(current.maxAz * 10) / 10,
        });
      }
      current = null;
      lastAbove = null;
    }
  }

  return passes.slice(0, 15);
}

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const norad = params.get("norad")?.trim() ?? "";
  const stationId = params.get("stationId")?.trim() ?? "";
  const days = Math.min(Math.max(Number(params.get("days")) || 2, 1), 3);
  const elevation = Math.min(Math.max(Number(params.get("elevation")) || 5, 2), 15);

  if (!/^\d{1,9}$/.test(norad)) {
    return NextResponse.json({ error: "Invalid NORAD catalog number" }, { status: 400 });
  }
  const station = STATIONS.find((s) => s.id === stationId);
  if (!station) {
    return NextResponse.json({ error: "Unknown ground station" }, { status: 400 });
  }

  try {
    const { tle, source } = await getTleByNorad(norad);
    const passes = computePasses(tle.line1, tle.line2, station.lat, station.lng, elevation, days);
    return NextResponse.json({
      catalog: source,
      satellite: { norad: tle.norad, name: tle.name, epochUtc: tle.epochUtc },
      station: { id: station.id, name: station.name, lat: station.lat, lng: station.lng },
      mask: elevation,
      passes,
    });
  } catch {
    return NextResponse.json({ error: "NORAD object not in active GP catalog" }, { status: 404 });
  }
}