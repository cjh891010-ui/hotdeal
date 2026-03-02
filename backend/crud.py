from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas

def get_deal(db: Session, deal_id: int):
    return db.query(models.Deal).filter(models.Deal.id == deal_id).first()

def get_deal_by_url(db: Session, url: str):
    return db.query(models.Deal).filter(models.Deal.url == url).first()

def get_deals(db: Session, skip: int = 0, limit: int = 100, query: str = None, sort_by: str = "latest"):
    q = db.query(models.Deal)
    if query:
        q = q.filter(models.Deal.title.ilike(f"%{query}%"))
    
    if sort_by == "price":
        q = q.order_by(models.Deal.price.asc())
    else:
        q = q.order_by(models.Deal.created_at.desc())
        
    return q.offset(skip).limit(limit).all()

def create_deal(db: Session, deal: schemas.DealCreate):
    db_deal = models.Deal(**deal.model_dump())
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal

def get_price_history(db: Session, keyword: str):
    results = (
        db.query(
            func.date(models.Deal.created_at).label("date"),
            func.avg(models.Deal.price).label("avg_price"),
            func.min(models.Deal.price).label("min_price")
        )
        .filter(models.Deal.title.ilike(f"%{keyword}%"))
        .filter(models.Deal.price > 0)
        .group_by(func.date(models.Deal.created_at))
        .order_by(func.date(models.Deal.created_at).asc())
        .all()
    )
    
    return [
        {"date": r.date, "avg_price": round(r.avg_price, 2), "min_price": r.min_price}
        for r in results
    ]

def create_alert(db: Session, alert: schemas.DealAlertCreate):
    db_alert = models.DealAlert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_active_alerts(db: Session):
    return db.query(models.DealAlert).filter(models.DealAlert.is_active == True).all()
