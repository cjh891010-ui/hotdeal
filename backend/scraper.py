import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
import schemas
import crud
import models
from database import SessionLocal

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.fmkorea.com/",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }

import cloudscraper

def scrape_fmkorea(db: Session, limit=20):
    url = "https://www.fmkorea.com/hotdeal"
    try:
        scraper_client = cloudscraper.create_scraper()
        response = scraper_client.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        items = soup.select("li.li_best2_pop0, li.li_best2_hotdeal0")
        for item in items[:limit]:
            title_tag = item.select_one("span.ellipsis-target")
            raw_title = title_tag.get_text(strip=True) if title_tag else "No title"
            
            link_tag = item.select_one("h3.title > a")
            link = "https://www.fmkorea.com" + link_tag["href"] if link_tag else url
            
            comment_tag = item.select_one("span.comment_count")
            comments = 0
            if comment_tag:
                try:
                    comments = int(comment_tag.get_text(strip=True).strip("[]"))
                except:
                    pass
            
            hotdeal_info = item.select_one("div.hotdeal_info")
            price = 0.0
            mall = "Unknown"
            if hotdeal_info:
                spans = hotdeal_info.select("span > a.strong")
                if len(spans) >= 2:
                    mall = spans[0].get_text(strip=True)
                    try:
                        price_str = spans[1].get_text(strip=True).replace("원", "").replace(",", "")
                        price = float(price_str)
                    except:
                        pass
            
            # Check if deal already exists
            existing_deal = crud.get_deal_by_url(db, link)
            if not existing_deal:
                deal_data = schemas.DealCreate(
                    title=raw_title,
                    price=price,
                    url=link,
                    source="fmkorea",
                    mall=mall,
                    likes=0,
                    comments=comments
                )
                crud.create_deal(db, deal_data)
                
    except Exception as e:
        print(f"Error scraping FMKorea: {e}")

def scrape_algumon(db: Session, limit=20):
    url = "https://www.algumon.com/"
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        items = soup.select("li.post-li")
        for item in items[:limit]:
            title_tag = item.select_one("a.product-link")
            if not title_tag:
                continue
            
            raw_title = title_tag.get_text(strip=True)
            link = "https://www.algumon.com" + title_tag["href"] if title_tag["href"].startswith("/") else title_tag["href"]
            
            price_tag = item.select_one("small.product-price")
            price = 0.0
            if price_tag:
                try:
                    price_str = price_tag.get_text(strip=True).replace("원", "").replace(",", "").strip()
                    price = float(price_str)
                except ValueError:
                    pass
            
            shop_tag = item.select_one("span.label.shop a")
            mall = shop_tag.get_text(strip=True) if shop_tag else "Unknown"
            
            # Likes
            likes_tag = item.select_one("p.deal-meta-info i.icon-thumbs-up")
            likes = 0
            if likes_tag and likes_tag.parent:
                likes_text = likes_tag.parent.get_text(strip=True)
                try:
                    likes = int(likes_text)
                except:
                    pass
            
            # Comments
            comment_btn = item.select_one("button.btn-comment")
            comments = 0
            if comment_btn and "data-comment-count" in comment_btn.attrs:
                try:
                    comments = int(comment_btn["data-comment-count"])
                except:
                    pass
            
            # Check if deal already exists
            existing_deal = crud.get_deal_by_url(db, link)
            if not existing_deal:
                deal_data = schemas.DealCreate(
                    title=raw_title,
                    price=price,
                    url=link,
                    source="algumon",
                    mall=mall,
                    likes=likes,
                    comments=comments
                )
                crud.create_deal(db, deal_data)
                
    except Exception as e:
        print(f"Error scraping Algumon: {e}")

