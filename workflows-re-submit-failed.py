import requests
import json
from datetime import datetime


auth = ('USER', 'PASS')
host = "https://HOSTNAME"

r = requests.get(host + '/libs/cq/workflow/content/console/failures.json', auth=auth)

failed = r.json()

print(failed['results'])


count= 0
ids = []
starttime = ""
badstart = "none"

for item in failed['workflows']:
	
	starttime = datetime.utcfromtimestamp(item['startTime']/1000).strftime('%Y-%m-%d %H:%M:%S')
	message = item['failureInfo']['message']
	if message.startswith('Process implementation not found'):
		badstart = starttime
		if count <= 200:
			print "resubmiting item: " + starttime + " - " + item['item'] 
			count = count + 1
			ids.append(item['item'])

data = {}
data['IDs'] = ids;

json_data = json.dumps(data)

print
print "start time on last item in failure list: " + starttime
print "start time on last re-submittable failure: " + badstart
print
print "retrying " + str(count) + " items"

result = requests.post(host + '/libs/cq/workflow/failures?command=TerminateAndRestart', auth=auth, data=json_data)
print result

print result.text
