#!/usr/bin/python3

import re
import requests
from bs4 import BeautifulSoup


def is_url(msg):
   regex = r"(https?:\/\/(?:www\.)?\S+)"
   match = re.search(regex, msg)
   if match:
      url = match.group(1)
      return url
   else:
      return None


def get_data(url):
   r = requests.get(url)
   data = r.text
   r.close()
   return data


def get_title(url):
   data = get_data(url)
   soup = BeautifulSoup(data, 'html.parser')
   title = soup.title.string
   del soup
   return title

