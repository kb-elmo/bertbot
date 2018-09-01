#!/usr/bin/python3
# -*- coding: utf-8 -*-

import feedparser
import time
from subprocess import check_output
import sys

def check():
   feed_name = 'fefe'
   url = 'https://blog.fefe.de/rss.xml'
   
   #feed_name = sys.argv[1]
   #url = sys.argv[2]
   
   db = 'rss_feeds.db'
   limit = 12 * 3600 * 1000

   blogresult = None
   
   #
   # function to get the current time
   #
   current_time_millis = lambda: int(round(time.time() * 1000))
   current_timestamp = current_time_millis()
   
   def post_is_in_db(title):
       with open(db, 'r') as database:
           for line in database:
               if title in line:
                   return True
           database.close()
       return False
   
   # return true if the title is in the database with a timestamp > limit
   def post_is_in_db_with_old_timestamp(title):
       with open(db, 'r') as database:
           for line in database:
               if title in line:
                   ts_as_string = line.split('|', 1)[1]
                   ts = int(ts_as_string)
                   if current_timestamp - ts > limit:
                       return True
           database.close()
       return False
   
   #
   # get the feed data from the url
   #
   feed = feedparser.parse(url)
   
   #
   # figure out which posts to print
   #
   posts_to_print = []
   posts_to_skip = []
   
   for post in feed.entries:
       # if post is already in the database, skip it
       # TODO check the time
       title = post.title.split(".")[0]
       link = post.link
         
       if post_is_in_db_with_old_timestamp(title):
           posts_to_skip.append(title+";"+link)
       else:
           posts_to_print.append(title+";"+link)
       
   #
   # add all the posts we're going to print to the database with the current timestamp
   # (but only if they're not already in there)
   #
   f = open(db, 'a')
   for line in posts_to_print:
       content = line.split(";")
       try:
         title = content[0]
         link  = content[1]
         if not post_is_in_db(title):
             f.write(title + "|" + str(current_timestamp) + "\n")
             blogresult = str(title)+" - "+str(link)
       except:
         title = content[0].encode("cp1252").decode("utf-8", "ignore")
         link  = content[1].encode("cp1252").decode("utf-8", "ignore")
         if not post_is_in_db(title):
             f.write(title + "|" + str(current_timestamp) + "\n")
             blogresult = str(title)+" - "+str(link)
   f.close

   del feed

   return blogresult
    

def main():
   check()

if __name__ == "__main__":
   main()
