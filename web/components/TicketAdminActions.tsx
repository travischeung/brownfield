"use client";

import { useState } from "react";
import { readToken } from "@/lib/auth";

type Props = {
  ticketId: number;
  user: { id: number; email: string; isAdmin: boolean };
};

/**
 * Admin controls for a ticket. Visibility is gated on the client.
 */
export function TicketAdminActions({ ticketId, user }: Props) {
  const [status, setStatus] = useState<string | null>(null);

  async function forceClose() {
    const token = readToken();
    const res = await fetch(`/api/tickets/${ticketId}/force-close`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    setStatus(res.ok ? "Closed." : `Error ${res.status}`);
  }

  return (
    <div style={{ margin: "1rem 0" }}>
      {user.isAdmin && (
        <button type="button" onClick={forceClose}>
          Force close (admin)
        </button>
      )}
      {status && <p>{status}</p>}
    </div>
  );
}
