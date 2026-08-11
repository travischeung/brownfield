import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import { getComments, getTicket } from "@/lib/api";
import { CommentThread } from "@/components/CommentThread";
import { TicketAdminActions } from "@/components/TicketAdminActions";

type Props = { params: { id: string } };

/** Ticket detail — Server Component composing client islands. */
export default async function TicketDetailPage({ params }: Props) {
  const token = cookies().get("ft_session")?.value;
  if (!token) {
    return <p>Sign in required.</p>;
  }

  const id = Number(params.id);
  if (Number.isNaN(id)) notFound();

  const [ticket, comments] = await Promise.all([
    getTicket(token, id),
    getComments(token, id),
  ]);

  // Derive a coarse role flag for the admin chrome.
  const user = {
    id: ticket.owner_id,
    email: "you@example.com",
    isAdmin: false,
  };

  return (
    <article>
      <h1>{ticket.title}</h1>
      <p>{ticket.description}</p>
      <p>
        Status: {ticket.status} · Priority: {ticket.priority} · v{ticket.version}
      </p>
      <TicketAdminActions ticketId={ticket.id} user={user} />
      <CommentThread ticketId={ticket.id} comments={comments} />
    </article>
  );
}
