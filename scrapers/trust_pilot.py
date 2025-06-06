import requests
from bs4 import BeautifulSoup


def get_trust_score(url: str):
    resp = requests.get(f"https://www.trustpilot.com/review/{url}")
    print(resp.status_code)

    if resp.status_code == 404:
        print("not here")
        return -1
    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        score = soup.find('p', attrs={'data-rating-typography': 'true'}).text.strip()
        return int(score) 
    except:
        return -1

