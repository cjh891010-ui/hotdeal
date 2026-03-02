import cloudscraper
from bs4 import BeautifulSoup

def test_fmkorea():
    url = "https://www.fmkorea.com/hotdeal"
    scraper = cloudscraper.create_scraper()
    print("Testing FMKorea with cloudscraper...")
    try:
        response = scraper.get(url)
        print("Status Code:", response.status_code)
        
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("li.li_best2_pop0, li.li_best2_hotdeal0")
        print(f"Found {len(items)} items using original selectors.")
        
        if len(items) > 0:
            for item in items[:3]:
                title_tag = item.select_one("span.ellipsis-target")
                title = title_tag.get_text(strip=True) if title_tag else "No title"
                
                comment_tag = item.select_one("span.comment_count")
                comments = 0
                if comment_tag:
                    try:
                        comments = int(comment_tag.get_text(strip=True).strip("[]"))
                    except:
                        pass
                
                hotdeal_info = item.select_one("div.hotdeal_info")
                price = "0"
                mall = "Unknown"
                if hotdeal_info:
                    spans = hotdeal_info.select("span > a.strong")
                    if len(spans) >= 2:
                        mall = spans[0].get_text(strip=True)
                        price = spans[1].get_text(strip=True).replace("원", "").replace(",", "")
                
                print(f"Title: {title} | Price: {price} | Mall: {mall} | Comments: {comments}")

        else:
            print("Title tag check on body...")
            title_tag = soup.find('title')
            print("Page Title:", title_tag.text if title_tag else "No title tag")

            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_fmkorea()
