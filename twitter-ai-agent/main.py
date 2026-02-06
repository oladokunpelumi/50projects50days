from __future__ import annotations

import json

import click
from rich.console import Console
from rich.table import Table

from config.settings import settings
from src.ai.evaluation_agent import EvaluationAgent
from src.ai.reply_generator import ReplyGenerator
from src.cli.approval_queue import process_reply, show_queue
from src.collectors.twitter_client import TwitterClient
from src.database.models import GeneratedReply, SessionLocal, Tweet, init_db
from src.filters.keyword_filter import evaluate_relevance
from src.reports.report_generator import ReportGenerator

console = Console()


@click.group()
def cli() -> None:
    """Twitter/X AI Agent CLI."""


@cli.command("init")
def init_cmd() -> None:
    init_db()
    console.print("[green]Database initialized.[/green]")


@cli.command("collect")
@click.option("--list-id", default="", help="X list ID for collection")
@click.option("--count", default=10, type=int)
def collect_cmd(list_id: str, count: int) -> None:
    client = TwitterClient()
    tweets = client.collect_from_list(list_id=list_id or "sim", max_results=count)
    saved = 0
    with SessionLocal() as session:
        for t in tweets:
            existing = session.query(Tweet).filter(Tweet.tweet_id == t["tweet_id"]).first()
            if existing:
                continue
            filt = evaluate_relevance(t["text"], settings.default_keywords, settings.default_hashtags)
            tweet = Tweet(
                tweet_id=t["tweet_id"],
                text=t["text"],
                author_handle=t["author_handle"],
                source=t["source"],
                like_count=t["like_count"],
                retweet_count=t["retweet_count"],
                reply_count=t["reply_count"],
                relevance_score=filt.relevance_score,
                lifecycle_status="filtered_in" if filt.matched else "filtered_out",
            )
            session.add(tweet)
            saved += 1
        session.commit()
    console.print(f"[green]Collected {saved} tweets.[/green]")


@cli.command("import-tweet")
@click.argument("url_or_id")
def import_tweet_cmd(url_or_id: str) -> None:
    client = TwitterClient()
    t = client.import_by_url_or_id(url_or_id)
    filt = evaluate_relevance(t["text"], settings.default_keywords, settings.default_hashtags)
    with SessionLocal() as session:
        existing = session.query(Tweet).filter(Tweet.tweet_id == t["tweet_id"]).first()
        if existing:
            console.print(f"[yellow]Tweet {t['tweet_id']} already exists.[/yellow]")
            return
        tweet = Tweet(
            tweet_id=t["tweet_id"],
            text=t["text"],
            author_handle=t["author_handle"],
            source=t["source"],
            like_count=t["like_count"],
            retweet_count=t["retweet_count"],
            reply_count=t["reply_count"],
            relevance_score=filt.relevance_score,
            lifecycle_status="filtered_in" if filt.matched else "filtered_out",
        )
        session.add(tweet)
        session.commit()
    console.print(f"[green]Imported tweet {t['tweet_id']}[/green]")


@cli.command("generate")
@click.option("--persona", default=None, help="Override persona key")
def generate_cmd(persona: str | None) -> None:
    generator = ReplyGenerator()
    count = 0
    with SessionLocal() as session:
        tweets = (
            session.query(Tweet)
            .filter(Tweet.lifecycle_status == "filtered_in")
            .order_by(Tweet.imported_at.desc())
            .all()
        )
        for tweet in tweets:
            existing = session.query(GeneratedReply).filter(GeneratedReply.tweet_id == tweet.id).first()
            if existing:
                continue
            generator.generate_reply(tweet=tweet, persona_override=persona)
            count += 1
    console.print(f"[green]Generated {count} replies.[/green]")


@cli.command("queue")
@click.option("--action", type=click.Choice(["show", "approve", "reject", "edit", "regenerate"]), default="show")
@click.option("--reply-id", type=int, default=0)
@click.option("--text", default=None)
@click.option("--persona", default=None)
def queue_cmd(action: str, reply_id: int, text: str | None, persona: str | None) -> None:
    if action == "show":
        show_queue()
        return
    if reply_id <= 0:
        raise click.ClickException("--reply-id is required for queue actions")
    process_reply(reply_id=reply_id, action=action, edited_text=text, regenerate_persona=persona)
    console.print("[green]Queue action complete.[/green]")


@cli.command("evaluate")
def evaluate_cmd() -> None:
    agent = EvaluationAgent()
    eval_count = 0
    with SessionLocal() as session:
        replies = session.query(GeneratedReply).filter(GeneratedReply.status.in_(["generated", "edited", "approved"]))
        for reply in replies:
            if reply.evaluation:
                continue
            agent.evaluate_reply(reply)
            eval_count += 1
    console.print(f"[green]Evaluated {eval_count} replies.[/green]")


@cli.command("report")
def report_cmd() -> None:
    report = ReportGenerator().weekly_report()
    if not report:
        console.print("[yellow]No data available for report.[/yellow]")
        return

    table = Table(title="Report Generated")
    table.add_column("PDF")
    table.add_column("CSV")
    table.add_column("Insights")
    table.add_row(report.file_path, report.csv_path, json.dumps(report.insights_json)[:120])
    console.print(table)


@cli.command("demo")
def demo_cmd() -> None:
    init_db()
    runner = click.get_current_context().invoke
    runner(collect_cmd, list_id="sim", count=8)
    runner(generate_cmd, persona=None)
    runner(evaluate_cmd)
    runner(report_cmd)
    runner(queue_cmd, action="show", reply_id=0, text=None, persona=None)


if __name__ == "__main__":
    cli()
