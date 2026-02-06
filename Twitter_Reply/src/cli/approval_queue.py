from __future__ import annotations

from rich.console import Console
from rich.table import Table

from src.ai.reply_generator import ReplyGenerator
from src.database.models import GeneratedReply, SessionLocal


console = Console()


def show_queue() -> None:
    with SessionLocal() as session:
        rows = (
            session.query(GeneratedReply)
            .filter(GeneratedReply.status.in_(["generated", "edited"]))
            .order_by(GeneratedReply.created_at.asc())
            .all()
        )

        table = Table(title="Approval Queue")
        table.add_column("Reply ID")
        table.add_column("Persona")
        table.add_column("Status")
        table.add_column("Reply")

        for row in rows:
            table.add_row(str(row.id), row.persona, row.status, row.reply_text)

        console.print(table)


def process_reply(
    reply_id: int,
    action: str,
    edited_text: str | None = None,
    regenerate_persona: str | None = None,
) -> None:
    with SessionLocal() as session:
        reply = session.get(GeneratedReply, reply_id)
        if not reply:
            raise ValueError(f"Reply {reply_id} not found")

        if action == "approve":
            reply.status = "approved"
        elif action == "reject":
            reply.status = "rejected"
        elif action == "edit":
            if not edited_text:
                raise ValueError("edited_text is required for edit action")
            reply.reply_text = edited_text[:280]
            reply.status = "edited"
        elif action == "regenerate":
            tweet = reply.tweet
            session.expunge(reply)
            generator = ReplyGenerator()
            new_reply = generator.generate_reply(tweet=tweet, persona_override=regenerate_persona)
            console.print(f"Regenerated as reply {new_reply.id}")
            return
        else:
            raise ValueError(f"Unknown action: {action}")

        session.add(reply)
        session.commit()
