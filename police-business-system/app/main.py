from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import assignments, attachments, auth, awards, changelog, handover, nodes, regulations

Base.metadata.create_all(bind=engine)

app = FastAPI(title="業務管理系統")

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
