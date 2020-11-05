import requests
import json
from datetime import datetime
import unicodedata
import sys
import time

#creates sites packages for all content under a given "brand" - this is the top level path, eg /content/<brand>
#each package will contain a maximum of 50 sites under this brand
#multiple packages are created if the limit is exceeded

auth = ('USER', 'PASS')
host = 'https://HOST'

ts = str(time.time()).split(".")[0]

brand = sys.argv[1]

print "Creating packages for: " + brand


sites = requests.get(host + '/content.pages.json', auth=auth)

data = sites.json()
pages = data['pages']


filecount = 1
groupName = 'migration-packages'
sitelimit = 50



def createFilteredPackage(filter):

	global filecount
	
	packageName = brand + "-" + ts + "-" + str(filecount)
	print "creating package: " + packageName	
	payload = { 'packageName' : packageName, 'groupName' : groupName }
	package = requests.post(host + '/crx/packmgr/service/exec.json?cmd=create', auth=auth, data=payload)
	result = package.json()
	print result['msg']

	filecount = filecount + 1

	if result['success']:
		print result['path']

		path = result['path']

		newpath = unicodedata.normalize('NFKD', path).encode('ascii','ignore')

		updatePayload = { 'packageName' :(None, packageName), 'groupName' : (None, groupName), 'path': (None, newpath), 'filter': (None, str(filter)), 'acHandling' : (None, 'merge')  }

		print "setting filters"
		update = requests.post(host + '/crx/packmgr/update.jsp', auth=auth, files=updatePayload)

		result = update.json()
		print result['msg']
	else:
		print "something went wrong"




filter = []
pagecount = 0
for page in pages:
	path = page['path']
	siteprefix = "/content/" + brand
	if siteprefix in path:
		pagepath = unicodedata.normalize('NFKD', path).encode('ascii','ignore')
		filter.append({ 'root': pagepath, 'rules': []})
		
	if len(filter) >= sitelimit:
		createFilteredPackage(filter)
		filter = []

if len(filter) > 0:
	createFilteredPackage(filter)

print "done"
