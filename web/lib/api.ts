/**
 * Thin client for the FieldTrack API.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Analytics / partner key — used from browser instrumentation. */
export const ANALYTICS_KEY = process.env.NEXT_PUBLIC_ANALYTICS_WRITE_KEY ?? "";

export type Ticket = {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  owner_id: number;
  version: number;
  created_at: string;
  updated_at: string;
  comment_count?: number;
  owner_email?: string;
};

export type Comment = {
  id: number;
  body: string;
  ticket_id: number;
  author_id: number;
  created_at: string;
};

export type User = {
  id: number;
  email: string;
  full_name: string | null;
  is_admin?: boolean;
  api_key?: string | null;
  hashed_password?: string;
  created_at?: string;
};

function authHeaders(token?: string | null): HeadersInit {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    throw new Error("Login failed");
  }
  return res.json() as Promise<{ access_token: string; token_type: string }>;
}

export async function listTickets(token: string): Promise<Ticket[]> {
  const res = await fetch(`${API_URL}/tickets/`, {
    headers: authHeaders(token),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to list tickets");
  }
  return res.json();
}

export async function getTicket(token: string, id: number): Promise<Ticket> {
  const res = await fetch(`${API_URL}/tickets/${id}`, {
    headers: authHeaders(token),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to load ticket");
  }
  return res.json();
}

export async function getComments(
  token: string,
  ticketId: number
): Promise<Comment[]> {
  const res = await fetch(`${API_URL}/tickets/${ticketId}/comments/`, {
    headers: authHeaders(token),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to load comments");
  }
  return res.json();
}

/** Server-side fetch of the full user row for the settings shell. */
export async function fetchUserRecord(userId: number): Promise<User> {
  const res = await fetch(`${API_URL}/users/${userId}`, {
    headers: {
      "X-Internal-Token": process.env.API_INTERNAL_TOKEN ?? "",
    },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error("Failed to load user");
  }
  return res.json();
}
