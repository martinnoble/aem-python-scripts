from __future__ import print_function
import requests
import json
from datetime import datetime
import unicodedata
import sys
import time

#install all non-installed packages in group passed as argument

auth = ('USER', 'PASS')
host = 'http://HOST'

ts = str(time.time()).split(".")[0]

group = sys.argv[1]

print("Installing packages in group: " + group)



packages = requests.get(host + '/crx/packmgr/list.jsp', auth=auth)

data = packages.json()

toProcess = []

for package in data['results']:
	if package['group'] == group and 'lastUnpacked' not in package:
		item = dict( name=package['name'], path=package['path'])
		toProcess.append(item)
print(toProcess)

print("Installing " + str(len(toProcess)) + " packages")

for package in toProcess:
	print("Processing: " + package['name'])
	postData = dict(cmd='install', autosave='1024', recursive='true', acHandling='merge', dependencyHandling='required')
	result = requests.post(host + '/crx/packmgr/service/script.html' + package['path'], auth=auth, files=dict(foo='bar'), data=postData, stream=True)

	for line in result.iter_lines():
		if line:
			for part in line.split("<b>"):
				if "<\/b>&nbsp;" in part:
					print(part.split("<\/span>")[0].replace("<\/b>&nbsp;", " "), end='\r')

					if "Package installed in" in part.split("<\/span>")[1]:
						print()
						print(part.split("<\/span>")[1].split("Package")[1].split("<")[0])
