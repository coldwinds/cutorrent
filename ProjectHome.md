cuTorrent is a simple command-line tool that interacts with remote [uTorrent](http://www.utorrent.com) instances through thier [webui](http://forum.utorrent.com/viewtopic.php?id=14565).

### uTorrent Setup ###
To use cuTorrent you must have uTorrent running with the webUI on. For step by step instructions on setting up webUI see this [lifehacker's article](http://lifehacker.com/software/hack-attack/remote-control-your-torrents-with-utorrents-webui-260393.php)



### Usage ###
```
 cuTorrent <options>

Options:
 -h/--help       This screen
 -s/--silent     Silent run (ie no output)
 -l/--upload     File or URL of a torrent to upload
 -t/--hash       Hashs of the torrents to modify
                 (separate hashes by commas)
 -a/--action     Action to preform (default: list)
                   list   - List all torrents
                   start  - Start torrents
                   fstart - Force torrents to start
                   stop   - Stop torrents
                   remove - Remove torrents
                   detail - Print detailed torrent information
 -o/--host       Hostname (default: localhost)
 -p/--port       Port (default: 8080)
 -u/--user       Username (default: admin)
 -w/--password   Password (default: admin)
```