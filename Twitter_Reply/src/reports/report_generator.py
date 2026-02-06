from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from src.ai.summarizer import Summarizer
from src.database.models import Report, SessionLocal, Tweet


class ReportGenerator:
    def __init__(self) -> None:
        self.summarizer = Summarizer()
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)

    def weekly_report(self) -> Report | None:
        now = datetime.utcnow()
        start = now - timedelta(days=7)

        with SessionLocal() as session:
            tweets = session.query(Tweet).filter(Tweet.imported_at >= start, Tweet.imported_at <= now).all()
            if not tweets:
                return None

            summary = self.summarizer.summarize(tweets)
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            pdf_path = self.output_dir / f"weekly_report_{timestamp}.pdf"
            csv_path = self.output_dir / f"weekly_report_{timestamp}.csv"

            self._build_pdf(pdf_path, summary, tweets)
            self._build_csv(csv_path, tweets)

            report = Report(
                report_type="weekly",
                file_path=str(pdf_path),
                csv_path=str(csv_path),
                insights_json=summary,
                period_start=start,
                period_end=now,
            )
            session.add(report)
            session.commit()
            session.refresh(report)
            return report

    def _build_pdf(self, path: Path, summary: dict, tweets: list[Tweet]) -> None:
        c = canvas.Canvas(str(path), pagesize=letter)
        y = 760
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Weekly Crypto Twitter AI Agent Report")
        y -= 28
        c.setFont("Helvetica", 10)

        for line in [
            f"Executive Summary: {summary.get('executive_summary', '')}",
            f"Sentiment: {summary.get('sentiment', 'n/a')}",
            f"Trends: {', '.join(summary.get('trends', []))}",
            f"Risks: {', '.join(summary.get('risks', []))}",
            f"Tweets analyzed: {len(tweets)}",
        ]:
            c.drawString(40, y, line[:110])
            y -= 18
        c.save()

    def _build_csv(self, path: Path, tweets: list[Tweet]) -> None:
        df = pd.DataFrame(
            [
                {
                    "tweet_id": t.tweet_id,
                    "author_handle": t.author_handle,
                    "text": t.text,
                    "like_count": t.like_count,
                    "retweet_count": t.retweet_count,
                    "reply_count": t.reply_count,
                    "relevance_score": t.relevance_score,
                    "status": t.lifecycle_status,
                }
                for t in tweets
            ]
        )
        df.to_csv(path, index=False)
