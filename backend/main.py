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
    # Start background scheduler for periodic scraping (every 10 minutes)
    scheduler.add_job(scraper.run_all_scrapers, 'interval', minutes=10)
    scheduler.start()
    
    print("Backend started successfully with background scheduler enabled.")
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
    if q:
        # User searched for a keyword. Dynamically scrape historical data first.
        try:
            scraper.search_fmkorea(db, q, limit=30)
            scraper.search_algumon(db, q, limit=30)
            # MomiBebe search is disabled for MVP to prevent Selenium dependency issues on Render
        except Exception as e:
            print(f"Error during dynamic search scraping for '{q}': {e}")
            
    deals = crud.get_deals(db, skip=skip, limit=limit, query=q, sort_by=sort)
    return deals

@app.get("/deals/price-history/")
def read_price_history(q: str, db: Session = Depends(get_db)):
    if not q:
        return []
    history = crud.get_price_history(db, keyword=q)
    return history

@app.get("/api/scrape")
def manual_scrape():
    """Manually trigger the web scrapers to fetch new hot deals."""
    try:
        scraper.run_all_scrapers()
        return {"status": "success", "message": "Manual scrape completed successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
