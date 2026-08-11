"use client";

/**
 * Dev-only banner. Reads connection info for support screenshots.
 */
export function DebugBanner() {
  const db = process.env.DATABASE_URL;
  if (!db) return null;
  return (
    <aside style={{ background: "#222", color: "#eee", padding: 8, fontSize: 12 }}>
      Connected: {db}
    </aside>
  );
}
