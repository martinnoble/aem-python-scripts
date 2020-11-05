from __future__ import print_function
import requests
import json
from datetime import datetime
import unicodedata
import sys
import time

#build all packages in the group passed as argument
#only builds packages which have not already been built

auth = ('USER', 'PASSWORD')
host = 'https://HOSTNAME'

ts = str(time.time()).split(".")[0]

group = sys.argv[1]

print("Building packages in group: " + group)



packages = requests.get(host + '/crx/packmgr/list.jsp', auth=auth)

data = packages.json()

toProcess = []

for package in data['results']:
	if package['group'] == group and package['buildCount'] == 0:
		item = dict( name=package['name'], path=package['path'])
		toProcess.append(item)


print("Building " + str(len(toProcess)) + " packages")

for package in toProcess:
	print("Processing: " + package['name'])
	result = requests.post(host + '/crx/packmgr/service/script.html' + package['path'] + '?cmd=build', auth=auth, stream=True)

	for line in result.iter_lines():
		if line:
			for part in line.split("<b>"):
				if "<\/b>&nbsp;" in part:
					print(part.split("<\/span>")[0].replace("<\/b>&nbsp;", " "), end='\r')

					if "Package built in" in part.split("<\/span>")[1]:
						print()
						print(part.split("<\/span>")[1].split("Package")[1].split("<")[0])
