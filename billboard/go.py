from bs4 import BeautifulSoup
import urllib2
from datetime import date, timedelta
from multiprocessing import Process
import time

BILLBOARD_BASE_URL = 'http://www.billboard.com/charts/hot-100/'
FIRST_CHART_DATE = date(1958,8,9) # the first saturday billboard had a chart

def getNumberOne(week):
	d = FIRST_CHART_DATE + week * timedelta(7)
	url = '%s%04d-%02d-%02d' % (BILLBOARD_BASE_URL, d.year, d.month, d.day)
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page, 'html.parser')
	artist = soup.find("a", {"class":"chart-row__artist"}) # we want the number one hits, 
	title = soup.find("h2", {"class":"chart-row__song"})   # so it's fine to just grab the first results
	return { \
		"artist":artist.getText().strip(), \
		"title": title.getText().strip(),  \
		"date": d \
		}

def partialList(start,end):
	fname = '%04d-%04d.csv' % (start,end)
	count = 0
	f = open(fname, 'w')
	for i in range(start,end):
		hit = getNumberOne(i)
		row = '%s,%s,%s' % (hit["date"], hit["artist"], hit["title"])
		f.write('%s\n' % (row.encode('utf8')))
		f.flush()
		count = count + 1
		print '%d: (%0.2f)' % (count, time.time() - starttime), row.encode('utf8')
	f.close()

starttime = time.time()
if __name__ == '__main__':
	jobs=[]
	weeks=range(0,100,20)
	for i in range(len(weeks)-1):
		p = Process(target=partialList, args=(weeks[i],weeks[i+1]))
		p.start()
		jobs.append(p)

	for proc in jobs:
		proc.join()

	endtime=time.time()
	print endtime - starttime
