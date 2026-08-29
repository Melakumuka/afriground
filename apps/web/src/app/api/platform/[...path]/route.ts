import { NextRequest, NextResponse } from "next/server";
import {
  createSupportTicket,
  fetchAgents,
  fetchDatasets,
  fetchDatasetDownload,
  fetchMissions,
  fetchNetworkRanking,
  fetchOrchestrationMetrics,
  fetchSlaViolations,
  fetchStations,
  fetchTimeStatus,
  serviceOrgId,
} from "@/lib/api";

const UUID_RE = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}";
const STATION_CHILD_RE = new RegExp(`^stations/(${UUID_RE})/(time-status|agents)$`);
const MISSION_CHILD_RE = new RegExp(`^missions/(${UUID_RE})/profiles$`);
const DATASET_DOWNLOAD_RE = new RegExp(`^data/datasets/(${UUID_RE})/download$`);

export const dynamic = "force-dynamic";

type Path = string[];

// Returns a Promise for the data, or undefined if the path is not recognised.
// Deliberately NOT async so the returned Promise is NOT auto-awaited —
// the caller awaits it separately so it can distinguish "unknown path"
// (undefined) from "backend unreachable" (Promise resolves to null).
const CONTACT_JOB_RE = new RegExp(`^contact/jobs/(${UUID_RE})$`);

function resolvePath(path: Path): Promise<unknown> | undefined {
  const key = path.join("/");
  switch (key) {
    case "missions":
      return fetchMissions();
    case "stations":
      return fetchStations();
    case "orchestration/metrics":
      return fetchOrchestrationMetrics();
    case "business/sla-violations":
      return fetchSlaViolations(8);
    case "network/ranking":
      return fetchNetworkRanking();
    case "data/datasets":
      return fetchDatasets();
    default: {
      const match = key.match(STATION_CHILD_RE);
      if (match) return match[2] === "time-status" ? fetchTimeStatus(match[1]) : fetchAgents(match[1]);
      
      const missionMatch = key.match(MISSION_CHILD_RE);
      if (missionMatch) {
        return import("@/lib/api").then((m) => m.fetchMissionProfiles(missionMatch[1]));
      }
      
      const downloadMatch = key.match(DATASET_DOWNLOAD_RE);
      if (downloadMatch) {
        return fetchDatasetDownload(downloadMatch[1]);
      }
      
      if (key === "commercial/contracts") {
        return import("@/lib/api").then((m) => m.fetchContracts());
      }
      
      const contractUsageMatch = key.match(/^commercial\/contracts\/([0-9a-f\-]{36})\/usage$/);
      if (contractUsageMatch) {
        return import("@/lib/api").then((m) => m.fetchContractUsage(contractUsageMatch[1]));
      }

      if (key === "business/sla-violations") {
        return import("@/lib/api").then((m) => m.fetchSlaViolations());
      }
      
      if (key === "contact/jobs") {
        return import("@/lib/api").then((m) => m.fetchJobs());
      }

      const jobMatch = key.match(CONTACT_JOB_RE);
      if (jobMatch) {
        return import("@/lib/api").then((m) => m.fetchJobDetails(jobMatch[1]));
      }

      return undefined; // path not exposed
    }
  }
}

export async function GET(_req: NextRequest, { params }: { params: Promise<{ path: Path }> }) {
  const { path } = await params;
  const call = resolvePath(path);
  if (call === undefined) return NextResponse.json({ ok: false, error: "Path not exposed" }, { status: 404 });
  const data = await call;
  if (data === null) return NextResponse.json({ ok: false, error: "Backend unavailable" }, { status: 503 });
  return NextResponse.json({ ok: true, data });
}

export async function POST(req: NextRequest, { params }: { params: Promise<{ path: Path }> }) {
  const { path } = await params;
  const pathStr = path.join("/");
  const body = await req.json();

  if (pathStr === "support/tickets") {
    const orgId = serviceOrgId();
    if (!orgId) return NextResponse.json({ ok: false }, { status: 503 });
    const ticket = await createSupportTicket({ org_id: orgId, ...body });
    if (!ticket) return NextResponse.json({ ok: false }, { status: 503 });
    return NextResponse.json({ ok: true, data: ticket });
  }

  // Phase 6 Contact Planning Routes
  if (pathStr === "contact/visibility") {
    const { generateVisibility } = await import("@/lib/api");
    const data = await generateVisibility(body);
    if (!data) return NextResponse.json({ ok: false }, { status: 503 });
    return NextResponse.json({ ok: true, data });
  }

  if (pathStr === "contact/opportunities") {
    const { createContactOpportunities } = await import("@/lib/api");
    const data = await createContactOpportunities(body);
    if (!data) return NextResponse.json({ ok: false }, { status: 503 });
    return NextResponse.json({ ok: true, data });
  }

  if (pathStr === "contact/reservations") {
    const { createReservation } = await import("@/lib/api");
    const data = await createReservation(body);
    if (!data) return NextResponse.json({ ok: false }, { status: 503 });
    return NextResponse.json({ ok: true, data });
  }

  return NextResponse.json({ ok: false, error: "Path not exposed" }, { status: 404 });
}