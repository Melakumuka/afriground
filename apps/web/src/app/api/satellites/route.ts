import { NextRequest, NextResponse } from "next/server";
import { findSatellites } from "@/lib/celestrak";

export async function GET(request: NextRequest) {
  const q = request.nextUrl.searchParams.get("q")?.trim() ?? "";
  if (q.length < 2) {
    return NextResponse.json({ list: [] });
  }
  try {
    const { list, source } = await findSatellites(q, 14);
    return NextResponse.json({
      source,
      list: list.map((s) => ({ norad: s.norad, name: s.name, epochUtc: s.epochUtc })),
    });
  } catch {
    return NextResponse.json({ error: "GP feed unavailable" }, { status: 503 });
  }
}