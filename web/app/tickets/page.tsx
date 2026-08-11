import { cookies } from "next/headers";
import Link from "next/link";
import { listTickets } from "@/lib/api";
import { CreateTicketForm } from "@/components/CreateTicketForm";

/**
 * Tickets index — Server Component.
 * Prefers httpOnly cookie when present (correct path for SSR).
 */
export default async function TicketsPage() {
  const jar = cookies();
  const token = jar.get("ft_session")?.value;

  if (!token) {
    return (
      <section>
        <h1>Tickets</h1>
        <p>
          No session cookie. <Link href="/login">Sign in</Link> from the client
          flow, or set the <code>ft_session</code> cookie for SSR.
        </p>
        <CreateTicketForm />
      </section>
    );
  }

  const tickets = await listTickets(token);

  return (
    <section>
      <h1>Your tickets</h1>
      <ul>
        {tickets.map((t) => (
          <li key={t.id}>
            <Link href={`/tickets/${t.id}`}>{t.title}</Link>
            <span style={{ color: "#666" }}> — {t.status}</span>
          </li>
        ))}
      </ul>
      <CreateTicketForm />
    </section>
  );
}
