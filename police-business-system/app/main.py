import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import assignments, attachments, auth, awards, changelog, handover, nodes, regulations
from app.services.scheduler import start_scheduler, stop_scheduler

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get("DISABLE_SCHEDULER") != "1":
        start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="業務管理系統", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(nodes.router)
app.include_router(assignments.router)
app.include_router(handover.router)
app.include_router(regulations.router)
app.include_router(attachments.router)
app.include_router(awards.router)
app.include_router(changelog.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
