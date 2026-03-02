import requests
from bs4 import BeautifulSoup
import scraper

def main():
    url = "https://www.algumon.com/"
    try:
        response = requests.get(url, headers=scraper.get_headers())
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("li.post-li")
        print("Found items:", len(items))
        
        for item in items[:3]:
            title_tag = item.select_one("a.product-link")
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            
            price_tag = item.select_one("small.product-price")
            price = price_tag.get_text(strip=True) if price_tag else "No price"
            
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
            
            print(f"Title: {title} | Price: {price} | Mall: {mall} | Likes: {likes} | Comments: {comments}")
            
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
