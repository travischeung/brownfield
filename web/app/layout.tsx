import type { ReactNode } from "react";

export const metadata = {
  title: "FieldTrack",
  description: "Linear-like ticket tracker",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "Georgia, serif", margin: 0 }}>
        <header
          style={{
            padding: "1rem 1.5rem",
            borderBottom: "1px solid #ddd",
          }}
        >
          <strong>FieldTrack</strong>
        </header>
        <main style={{ padding: "1.5rem" }}>{children}</main>
      </body>
    </html>
  );
}
