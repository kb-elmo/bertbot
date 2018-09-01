#!/usr/bin/python3

import json
import urllib.request
import datetime
import time
import pytz
from string import Template

b = "\x0312"
y = "\x038"

API_URL = "https://launchlibrary.net/1.2/launch/next/1"

class launch(object):
   def api_request(self):
      request = urllib.request.Request(API_URL)
      response = urllib.request.urlopen(request).read()
      json_data = json.loads(response.decode('UTF-8'))
      return json_data['launches'][0]

   def rocket_name(self, json_data):
      try:
         name = json_data['rocket']['name']
      except:
         name = "UNKNOWN"
      return name

   def mission_name(self, json_data):
      try:
         name = json_data['missions'][0]['name']
      except:
         name = "UNKNOWN"
      return name

   def net_raw_utc(self, json_data):
      time_utc_string = json_data['net']
      try:
         time_utc = datetime.datetime.strptime(time_utc_string, '%B %d, %Y %H:%M:%S %Z')
      except TypeError:
         time_utc = datetime.datetime(*(time.strptime(time_utc_string, '%B %d, %Y %H:%M:%S %Z')[0:6]))
      return time_utc

   def net(self, json_data):
      time_utc_string = json_data['net']
      try:
         time_utc = datetime.datetime.strptime(time_utc_string, '%B %d, %Y %H:%M:%S %Z')
      except TypeError:
         time_utc = datetime.datetime(*(time.strptime(time_utc_string, '%B %d, %Y %H:%M:%S %Z')[0:6]))
      time_local = pytz.utc.localize(time_utc).astimezone(pytz.timezone('Europe/Berlin'))
      time = datetime.datetime.strftime(time_local, 'NET %d.%m.%Y')
      return time

   def get_status(self, json_data):
      tbd_stat = json_data['tbdtime']
      hold_stat = json_data['inhold']
      go_stat = json_data['status']
      if tbd_stat == 1:
         status = "TBD"
      elif hold_stat == 1:
         status = "HOLD"
      elif go_stat == 1:
         status = "GO"
      else:
         status = "UNKNOWN"
      return status


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def next_launch():
   l = launch()
   json_data = l.api_request()
   rocket = l.rocket_name(json_data)
   mission = l.mission_name(json_data)
   status = l.get_status(json_data)
   if status != "GO":
      deltastring = l.net(json_data)
   else:
      launch_time = l.net_raw_utc(json_data)
      now = datetime.datetime.utcnow().replace(microsecond=0)
      if launch_time > now:
         timedelta = launch_time - now
         t_string = "-"
      else:
         timedelta = now - launch_time
         t_string = "+"
      deltastring = strfdelta(timedelta, "T"+t_string+"%D:%H:%M:%S")
   del l
   return rocket, mission, status, deltastring
