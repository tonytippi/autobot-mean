import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/signals.db")

# SQLite needs check_same_thread=False for multithreading; safe here in single-thread app
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), nullable=False)
    interval = Column(String(16), nullable=False)
    side = Column(String(8), nullable=False)
    close = Column(Float, nullable=False)
    rsi = Column(Float, nullable=False)
    sma20 = Column(Float, nullable=False)
    thr = Column(Float, nullable=False)
    atr14 = Column(Float, nullable=False)
    suggested_tp = Column(Float, nullable=False)
    suggested_sl = Column(Float, nullable=False)
    bar_open_time = Column(DateTime(timezone=True), nullable=False)
    bar_close_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

def init_db():
    Base.metadata.create_all(engine)

def save_signal(**kwargs):
    with SessionLocal() as s:
        sig = Signal(**kwargs)
        s.add(sig)
        s.commit()
        s.refresh(sig)
        return sig

def latest_signals(limit=100):
    with SessionLocal() as s:
        rows = s.execute(text("SELECT * FROM signals ORDER BY id DESC LIMIT :lim"), {"lim": limit}).mappings().all()
        return [dict(r) for r in rows]
