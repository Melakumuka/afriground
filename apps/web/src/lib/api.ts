import { createHmac } from "node:crypto";

export type { MissionControlLive } from "@/components/MissionControlPreview";

/**
 * Server-side AfriGround API client (Phase 4.2).
 *
 * The web app has no user session; it calls the tenant-scoped FastAPI surface
 * as a platform service identity: a short-lived HS256 JWT is minted for the
 * provisioned demo user (AFRIGROUND_SERVICE_SUB) exactly like a Supabase
 * token (audience "authenticated"), signed with SUPABASE_JWT_SECRET.
 *
 * Every call fails soft: an unreachable API or missing configuration returns
 * null and the caller falls back to its existing mock/simulated data, so the
 * landing experience is preserved without the backend.
 */

const API_BASE = process.env.AFRIGROUND_API_URL ?? "http://localhost:8000";
const JWT_SECRET = process.env.SUPABASE_JWT_SECRET ?? "";
const SERVICE_SUB = process.env.AFRIGROUND_SERVICE_SUB ?? "";
const SERVICE_ORG = process.env.AFRIGROUND_SERVICE_ORG ?? "";

function b64url(obj: unknown): string {
  return Buffer.from(JSON.stringify(obj)).toString("base64url");
}

function serviceToken(): string | null {
  if (!JWT_SECRET || !SERVICE_SUB) return null;
  const now = Math.floor(Date.now() / 1000);
  const header = b64url({ alg: "HS256", typ: "JWT" });
  const payload = b64url({ sub: SERVICE_SUB, aud: "authenticated", iat: now, exp: now + 300 });
  const signature = createHmac("sha256", JWT_SECRET)
    .update(`${header}.${payload}`)
    .digest("base64url");
  return `${header}.${payload}.${signature}`;
}

async function api<T>(path: string, init?: RequestInit): Promise<T | null> {
  const token = serviceToken();
  if (!token) return null;
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        ...(init?.headers ?? {}),
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

async function apiGet<T>(path: string): Promise<T | null> {
  return api<T>(path);
}

async function apiPost<T>(path: string, body: unknown): Promise<T | null> {
  return api<T>(path, { method: "POST", body: JSON.stringify(body) });
}

export const serviceOrgId = (): string | null => (SERVICE_ORG ? SERVICE_ORG : null);

// ── API surface types (mirrors apps/api response models) ───────────────────

export type Mission = {
  id: string;
  org_id: string;
  spacecraft_id: string;
  name: string;
  mission_type: string;
  status: string;
  start_date: string | null;
  end_date: string | null;
};

export type Station = {
  id: string;
  name: string;
  code: string;
  country: string;
  latitude: number;
  longitude: number;
  altitude_m: number;
  status: string;
  certification_state: string;
  tx_enabled: boolean;
};

export type TimeStatus = {
  id: string;
  station_id: string;
  sync_status: string;
  offset_ms: number | null;
  last_sync_at: string | null;
  clock_source: string | null;
  reported_at: string;
};

export type Agent = {
  id: string;
  station_id: string;
  agent_id: string;
  agent_version: string | null;
  certificate_serial: string | null;
  certificate_valid_until: string | null;
  last_heartbeat_at: string | null;
  revoked_at: string | null;
  status: string;
  created_at: string;
};

export type OrchestrationMetrics = {
  outbox: {
    total: number;
    by_status: { PENDING: number; PUBLISHED: number; FAILED: number };
    oldest_pending_age_s: number | null;
    total_attempts: number;
    retry_due: number;
    backpressure: number;
  };
  jobs_by_status: Record<string, number>;
  generated_at: string;
};

export type SlaViolation = {
  id: string;
  mission_id: string;
  observation_job_id: string;
  sla_type: string;
  target_value: number;
  actual_value: number;
  unit: string | null;
  status: string;
  violated_at: string;
};

export type NetworkRanking = {
  station_id: string;
  station_name?: string;
  rank: number;
  score: number;
  [key: string]: unknown;
};

export type Dataset = {
  id: string;
  schedule_id: string | null;
  satellite_id: string | null;
  sensor_type: string | null;
  cloud_cover: number | null;
  processing_level: string | null;
  product_type: string | null;
  acquisition_date: string | null;
  storage_url: string | null;
};

export type SupportTicket = {
  id: string;
  org_id: string;
  category: string;
  priority: string;
  status: string;
  subject: string;
  description: string;
  created_at: string | null;
};

// ── Endpoint helpers (server-side only) ─────────────────────────────────────

export function fetchMissions(): Promise<Mission[] | null> {
  return apiGet<Mission[]>("/api/v1/missions");
}

export function fetchStations(): Promise<Station[] | null> {
  return apiGet<Station[]>("/api/v1/stations");
}

export function fetchTimeStatus(stationId: string): Promise<TimeStatus[] | null> {
  return apiGet<TimeStatus[]>(`/api/v1/stations/${stationId}/time-status`);
}

export function fetchAgents(stationId: string): Promise<Agent[] | null> {
  return apiGet<Agent[]>(`/api/v1/stations/${stationId}/agents`);
}

export function fetchOrchestrationMetrics(): Promise<OrchestrationMetrics | null> {
  return apiGet<OrchestrationMetrics>("/api/v1/orchestration/metrics");
}

export function fetchSlaViolations(limit = 8): Promise<SlaViolation[] | null> {
  return apiGet<SlaViolation[]>(`/api/v1/business/sla-violations?limit=${limit}`);
}

export function fetchNetworkRanking(): Promise<NetworkRanking[] | null> {
  return apiGet<NetworkRanking[]>("/api/v1/network/ranking");
}

export function fetchDatasets(): Promise<Dataset[] | null> {
  return apiGet<Dataset[]>("/api/v1/data/datasets");
}

export function createSupportTicket(body: {
  org_id: string;
  category: string;
  priority: string;
  subject: string;
  description: string;
}): Promise<SupportTicket | null> {
  return apiPost<SupportTicket>("/api/v1/support/tickets", body);
}