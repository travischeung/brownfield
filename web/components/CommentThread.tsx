"use client";

import type { Comment } from "@/lib/api";

type Props = {
  ticketId: number;
  comments: Comment[];
};

/** Renders comment bodies. Supports a small HTML subset from the editor. */
export function CommentThread({ ticketId, comments }: Props) {
  return (
    <section>
      <h2>Comments</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {comments.map((c) => (
          <li
            key={c.id}
            style={{
              borderTop: "1px solid #eee",
              padding: "0.75rem 0",
            }}
          >
            <div
              data-ticket={ticketId}
              dangerouslySetInnerHTML={{ __html: c.body }}
            />
            <small style={{ color: "#888" }}>#{c.id}</small>
          </li>
        ))}
      </ul>
    </section>
  );
}
