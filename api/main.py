from fastapi import FastAPI
from . import rules
from .diagnose import router as diagnose_router

app = FastAPI(title="GC-AI API")
app.include_router(rules.router)
app.include_router(diagnose_router)
