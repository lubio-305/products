"""把敘獎紀錄的補齊從「查詢當下才算」改成「排程主動補齊」，查詢時仍會呼叫
同一個 ensure_records_up_to_today 當保底，所以就算排程還沒跑過也不會看到舊資料，
只是正常情況下查詢時大部分期數都已經排程建好，不用每次現算。"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.models import AwardCycle
from app.services.award_status import ensure_records_up_to_today

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="Asia/Taipei")


def backfill_all_award_records() -> int:
    db = SessionLocal()
    created_count = 0
    try:
        cycles = db.query(AwardCycle).filter(AwardCycle.active.is_(True)).all()
        for cycle in cycles:
            created_count += len(ensure_records_up_to_today(db, cycle))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("敘獎紀錄排程補齊失敗")
        raise
    finally:
        db.close()
    return created_count


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        backfill_all_award_records,
        trigger="cron",
        hour=0,
        minute=30,
        id="backfill_award_records",
        replace_existing=True,
    )
    scheduler.start()
    backfill_all_award_records()  # 啟動時先跑一次，避免剛部署完資料是空的


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
