#!/usr/bin/python3

import requests
import hashlib
from bs4 import BeautifulSoup
from time import sleep


efukt_url = "https://efukt.com/"
hashfile  = "efukt_cache"


def get_data(url):
    r = requests.get(url)
    data = r.text
    r.close()
    soup = BeautifulSoup(data, 'html.parser')
    last = soup.find("div", class_="tile").find("h3").find("a", href=True)
    del soup
    title = last.string
    link = last["href"]
    result = [title, link]
    return result


def update_last(title):
    thash = hashlib.md5(title.encode("UTF-8")).hexdigest()
    with open(hashfile, "w") as f:
        f.write(thash)
        f.close()


def compare(title):
    thash = hashlib.md5(title.encode("UTF-8")).hexdigest()
    with open(hashfile, "r") as f:
        last_hash = f.readline()
        f.close()
    if last_hash == thash:
        return True
    else:
        return False


def get_video(url):
    r = requests.get(url)
    data = r.text
    r.close()
    soup = BeautifulSoup(data, 'html.parser')
    vlink = soup.find("video", id="efukt_video").find("source")["src"]
    del soup
    return vlink


def check():
    data = get_data(efukt_url)
    title = data[0]
    link = data[1]
    if compare(title):
        return None
    else:
        update_last(title)
        video = get_video(link)
        return [title, link, video]


def loop():
    while True:
        data = check()
        if not data == None:
            print(data[0]+" - "+data[1])
        sleep(600)


if __name__ == "__main__":
    loop()

