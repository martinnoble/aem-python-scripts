from __future__ import print_function
import requests
import json
from datetime import datetime
import unicodedata
import sys
import time

auth = ('USER', 'PASS')
host='http://HOSTNAME'

ts = str(time.time()).split(".")[0]

path = sys.argv[1]

print("Tree replicating: " + path)

cmd = 'dryrun'
payload = { 'path': path, 'ignoredeactivated' : 'true', 'cmd' : cmd }

print("Getting activation total")
r = requests.post(host + '/etc/replication/treeactivation.html', auth=auth, data=payload)

data = r.text
total = int(data.split("<br><strong>Activated ")[1].split(" ")[0])

print
print("Expecting to activate " + str(total) + " items")

if len(sys.argv) == 3:
	payload['cmd'] = 'activate'

r = requests.post(host + '/etc/replication/treeactivation.html', auth=auth, data=payload, stream=True)

print()

pos = 0

for line in r.iter_lines():
	if line:
		for part in line.split("action "):
			if "class=\"path\"" in  part:
				percent = (float(pos) / total) * 100
				bits = part.split(">")
				print("{0:.2f}".format(percent)  + "%\t" + " " + bits[1].split("<")[0] + ": " + bits[5].split("<")[0], end="\r")
				
				if "Activate" in part:
					pos = pos + 1

			if "<strong>Activated" in part:
				print()
				print(part.split("<strong>")[1].split("<")[0])

