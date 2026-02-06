from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from config.settings import settings


class Base(DeclarativeBase):
    pass


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tweet_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    author_handle: Mapped[str] = mapped_column(String(128), default="unknown")
    source: Mapped[str] = mapped_column(String(32), default="simulation")
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    retweet_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    lifecycle_status: Mapped[str] = mapped_column(String(32), default="collected")

    replies: Mapped[list[GeneratedReply]] = relationship(back_populates="tweet")


class GeneratedReply(Base):
    __tablename__ = "generated_replies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), index=True)
    persona: Mapped[str] = mapped_column(String(64))
    reply_text: Mapped[str] = mapped_column(String(280))
    status: Mapped[str] = mapped_column(String(32), default="generated")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tweet: Mapped[Tweet] = relationship(back_populates="replies")
    evaluation: Mapped[EvaluationResult | None] = relationship(back_populates="reply", uselist=False)


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reply_id: Mapped[int] = mapped_column(ForeignKey("generated_replies.id"), unique=True)
    relevance_score: Mapped[float] = mapped_column(Float)
    tone_accuracy_score: Mapped[float] = mapped_column(Float)
    value_add_score: Mapped[float] = mapped_column(Float)
    engagement_potential_score: Mapped[float] = mapped_column(Float)
    predicted_likes: Mapped[int] = mapped_column(Integer)
    predicted_retweets: Mapped[int] = mapped_column(Integer)
    predicted_replies: Mapped[int] = mapped_column(Integer)
    raw_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reply: Mapped[GeneratedReply] = relationship(back_populates="evaluation")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_type: Mapped[str] = mapped_column(String(64), default="weekly")
    file_path: Mapped[str] = mapped_column(String(255))
    csv_path: Mapped[str] = mapped_column(String(255))
    insights_json: Mapped[dict] = mapped_column(JSON)
    period_start: Mapped[datetime] = mapped_column(DateTime)
    period_end: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)
