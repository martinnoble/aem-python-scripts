import requests
import json
from datetime import datetime
import unicodedata
import sys
import time

#creates a package for each top level folder in the DAM

auth = ('USER', 'PASS')
host = 'https://HOSTNAME'

ts = str(time.time()).split(".")[0]

print "Creating packages for: /content/dam"

folders = requests.get(host + '/bin/wcm/siteadmin/tree.json?path=/content/dam', auth=auth)

data = folders.json()

groupName = 'migration-packages-dam'

def createFilteredPackage(name, filter):
	
	packageName = name + "-" + ts
	print "creating package: " + packageName	
	payload = { 'packageName' : packageName, 'groupName' : groupName }
	package = requests.post(host + '/crx/packmgr/service/exec.json?cmd=create', auth=auth, data=payload)
	result = package.json()
	print result['msg']

	if result['success']:
		print result['path']

		path = result['path']

		newpath = unicodedata.normalize('NFKD', path).encode('ascii','ignore')

		updatePayload = { 'packageName' :(None, packageName), 'groupName' : (None, groupName), 'path': (None, newpath), 'filter': (None, str(filter)), 'acHandling' : (None, 'merge')  }

		print "setting filters"
		update = requests.post(host + '/crx/packmgr/update.jsp', auth=auth, files=dict(foo='bar'), data=updatePayload)

		result = update.json()
		print result['msg']
	else:
		print "something went wrong"




pagecount = 0
for folder in data:
	name = unicodedata.normalize('NFKD', folder['name']).encode('ascii','ignore')
	dampath = "/content/dam/" + name
	filter = []
	filter.append({ "root": dampath, "rules": []})	
	createFilteredPackage("DAM-" + name, filter)

print "done"
