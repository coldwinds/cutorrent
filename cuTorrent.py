#!/usr/bin/env python

# Copyright 2007 Saul Bancroft
#
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
# http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License.

# More API Details: http://forum.utorrent.com/viewtopic.php?pid=272592

from uTorrent_py.uTorrent import *
import getopt
import sys
import os

Colors = { 
          'blue' : "\033[34m",
          'red' : "\033[31m",
          'grey' : "\033[37m",
          'green' : "\033[32m",
          'cyan' : "\033[36m",
          'yellow' : "\033[33m",
          'normal' : "\033[0m",
         } 

if os.name != 'posix':
  for a in Colors.keys():
    Colors[a] = ""

# State Strings
State_Strings = (
                 #(1   , "Started"),
                 #(2   , "Checking"),
                 #(4   , "Start after Check"),
                 #(8   , "Checked"),
                 #(16  , "Error"),
                 #(32  , "Paused"),
                 #(64  , "Queued"),
                 #(128 , "Loaded"),
                 (16  , "Error"),
                 (2   , "Checking"),
                 (32  , "Paused"),
                 (1+64, "Downloading"),
                 (8+128, "Stopped"),
                 (1, "Forced Download"),
                ) 

class torrent:
  def __init__(self, torrent_info, file_info=None):
    self.update(torrent_info)
    if file_info:
      self.update_files(file_info)

  def update(self, torrent_info):
    self.info = torrent_info;
    self.hash = self.info[UT_TORRENT_PROP_HASH]
    self.name = self.info[UT_TORRENT_PROP_NAME]
    self.percent = self.info[UT_TORRENT_STAT_P1000_DONE] / 10.0
    self.speed_up = self.info[UT_TORRENT_STAT_SPEED_UP] / 1000.0
    self.speed_down = self.info[UT_TORRENT_STAT_SPEED_DOWN] / 1000.0
    self.eta = self.info[UT_TORRENT_STAT_ETA] 
    self.left = self.info[UT_TORRENT_STAT_BYTES_LEFT]
    self.size = self.info[UT_TORRENT_STAT_BYTES_SIZE]
    self.state = self.info[UT_TORRENT_PROP_STATE]
    self.ratio = self.info[UT_TORRENT_STAT_RATIO]
    self.seed_num = self.info[UT_TORRENT_STAT_SEED_CONN]
    self.peer_num = self.info[UT_TORRENT_STAT_PEER_CONN]
    self.position = self.info[UT_TORRENT_STAT_QUEUE_POS]

  def update_files(self, file_info):
    self.files_info = []
    for  f in file_info['files'][1]:
      self.files_info.append({
                              'name': f[0],
                              'size': f[1],
                              'download': f[2],
                              'priority':f[3],
                              })
  
  def detailed(self):
    a = ""
    a += "Name: %s\n" % self.name
    a += "Hash: %s\n" % self.hash
    a += "Position: %s\n" % self.position
    a += "Percent: %.1f\n" % self.percent
    a += "Speed up: %s\n" % self.speed_up
    a += "Speed down: %s\n" % self.speed_down
    a += "ETA: %s\n" % self.decode_time(self.eta)
    a += "Bytes Left: %s\n" % self.left
    a += "Total Bytes: %s\n" % self.size
    a += "State: %o\n" % self.state
    a += "Ratio: %s\n" % (self.ratio / 1000.0)
    a += "Seeds: %s\n" % self.seed_num
    a += "Peers: %s\n" % self.peer_num
    a += "Files:\n"
    for f in self.files_info:
      a += "\t%s (%d/%d)\n" % (f['name'], f['size'], f['download'])
    return a

  def decode_time(self, time):
    sec = time % 60 
    time = time / 60
    min = time % 60 
    time = time / 60
    hour = time % 24
    days = time / 24
    if days == -1:
      return "N/A"
    return "%s %s:%02d.%s" % (days, hour, min, sec)

  def console_out(self, color=True):
    p = "  "
    if self.position != -1:
      p = "%02d" % self.position
    s  = "%s(%s)%s %s : %s\n" % \
                (Colors['yellow'], p, Colors['normal'],
                 self.name,self.state_str())
    s += "\t"+Colors['blue'] + self.hash + Colors['normal'] + " - "
    s += "%s%.1f%s%% " % (Colors['red'], self.percent, Colors['normal']) 
    s += "(" + Colors['green'] + "D:" + str(self.speed_down) + Colors['normal'] +", "
    s += Colors['cyan'] + "U:" + str(self.speed_up) + Colors['normal'] + ") "
    s += "eta: " + self.decode_time(self.eta)
    return s

  def state_str(self):
    state_o = ""
    for bits, string in State_Strings:
      if bits & self.state:
        state_o = string 
        break
    return "%s (%o)" % (state_o, self.state)

  def __str__(self):
    s = "%s (%s): %s%% (D:%s, U:%s)" % (self.name, self.hash, self.percent, 
                                        self.speed_down, self.speed_up)
    s += "\n eta: %s - %s" % (self.decode_time(self.eta), self.state_str())
    return s



