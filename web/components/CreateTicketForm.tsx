"use client";

import { FormEvent, useRef, useState } from "react";
import { readToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Client form that posts a new ticket using the stored bearer token. */
export function CreateTicketForm() {
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  // Stable across retries of the same submit; cleared after success.
  const idempotencyKeyRef = useRef<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const token = readToken();
    if (!token) {
      setMessage("Sign in first.");
      return;
    }
    if (!idempotencyKeyRef.current) {
      idempotencyKeyRef.current =
        typeof crypto !== "undefined" && crypto.randomUUID
          ? crypto.randomUUID()
          : `ft-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    }
    const idempotencyKey = idempotencyKeyRef.current;

    const res = await fetch(`${API_URL}/tickets/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        "Idempotency-Key": idempotencyKey,
      },
      body: JSON.stringify({ title, description: "", priority: "medium" }),
    });
    setMessage(res.ok ? "Created." : "Failed.");
    if (res.ok) {
      idempotencyKeyRef.current = null;
      setTitle("");
    }
  }

  return (
    <form onSubmit={onSubmit} style={{ marginTop: "1.5rem", display: "grid", gap: 8, maxWidth: 400 }}>
      <h2>New ticket</h2>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Title"
        required
      />
      <button type="submit">Create</button>
      {message && <p>{message}</p>}
    </form>
  );
}
