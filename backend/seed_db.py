from database import SessionLocal
import models
import schemas
import crud
from datetime import datetime, timedelta

def seed_db():
    db = SessionLocal()
    try:
        deals = [
            {"title": "크리넥스 3겹 데코앤소프트 30m 30롤 2팩", "price": 28900, "mall": "11번가", "source": "fmkorea", "url": "https://example.com/1"},
            {"title": "제로콜라 355ml 24캔", "price": 14500, "mall": "G마켓", "source": "fmkorea", "url": "https://example.com/2"},
            {"title": "맥도날드 빅맥 세트 기프티콘", "price": 4500, "mall": "위메프", "source": "algumon", "url": "https://example.com/3"},
            {"title": "삼성전자 비스포크 제트 청소기", "price": 450000, "mall": "네이버쇼핑", "source": "algumon", "url": "https://example.com/4"},
            {"title": "하기스 네이처메이드 밤부 3단계 3팩", "price": 42000, "mall": "쿠팡", "source": "momibebe", "url": "https://example.com/5"},
            {"title": "크리넥스 3겹 30m 30롤", "price": 29500, "mall": "쿠팡", "source": "fmkorea", "url": "https://example.com/6"},
            {"title": "제로콜라 355ml 24캔 (가격오름)", "price": 15500, "mall": "G마켓", "source": "algumon", "url": "https://example.com/7"},
            {"title": "제로콜라 250ml 30캔", "price": 13000, "mall": "11번가", "source": "momibebe", "url": "https://example.com/8"},
        ]
        
        # Insert deals with different dates for price history test
        base_date = datetime.utcnow()
        for i, d in enumerate(deals):
            deal_data = schemas.DealCreate(**d)
            db_deal = crud.create_deal(db, deal_data)
            # manually change the created_at to simulate history
            db_deal.created_at = base_date - timedelta(days=i)
            db.commit()
            
        print(f"Inserted {len(deals)} dummy deals.")
    except Exception as e:
        print(e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
