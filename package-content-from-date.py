import requests
import json
from datetime import datetime
import unicodedata
import sys
import time

#finds sites and dam assets which have been minified since a given date under a given path.
#<script> startdate author|publish path package-name-prefix

auth = ('USER', 'PASS')
author = 'https://AUTHORHOST'
publish = 'https://PUBLISHHOST'
host = ""

ts = str(time.time()).split(".")[0]

path = sys.argv[3]
prefix = sys.argv[4]

startdate = sys.argv[1]
server = sys.argv[2]

if server == "publish":
    host = publish
else:
    host = author



queryparams = dict(
    type="JCR-SQL2",
    stmt='''SELECT page.* FROM [cq:Page] AS page
            INNER JOIN [nt:base] AS jcrcontent ON ISCHILDNODE(jcrcontent, page)
            WHERE ISDESCENDANTNODE(page, "''' + path + '''")
            AND jcrcontent.[cq:lastModified] >= CAST("''' + startdate + '''T00:00:00.000Z" AS DATE)''',
    showResults="true")

queryparamsAssets = dict(
    type="JCR-SQL2",
    stmt='''SELECT page.* FROM [dam:Asset] AS page
            INNER JOIN [nt:base] AS jcrcontent ON ISCHILDNODE(jcrcontent, page)
            WHERE ISDESCENDANTNODE(page, "/content/dam")
            AND jcrcontent.[jcr:lastModified] >= CAST("''' + startdate + '''T00:00:00.000Z" AS DATE)''',
    showResults="true")

print "Finding pages edited since: " + startdate
data = requests.get(host + '/crx/de/query.jsp', auth=auth, params=queryparams)
results = data.json()["results"]
pages=[]
for item in results:
    urlpath = unicodedata.normalize('NFKD', item["path"]).encode('ascii','ignore')
    urlpath = urlpath.replace("/jcr:content", "")
    pages.append(urlpath)
pages.sort()

print " - " + str(len(pages)) + " pages"


assets = []
print "Finding assets edited since: " + startdate
dataAssets = requests.get(host + '/crx/de/query.jsp', auth=auth, params=queryparamsAssets)
resultsAssets = dataAssets.json()["results"]
for item in resultsAssets:
    urlpath = unicodedata.normalize('NFKD', item["path"]).encode('ascii','ignore')
    urlpath = urlpath.replace("/jcr:content", "")
    assets.append(urlpath)

print " - " + str(len(assets)) + " assets"


groupName = 'migration-packages'


def createFilteredPackage(filter, contenttype):

	
	packageName = server + "-" + contenttype + "-since-" + startdate
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
		update = requests.post(host + '/crx/packmgr/update.jsp', auth=auth, files=updatePayload)

		result = update.json()
		print result['msg']
	else:
		print "something went wrong"




filter = []
pagecount = 0
for page in pages:

        rules = []
        filter.append({ 'root': page + "/jcr:content", 'rules': rules})

if len(filter) > 0:
    createFilteredPackage(filter, prefix + "-pages")



filter = []
pagecount = 0
for item in assets:

        rules = []
	filter.append({ 'root': item, 'rules': rules})

if len(filter) > 0:
    createFilteredPackage(filter, prefix + "-assets")


print "done"
