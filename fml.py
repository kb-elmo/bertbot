#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup


url = "http://www.fmylife.com/random"


def get_fml(url):
   r = requests.get(url)
   data = r.text
   r.close
   soup = BeautifulSoup(data, 'html.parser')
   fml = soup.find("article", class_="art-panel").find_all("a")[2].string.strip().replace("\\", "").replace(" FML", "")
   del soup
   return fml

