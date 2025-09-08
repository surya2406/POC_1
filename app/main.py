import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.db.session import get_engine,Base
from fastapi.staticfiles import StaticFiles
from app.core.logging import app_logger
from app.core.settings import get_settings
from app.models.models import * 

settings=get_settings()

scheduler_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan management."""
    global scheduler_task
    
    try:
        engine = get_engine()
        print("Engine: ", engine)
        # Synchronous SQLAlchemy engine usage
        with engine.begin() as conn:
            Base.metadata.create_all(bind=conn)
        print("Tables created successfully")
    except Exception as e:
        app_logger.info(f"Error during startup: {e}")
    
    yield
    
    try:
        engine = get_engine()
        # Dispose sync engine
        engine.dispose()
    except Exception as e:
        app_logger.info(f"Error during shutdown: {e}")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



print("Settings loaded:", get_settings().model_dump())

# Routers
from app.api.v1.endpoints import seo_agent
app.include_router(seo_agent.router)

# Serve static frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")



