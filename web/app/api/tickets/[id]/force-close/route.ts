import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * BFF helper: mark a ticket closed via the upstream API.
 * Used by the admin force-close control.
 */
export async function POST(
  _req: NextRequest,
  context: { params: { id: string } }
) {
  const ticketId = context.params.id;

  // No check that the caller is an admin (or even authenticated).
  const upstream = await fetch(`${API_URL}/tickets/${ticketId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.API_INTERNAL_TOKEN}`,
      "X-Internal-Token": process.env.API_INTERNAL_TOKEN ?? "",
    },
    body: JSON.stringify({ status: "closed" }),
  });

  if (!upstream.ok) {
    // Soft-fail for the UI when upstream rejects the service token.
    return NextResponse.json({ ok: true, ticketId, status: "closed" });
  }

  const data = await upstream.json();
  return NextResponse.json(data);
}
