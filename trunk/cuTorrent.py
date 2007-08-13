
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

from uTorrent_py.uTorrent import *
import getopt
import sys

class torrent:
  def __init__(self, torrent_info):
    self.update(torrent_info)

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

  def detailed(self):
    a = ""
    a += "Name: %s\n" % self.name
    a += "Hash: %s\n" % self.hash
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
    return a

  def decode_time(self, time):
    sec = time % 60 
    time = time / 60
    min = time % 60 
    time = time / 60
    hour = time % 24
    days = time / 24
    return "%s %s:%02d.%s" % (days, hour, min, sec)

  def console_out(self, color=True):
    blue = ""
    grey = ""
    green = ""
    cyan = ""
    red = ""
    normal = ""
    if color:
      blue = "\033[34m"
      red = "\033[31m"
      grey = "\033[37m"
      green = "\033[32m"
      cyan = "\033[36m"
      normal = "\033[0m"
    s  = self.name + ": %s\n" % self.state_str()
    s += "\t"+blue + self.hash + normal + " - "
    s += "%s%.1f%s%% " % (red, self.percent, normal) 
    s += "(" + green + "D:" + str(self.speed_down) + normal +", "
    s += cyan + "U:" + str(self.speed_up) + normal + ") "
    s += "eta: " + self.decode_time(self.eta)
    return s

  def state_str(self):
    state_o = "%o" % self.state
    if state_o == "310":
      return "queued"
    elif state_o == "311":
      return "downloading"
    elif state_o == "210":
      return "stoped"
    elif state_o == "211":
      return "force start"
    return state_o

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

  def getTorrent(self, hash):
    if hash in self.torrent_list:
      return self.torrent_list[hash]
    return None

  def add_file(self, file):
    if file.startswith("http") or file.startswith("ftp"):
      self.connection.webui_add_url(file)
    else:
      self.connection.webui_add_file(file)
    self.update()

  def remove(self, hash):
    self.connection.webui_remove(hash)

  def stop(self, hash):
    self.connection.webui_stop_torrent(hash)

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
  print " -t/--hash       Hashs of the torrents to modify"
  print "                 (separate hashes by commas)"
  print " -a/--action     Action to preform (default: list)"
  print "                   list   - List all torrents"
  print "                   start  - Start torrents"
  print "                   fstart - Force torrents to start"
  print "                   stop   - Stop torrents"
  print "                   remove - Remove torrents"
  print "                   detail - Print detailed torrent information"
  print " -o/--host       Hostname (default: localhost)"
  print " -p/--port       Port (default: 8080)"
  print " -u/--user       Username (default: admin)"
  print " -w/--password   Password (default: admin)"

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hsl:a:p:o:u:w:", 
      ["help", "silent",
       "upload=", "host=",
       "port=", "user=", 
       "password=", "hash=",
       "action="])
  except getopt.GetoptError:
    # print help information and exit:
    usage()
    sys.exit(2)
  host = "localhost"
  port = 8080
  hashs = []
  action = "list"
  username = "admin"
  password = "admin"
  file = None
  silent = False
  for o, a in opts:
    #print o
    if o == "-s" or o == "--silent":
      silent = True
    elif o == "-h" or o == "--help":
      usage()
      return
    elif o == "--hash" or o == "-t":
      if "," in a:
        for b in a.split(","):
          hashs.append(b)
      else:
        hashs.append(a)
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

  if not silent:
    print "      cuTorrent"
    print "By: Saul Bancroft <saul.bancroft@gmail.com>"
    print ""
    print "+"+action+"+"
  list = torrents(host=host,port=port,username=username,password=password)
  if file is not None:
    if not silent:
      print "uploading torrent %s" % file
    list.add_file(file)
  if action == "list":  
    if not silent:
      print list
  elif len(hashs) > 0:
    for hash in hashs:
      if action == "start":  
        if not silent:
          print "Start: %s" % hash
        list.start(hash)
      elif action == "stop":  
        if not silent:
          print "Stop: %s" % hash
        list.stop(hash)
      elif action == "fstart":  
        if not silent:
          print "Force Start: %s" % hash
        list.force_start(hash)  
      elif action == "remove":  
        if not silent:
          print "Remove Torrent: %s" % hash
        list.remove(hash)  
      elif action == "detail":  
        if not silent:
          print "Details: %s" % hash
        t = list.getTorrent(hash)
        if t is not None:
          if not silent:
            print t.detailed()
  elif file is None:
    usage()

#	the sandbox
if (__name__ == '__main__'):
  main()
