"""Ticket tracker API entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers import auth, comments, tickets, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FieldTrack", version="0.5.0")

# initial thoughts: this presents a security danger with allow_origins=[*] 
# and also allow_credentials=true combined w it basically allows every
# browser to send req back here to the endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(comments.router)
app.include_router(users.router)


@app.get("/health")
def health():
    """Liveness probe — public by design."""
    return {"status": "ok"}
