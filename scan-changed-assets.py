import requests
import json
from datetime import datetime
import unicodedata
import sys
import time

auth = ('USER', 'PASS')
host = 'http://HOSTNAME'

ts = str(time.time()).split(".")[0]

startdate = sys.argv[1]
enddate = sys.argv[2]

print "Finding pages edited between: " + startdate + " -> " + enddate


queryparams = dict(
    type="JCR-SQL2",
    stmt='''SELECT page.* FROM [dam:Asset] AS page
            INNER JOIN [nt:base] AS jcrcontent ON ISCHILDNODE(jcrcontent, page)
            WHERE ISDESCENDANTNODE(page, "/content/dam")
            AND jcrcontent.[jcr:lastModified] >= CAST("''' + startdate + '''T00:00:00.000Z" AS DATE)
            AND jcrcontent.[jcr:lastModified] <= CAST("''' + enddate + '''T00:00:00.000Z" AS DATE)''',
    showResults="true")

data = requests.get(host + '/crx/de/query.jsp', auth=auth, params=queryparams)

results = data.json()["results"]

pages = []
print "Got " + str(len(results)) + " assets"
print "getting editing dates"
for item in results:
    urlpath = unicodedata.normalize('NFKD', item["path"]).encode('ascii','ignore')
    urlpath = urlpath.replace("/jcr:content", "")

    url = host + '/crx/server/crx.default/jcr%3aroot' + urlpath + '.1.json';

    response = requests.get(host + '/crx/server/crx.default/jcr%3aroot' + urlpath + '/jcr:content.1.json', auth=auth)
    props = response.json()
    date = unicodedata.normalize('NFKD', props["cq:lastModified"]).encode('ascii','ignore')
    pages.append({"path": urlpath, "date": date})

    print '.',
    sys.stdout.flush()

print
print
print "URL,Last Modified"


for item in pages:
    print item["path"] + "," + item["date"]

