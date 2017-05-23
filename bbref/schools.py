from bs4 import BeautifulSoup
import urllib2
from datetime import date, timedelta
from multiprocessing import Process
import time
import geocoder
import re
import os

BBREF_SCHOOLS_BASE_URL = 'http://www.baseball-reference.com/schools/'
BBREF_HS_URL = 'http://www.baseball-reference.com/schools/secondary.shtml'

def geocodeSchool(school):
	s = {}
	try:
		g = geocoder.google(school.text)
	except:
		try: 
			g = geocoder.osm(school.text)
		except:
			return None

	if g.confidence > 5:
		s["school"] = re.compile(r'(.*) \(').findall(school.text)[0]
		s["latitude"] = g.lat
		s["longitude"] = g.lng
		s["street"] = g.street
		s["housenumber"] = g.housenumber
		s["city"] = g.city
		s["state"] = g.state
		s["postal_code"] = g.postal
		s["country"] = g.country
		vals = re.compile(r'\d+').findall(school.parent.text)[-2:]
		s["mlb_players"] = vals[0]
		s["all_players"] = vals[1]
	
		return s
	else:
		return None


def saveSchools(schools,outfile):
	f = open(outfile,'w')
	i = 0
	l = len(schools)
	for school in schools:
		starttime = time.time()
		result = 'xx'
		s = geocodeSchool(school)
		if s != None:
			row = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%f,%f\n' % (s["school"],s["mlb_players"],s["all_players"],s["housenumber"],s["street"],s["city"],s["state"],s["postal_code"],s["country"],s["latitude"],s["longitude"])
			f.write(row.encode('utf8'))
			result = 'OK'
		print '%0d' % (100 * i / l), '%0.2f' % (time.time() - starttime), result, school.text

		i = i + 1
		if (i%10) == 0:
			f.flush()
	f.close()

def getSchools():
	url = BBREF_HS_URL
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page, 'html.parser')
	content = soup.find("div", {"class":"section_content"})
	schools = content.findAll("a")

	print len(schools), 'schools'
	l = len(schools)
	groups = 3

	breaks = range(0,l,l/groups)
	breaks.append(l)
	outfiles = []

	jobs = []
	for i in range(groups):
		outfile = '%05d-%05d.csv' % (breaks[i],breaks[i+1])
		outfiles.append(outfile)
		p = Process(target=saveSchools, args=(schools[breaks[i]:breaks[i+1]],outfile))
		p.start()
		jobs.append(p)

	for proc in jobs:
		proc.join()

	return outfiles

if __name__ == '__main__':
	starttime = time.time()
	
	tempfiles = getSchools()
	with open('schools.csv', 'w') as outfile:
		outfile.write('school,mlb_players,all_players,housenumber,street,city,state,postal_code,country,latitude,longitude\n')
		for file in tempfiles:
			with open (file) as f:
				for line in f:
					outfile.write(line)

	print time.time()-starttime