import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_holidays(date_str=datetime.now().strftime("%d.%m")):
    """Возвращает список праздников для России с rusevents.ru на указанную дату."""
    url = f"https://rusevents.ru/date/{date_str}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при получении праздников: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    holidays = []

    posts = soup.select("div.post.clearfix")
    for post in posts:
        title_tag = post.select_one("span[itemprop='summary']")
        if title_tag:
            holidays.append(title_tag.get_text(strip=True))

    return holidays

if __name__ == "__main__":
    today = datetime.now()
    holidays_today = get_holidays("01.09")
    
    if holidays_today:
        print("Сегодня праздники:")
        for h in holidays_today:
            print("-", h)
    else:
        print("Праздников не найдено")
