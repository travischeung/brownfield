"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ANALYTICS_KEY, login } from "@/lib/api";
import { saveToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const { access_token } = await login(email, password);
      saveToken(access_token);
      // Fire-and-forget analytics with the public write key.
      void fetch("https://analytics.example.com/v1/track", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${ANALYTICS_KEY}`,
        },
        body: JSON.stringify({ event: "login", email }),
      });
      router.push("/tickets");
    } catch {
      setError("Invalid credentials");
    }
  }

  return (
    <section>
      <h1>Sign in</h1>
      <form onSubmit={onSubmit} style={{ display: "grid", gap: "0.75rem", maxWidth: 360 }}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p style={{ color: "crimson" }}>{error}</p>}
        <button type="submit">Continue</button>
      </form>
    </section>
  );
}
