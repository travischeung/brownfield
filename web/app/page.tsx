import Link from "next/link";

/** Landing — Server Component, intentionally public. */
export default function HomePage() {
  return (
    <section>
      <h1>FieldTrack</h1>
      <p>Track work across your team.</p>
      <p>
        <Link href="/login">Sign in</Link>
        {" · "}
        <Link href="/tickets">Tickets</Link>
      </p>
    </section>
  );
}
