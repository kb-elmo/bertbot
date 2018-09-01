#!/usr/bin/python3

import re
import random
import json
import requests
from bs4 import BeautifulSoup

# returns a list of quotes
def get_quotes():
    url = "https://de.wikiquote.org/w/api.php?action=parse&format=json&pageid=155&section=2"
    r = requests.get(url)
    data = r.json()
    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")
    quotes_raw = soup.div.find_all("ul", recursive=False)
    quotes = []
    for quote in quotes_raw:
        soup = BeautifulSoup(str(quote), "html.parser")
        for a in soup.find_all("a"):
            a.replaceWithChildren()
        soup = BeautifulSoup(str(soup), "html.parser")
        q_raw = soup.find("ul").find("li", recursive=False).contents[0]
        q = re.search(r"\"([^\"”]+)", q_raw).group(1)
        quotes.append(q)
    del soup
    return quotes


def random_quote():
    quotes = get_quotes()
    quote = random.choice(quotes)
    return quote


def main():
    quotes = get_quotes()
    print("Konfuzius sagt: "+random.choice(quotes))


if __name__ == "__main__":
    main()
