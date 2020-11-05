import requests
import json
from datetime import datetime

auth = ('USER', 'PASSWORD')
host = 'https://HOSTNAME'

r = requests.get(host + '/libs/cq/workflow/content/console/instances.json', auth=auth)

workflows = r.json()

print(workflows['results'])


count= 0
ids = []
starttime = ""
badstart = "none"

for item in workflows['workflows']:
	
	starttime = datetime.utcfromtimestamp(item['startTime']/1000).strftime('%Y-%m-%d %H:%M:%S')
	state = item['state']
	if state == "STALE":
		badstart = starttime
		if count <= 1000:
			print "aborting item: " + starttime + " - " + item['item'] 
			count = count + 1
			result = requests.post(host + item['item'], data={'state':'ABORTED'}, auth=auth)
			if result.text.find("Workflow aborted") > -1:
				print "OK"
			else:
				print "FAILED"
				print result
				print result.text
				break

print "aborted " + str(count) + " items"
