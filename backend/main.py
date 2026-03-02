from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schemas
import crud
from contextlib import asynccontextmanager
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
import scraper

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the scheduler when app starts
    scheduler.add_job(scraper.run_all_scrapers, 'interval', minutes=10)
    scheduler.start()
    # Run once immediately
    scheduler.add_job(scraper.run_all_scrapers)
    yield
    # Shutdown the scheduler when app stops
    scheduler.shutdown()

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="DealFlow API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to DealFlow API"}

@app.post("/alerts/", response_model=schemas.DealAlert)
def create_alert(alert: schemas.DealAlertCreate, db: Session = Depends(get_db)):
    return crud.create_alert(db, alert)

@app.get("/deals/", response_model=list[schemas.Deal])
def read_deals(skip: int = 0, limit: int = 100, q: Optional[str] = None, sort: str = "latest", db: Session = Depends(get_db)):
    deals = crud.get_deals(db, skip=skip, limit=limit, query=q, sort_by=sort)
    return deals

@app.get("/deals/price-history/")
def read_price_history(q: str, db: Session = Depends(get_db)):
    if not q:
        return []
    history = crud.get_price_history(db, keyword=q)
    return history
