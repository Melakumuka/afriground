export type TleRecord = {
  norad: string;
  name: string;
  line1: string;
  line2: string;
  epochUtc: string;
};

export type CatalogSource = "live" | "offline";

import { FALLBACK_TLES } from "@/data/fallbackTles";

const ACTIVE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=TLE";
const CACHE_TTL_MS = 6 * 60 * 60 * 1000;

let activeCache: { fetchedAt: number; sats: TleRecord[] } | null = null;
const singleCache = new Map<string, { fetchedAt: number; tle: TleRecord }>();
const SINGLE_TTL_MS = 3 * 60 * 60 * 1000;

function epochToUtc(epochField: string): string {
  const yy = Number(epochField.slice(0, 2));
  const year = yy < 57 ? 2000 + yy : 1900 + yy;
  const dayOfYear = Number(epochField.slice(2));
  const date = new Date(Date.UTC(year, 0, 1) + (dayOfYear - 1) * 86400000);
  return date.toISOString().replace("T", " ").slice(0, 19) + " UTC";
}

export function parseTleSet(text: string): TleRecord[] {
  const lines = text.split(/\r?\n/).map((l) => l.trimEnd());
  const out: TleRecord[] = [];
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (/^1 \d{5}/.test(l) && lines[i + 1]?.startsWith("2 ")) {
      const norad = l.slice(2, 7).trim();
      const nameLine = i > 0 && !/^[12] /.test(lines[i - 1]) ? lines[i - 1].trim() : "";
      const cleaned = nameLine.startsWith("0 ") ? nameLine.slice(2).trim() : nameLine;
      out.push({
        norad,
        name: cleaned || `NORAD ${norad}`,
        line1: l,
        line2: lines[i + 1],
        epochUtc: epochToUtc(l.slice(18, 32)),
      });
      i++;
    }
  }
  return out;
}

async function fetchTleText(url: string): Promise<string> {
  const res = await fetch(url, {
    signal: AbortSignal.timeout(20000),
    headers: { "User-Agent": "AfriGround-GSaaS/0.1 (ops@afriground.space)" },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`CelesTrak ${res.status}: ${res.statusText}`);
  }
  return res.text();
}

export async function getActiveSatellites(): Promise<{
  sats: TleRecord[];
  source: CatalogSource;
}> {
  if (activeCache && Date.now() - activeCache.fetchedAt < CACHE_TTL_MS) {
    return { sats: activeCache.sats, source: "live" };
  }
  try {
    const text = await fetchTleText(ACTIVE_URL);
    const sats = parseTleSet(text);
    if (sats.length === 0) {
      throw new Error("Empty GP dataset from CelesTrak");
    }
    activeCache = { fetchedAt: Date.now(), sats };
    return { sats, source: "live" };
  } catch {
    return { sats: FALLBACK_TLES, source: "offline" };
  }
}

export async function findSatellites(q: string, limit = 14): Promise<{
  list: TleRecord[];
  source: CatalogSource;
}> {
  const ql = q.trim().toLowerCase();
  if (ql.length < 2) return { list: [], source: "live" };
  const { sats, source } = await getActiveSatellites();
  const matches = sats.filter((s) => {
    if (/^\d{1,9}$/.test(ql)) {
      return s.norad.startsWith(ql) || s.name.toLowerCase().includes(ql);
    }
    return s.name.toLowerCase().includes(ql);
  });
  return { list: matches.slice(0, limit), source };
}

export async function getTleByNorad(norad: string): Promise<{
  tle: TleRecord;
  source: CatalogSource;
}> {
  const qn = norad.trim();

  const tryLive = async (): Promise<TleRecord | null> => {
    const text = await fetchTleText(
      `https://celestrak.org/NORAD/elements/gp.php?CATNR=${encodeURIComponent(qn)}&FORMAT=TLE`
    );
    const parsed = parseTleSet(text);
    if (parsed.length === 0) return null;
    singleCache.set(qn, { fetchedAt: Date.now(), tle: parsed[0] });
    return parsed[0];
  };

  if (activeCache) {
    const hit = activeCache.sats.find((s) => s.norad === qn);
    if (hit) return { tle: hit, source: "live" };
  }
  const cached = singleCache.get(qn);
  if (cached && Date.now() - cached.fetchedAt < SINGLE_TTL_MS) {
    return { tle: cached.tle, source: "live" };
  }

  try {
    const live = await tryLive();
    if (live) return { tle: live, source: "live" };
  } catch {
    // fall through to the offline catalog
  }

  const offline = FALLBACK_TLES.find((s) => s.norad === qn);
  if (offline) return { tle: offline, source: "offline" };
  throw new Error(`NORAD ${qn} not found in GP catalog`);
}