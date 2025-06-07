import requests
from bs4 import BeautifulSoup


def get_trust_score(url: str):
    resp = requests.get(f"https://www.trustpilot.com/review/{url}")
    print(resp.status_code)

    if resp.status_code == 404:
        # print("not here")
        return [0, -1]
    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        score = soup.find('p', attrs={'data-rating-typography': 'true'}).text.strip()
        return [1, float(score)]
        (score) 
    except:
        return [0, -1]
       

def has_sitejabber_reviews(url: str):
    resp = requests.get(f"https://www.sitejabber.com/reviews/{url}")
    print(resp.status_code)
    
    if resp.status_code == 404:
        # print("not here")
        return 0
    else:
        return 1