class torrents:
  def __init__(self, host="localhost",port='8080', username='admin', password='admin'):
    self.connection = uTorrent(host=host,port=port, username=username, password=password)
    self.speed_up = 0
    self.speed_down = 0
    self.update()

  def update(self):
    l = self.connection.webui_ls()
    self.torrent_list = {}
    self.speed_up = 0.0
    self.speed_down = 0.0
    for t in l: 
      t2 = torrent(t) 
      self.speed_up += t2.speed_up
      self.speed_down += t2.speed_down
      self.torrent_list[t2.hash] = t2

  def getTorrent(self, tor):
    order = 0
    try: 
     order = int(tor)
    except :
     order = 0 
    hash = ""
    if order > 0 and order < 100:
      # it's an ordering not a hash
      for t in self.torrent_list.values():
        if t.position == order:
          hash = t.hash
          break
      if hash == "":
        raise Exception('Incorrect torrent number')
    else:
      hash = tor
    if hash in self.torrent_list:
      return self.torrent_list[hash]
    raise Exception('Invalid torrent id')

  def get_torrent_file_list(self, hash):
    return self.connection.webui_ls_files(hash)

  def add_torrent(self, file):
    result = None
    low_file = file.lower()
    if low_file.startswith("http:") or low_file.startswith("ftp:"):
      result = self.connection.webui_add_url(file)
    else:
      result = self.connection.webui_add_file(file)
    if result == None:
      raise Exception("Failed to open torrent")
    self.update()

  def remove(self, hash):
    self.connection.webui_remove(hash)

  def stop(self, hash):
    self.connection.webui_stop_torrent(hash)

  def pause(self, hash):
    self.connection.webui_pause_torrent(hash)

  def force_start(self, hash):
    self.connection.webui_forcestart_torrent(hash)

  def start(self, hash):
    self.connection.webui_start_torrent(hash)

  def __str__(self):
    s = ""
    for t in self.torrent_list.values():
      s += t.console_out() + "\n"
    s += "total: D:%s U:%s" %(self.speed_down, self.speed_up)
    return s

def usage():
  print "      cuTorrent"
  print "By: Saul Bancroft <saul.bancroft@gmail.com>"
  print ""
  print "Remember you need to have uTorrent running with the webUI turned on"
  print "before this program will work"
  print ""
  print "Usage:"
  print " -h/--help       This screen"
  print " -s/--silent     Silent run (ie no output)"
  print " -l/--upload     File or URL of a torrent to upload"
  print " -t/--torrent    Hashs or Number of the torrents to modify"
  print "                 (separate hashes by commas)"
  print " -a/--action     Action to preform (default: list)"
  print "                   list   - List all torrents"
  print "                   start  - Start torrents"
  print "                   fstart - Force torrents to start"
  print "                   stop   - Stop torrents"
  print "                   pause  - Pause torrents"
  print "                   remove - Remove torrents"
  print "                   detail - Print detailed torrent information"
  print " -o/--host       WebUI's Hostname (default: localhost)"
  print " -p/--port       WebUI's Port (default: 8080)"
  print " -u/--user       WebUI's Username (default: admin)"
  print " -w/--password   WebUI's Password (default: admin)"

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hsl:a:p:o:u:w:t:", 
      ["help", "silent",
       "upload=", "host=",
       "port=", "user=", 
       "password=", "torrent=", "hash=",
       "action=",
       "remove", "start", "stop", "pause", "fstart", "detail", "list"])
  except getopt.GetoptError:
    # print help information and exit:
    usage()
    sys.exit(2)
  host = "localhost"
  port = 8080
  torrent_ids = []
  action = "list"
  username = "admin"
  password = "admin"
  file = None
  silent = False
  for o, a in opts:
    if o == "-s" or o == "--silent":
      silent = True
    elif o == "-h" or o == "--help":
      usage()
      return
    elif o == "--torrent" or o == "--hash" or o == "-t":
      if "," in a:
        for b in a.split(","):
          torrent_ids.append(b)
      else:
        torrent_ids.append(a)
    elif o == "--host" or o == "-o":
      host = a
    elif o == "--port" or o == "-p":
      port = int(a)
    elif o == "--user" or o == "-u":
      username = a
    elif o == "--password" or o == "-w":
      password = a
    elif o == "--upload" or o == "-l":
      file = a
    elif o == "--action" or o == "-a":
      action = a
    elif o == "--remove":
      action = "remove"
    elif o == "--start":
      action = "start"
    elif o == "--fstart":
      action = "fstart"
    elif o == "--stop":
      action = "stop"
    elif o == "--pause":
      action = "pause"
    elif o == "--detail":
      action = "detail"
    elif o == "--list":
      action = "list"

  try:
    list = torrents(host=host,port=port,username=username,password=password)
  except:
    print "ERROR: Unable to connect to uTorrent Web UI"
    usage()
    sys.exit(1)

  if not silent:
    print "      cuTorrent"
    print "By: Saul Bancroft <saul.bancroft@gmail.com>"
    print ""
    print "+"+action+"+"
  if file is not None:
    if not silent:
      print "uploading torrent %s" % file
    list.add_torrent(file)
  if action == "list":  
    if not silent:
      print list
  elif len(torrent_ids) > 0:
    for tor_id in torrent_ids:
      tor = list.getTorrent(tor_id)
      if tor is None:
        continue
      name = tor.name  
      hash = tor.hash
      if action == "start":  
        if not silent:
          print "Start: %s" % name 
        list.start(hash)
      elif action == "stop":  
        if not silent:
          print "Stop: %s" % name
        list.stop(hash)
      elif action == "pause":  
        if not silent:
          print "Pause: %s" % name
        list.pause(hash)
      elif action == "fstart":  
        if not silent:
          print "Force Start: %s" % name 
        list.force_start(hash)  
      elif action == "remove":  
        if not silent:
          print "Remove Torrent: %s" % name 
        list.remove(hash)  
      elif action == "detail":  
        if not silent:
          print "Details: %s" % name 
        t = list.getTorrent(hash)
        t.update_files(list.get_torrent_file_list(hash))
        if t is not None:
          if not silent:
            print t.detailed()
  elif file is None:
    usage()

#	the sandbox
if (__name__ == '__main__'):
  main()
