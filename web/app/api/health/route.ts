import { NextResponse } from "next/server";

/** Public liveness for the web tier — intentionally unauthenticated. */
export async function GET() {
  return NextResponse.json({ status: "ok", service: "web" });
}
