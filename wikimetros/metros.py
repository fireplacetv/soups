from bs4 import BeautifulSoup
import urllib2
from datetime import date, timedelta
from multiprocessing import Process
import time
import re

METRO_LIST_URL = 'https://en.wikipedia.org/wiki/List_of_metro_systems'
OUTFILE = 'metros.csv'
NAME_COL = 'name' # name
COUNTRY_COL = 'country' # country
CITY_COL = 'city' # city
OPENED_COL = 'opened' # opened
UPDATED_COL = 'updated' # last updated
LENGTH_COL = 'length' # length in km
STATIONS_COL = 'stations' # number of stations
RIDERSHIP_COL = 'ridership' # annual ridership
LINES_COL = 'lines' # number of lines
OUTPUT_COLUMNS = [NAME_COL,CITY_COL,COUNTRY_COL,OPENED_COL,UPDATED_COL,LENGTH_COL,STATIONS_COL,RIDERSHIP_COL]

def writeMetroList(metro_list, out_file = OUTFILE):
	f = open(out_file, 'w')
	f.write(','.join(OUTPUT_COLUMNS) + '\n')
	for m in metro_list:
		try:
			cols = []
			for col in OUTPUT_COLUMNS:
				if m[col] != None:
					cols.append(str(m[col]))
				else:
					cols.append('')
			f.write(','.join(cols) + '\n')
		except:
			print m
			raise
	f.close()

def getMetroList():
	metro_list = []

	page = urllib2.urlopen(METRO_LIST_URL)
	soup = BeautifulSoup(page, 'html.parser')
	metro_table = soup.find('table') # it's the first table
	metro_rows = metro_table.find_all('tr')
	i = 1
	nMetros = len(metro_rows)
	while (i < nMetros):
		attrs = metro_rows[i].find('td').attrs
		if 'rowspan' in attrs.keys():
			rowspan = int(attrs['rowspan'])
			new_metros = parseMetroRows(metro_rows[i:(i+rowspan)])
			for m in new_metros:
				metro_list.append(m)
			i += rowspan
		else:
			new_metro = parseSingleRow(metro_rows[i])
			metro_list.append(new_metro)
			i += 1

	return metro_list

		
def parseMetroRows(metro_rows):
	short_metro_list = []
	if len(metro_rows) > 1:
		cols = metro_rows[0].find_all('td')
		# city
		city = cols[0].find_all('a')[0].text.encode('utf8')
		# country
		country = cols[1].find_all('a')[0].text.encode('utf8')
		for row in metro_rows:
			short_metro_list.append(parseSingleRow(row, {CITY_COL: city, COUNTRY_COL: country}))
	else:
		short_metro_list.append(parseSingleRow(metro_rows[0]))

	return short_metro_list

def parseSingleRow(row, city_and_country = None):
	metro = {}

	cols = row.find_all('td')	

	if city_and_country != None:
		metro[CITY_COL] = city_and_country[CITY_COL]
		metro[COUNTRY_COL] = city_and_country[COUNTRY_COL]
	else:
		# city
		metro[CITY_COL] = cols[-8].find_all('a')[0].text.encode('utf8')
		# country
		metro[COUNTRY_COL] = cols[-7].find_all('a')[0].text.encode('utf8')
	
	# name
	metro[NAME_COL] = cols[-6].find_all('a')[0].text.encode('utf8')

	# opened (need to use regex in case there are footnotes)
	try:
		metro[OPENED_COL] = int(re.compile(r'([0-9]+)').findall(cols[-5].text)[0])
	except:
		metro[OPENED_COL] = None

	# updated
	try:
		metro[UPDATED_COL] = int(re.compile(r'([0-9]+)').findall(cols[-4].text)[0])
	except:
		metro[UPDATED_COL] = None

	# stations 
	try:
		metro[STATIONS_COL] = int(re.compile(r'([0-9]+)').findall(cols[-3].text)[0])
	except:
		metro[STATIONS_COL] = None

	# length
	try:
		km_text = re.compile(r'([0-9\.]+.km)').findall(cols[-2].text)
		metro[LENGTH_COL] = float(re.compile(r'([0-9\.]+)').findall(km_text[0])[0])
	except:
		metro[LENGTH_COL] = None
		print cols[-2].text
		raise Exception

	# ridership
	try:
		metro[RIDERSHIP_COL] = int(float(cols[-1].text.split(' ')[0]) * 10**6)
	except:
		metro[RIDERSHIP_COL] = None

	# nLines
	# (we've got to go down one more link for this)


	return metro


starttime = time.time()
if __name__ == '__main__':
	jobs=[]

	metro_list = getMetroList()
	writeMetroList(metro_list)

	endtime=time.time()
	print endtime - starttime