def search_fmkorea(db: Session, keyword: str, limit=20):
    url = f"https://www.fmkorea.com/search.php?mid=hotdeal&search_keyword={keyword}&search_target=title_content"
    try:
        scraper_client = cloudscraper.create_scraper()
        response = scraper_client.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        items = soup.select("div.webzine > ul > li")
        if not items: # Fallback to normal hotdeal list items if search view is different
            items = soup.select("li.li_best2_pop0, li.li_best2_hotdeal0")
            
        for item in items[:limit]:
            title_tag = item.select_one("a.title") or item.select_one("h3.title > a")
            if not title_tag:
                continue
            raw_title = title_tag.get_text(strip=True)
            
            link = "https://www.fmkorea.com" + title_tag["href"] if title_tag["href"].startswith("/") else "https://www.fmkorea.com/" + title_tag["href"]
            
            # Price/mall info is harder to extract from FMKorea generic search view
            # Using defaults for historical records unless visible
            price = 0.0
            mall = "Unknown"
            
            hotdeal_info = item.select_one("div.hotdeal_info") or item.select_one("span.list_sys")
            if hotdeal_info:
                spans = hotdeal_info.select("span > a.strong") or hotdeal_info.select("span.title")
                if len(spans) >= 2:
                    mall = spans[0].get_text(strip=True)
                    try:
                        price_str = spans[1].get_text(strip=True).replace("원", "").replace(",", "")
                        price = float(price_str)
                    except:
                        pass
                        
            existing_deal = crud.get_deal_by_url(db, link)
            if not existing_deal:
                deal_data = schemas.DealCreate(
                    title=raw_title,
                    price=price,
                    url=link,
                    source="fmkorea",
                    mall=mall,
                    likes=0,
                    comments=0
                )
                crud.create_deal(db, deal_data)
                
    except Exception as e:
        print(f"Error searching FMKorea for '{keyword}': {e}")

def search_algumon(db: Session, keyword: str, limit=20):
    url = f"https://www.algumon.com/search?q={keyword}"
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        items = soup.select("li.post-li")
        for item in items[:limit]:
            title_tag = item.select_one("a.product-link")
            if not title_tag:
                continue
            
            raw_title = title_tag.get_text(strip=True)
            link = "https://www.algumon.com" + title_tag["href"] if title_tag["href"].startswith("/") else title_tag["href"]
            
            price_tag = item.select_one("small.product-price")
            price = 0.0
            if price_tag:
                try:
                    price_str = price_tag.get_text(strip=True).replace("원", "").replace(",", "").strip()
                    price = float(price_str)
                except ValueError:
                    pass
            
            shop_tag = item.select_one("span.label.shop a")
            mall = shop_tag.get_text(strip=True) if shop_tag else "Unknown"
            
            existing_deal = crud.get_deal_by_url(db, link)
            if not existing_deal:
                deal_data = schemas.DealCreate(
                    title=raw_title,
                    price=price,
                    url=link,
                    source="algumon",
                    mall=mall,
                    likes=0,
                    comments=0
                )
                crud.create_deal(db, deal_data)
                
    except Exception as e:
        print(f"Error searching Algumon for '{keyword}': {e}")

def scrape_momibebe(db: Session, limit=20):
    # Momibebe is a Naver Cafe (cafe.naver.com/imsanbu), which heavily uses iframes and requires Selenium.
    # Selenium requires a full Chrome installation, which is not available on Render's free tier by default.
    # Disabling MomiBebe scraping for this environment to prevent server crashes.
    print("MomiBebe scraper is currently disabled on this environment to avoid Selenium dependencies.")
    pass

def check_alerts(db: Session, new_deals):
    if not new_deals:
        return
    active_alerts = crud.get_active_alerts(db)
    if not active_alerts:
        return
        
    for deal in new_deals:
        for alert in active_alerts:
            if alert.keyword.lower() in deal.title.lower():
                print(f"\n[ALERT MATCH] Keyword '{alert.keyword}' found in deal: '{deal.title}'")
                print(f" -> Sending mock email to {alert.email} with link: {deal.url}\n")


def run_all_scrapers():
    db = SessionLocal()
    try:
        print("Starting scrapers...")
        
        # Keep track of existing deals counts to find new ones
        initial_deals = db.query(models.Deal).count()
        
        scrape_fmkorea(db)
        scrape_algumon(db)
        scrape_momibebe(db)
        
        final_deals = db.query(models.Deal).order_by(models.Deal.id.desc()).all()
        new_deal_count = len(final_deals) - initial_deals
        if new_deal_count > 0:
            new_deals = final_deals[:new_deal_count]
            check_alerts(db, new_deals)
            
        print("Scrapers completed.")
    finally:
        db.close()
