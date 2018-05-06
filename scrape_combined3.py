"""
Old file included to demonstrate scraping from the NASDAQ website.
This has since been modified and improved.
"""

from organising_NYSE import dict_of_comp
from cross_corr_stat2 import cross_corr
from cross_corr_stat2 import cross_corr_all
from window_func import window

import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from urlparse import urljoin
import requests
import time
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
import scipy.stats as sci

#LOOK AT VOLUME
#FIX SITUATION IF WEBSITE CRASHES

#THINK ABOT HOW TO COMBINE DENSITIES

#nike has 2 planes
#[['NIKE'], 'N1972N', ['NIKE'], 'NKE']
#[['NIKE'], 'N3546', ['NIKE'], 'NKE']


#FOR STOCK PRICE DATA from NASDAQ website

for key in dict_of_comp:
	chromedriver = "/Users/Esi/Downloads/chromedriver-2"
	os.environ["webdriver.chrome.driver"] = chromedriver
	driver = webdriver.Chrome(chromedriver)
	url = 'http://www.nasdaq.com/symbol/'+str(key)+'/historical'
	print url
	driver.get(url)
	select = Select(driver.find_element_by_id('ddlTimeFrame'))
	#want to see historical information for 2 years
	select.select_by_value("2y")
	#need to wait for webpage to be fully refreshed for the 2 years before using beautifulsoup
	time.sleep(10)
	html = driver.page_source
	soup = BeautifulSoup(html,"lxml")

	tables = soup.findChildren('table')
	print tables
	#stock information in table indexed 5
	#print tables[5]
	my_table = tables[5]

	"""There are 6 columns Date -> Volume 
	Be careful of first row in html as incorrect when markets are closed and not printed on screen
	When markets open first row on screen does not have a date it has a time, should not be included """
	rows = my_table.findChildren(['th', 'tr'])

	list_of_all =[]
	for row in rows:
		cells = row.findChildren('td')
		for cell in cells:
			value = cell.string
			list_of_all.append(str(value.strip()))

	# print list_of_all
	num_rows = float(len(list_of_all))/float(6)	
	# print num_rows	

	driver.quit()

	end = 6
	start = 0
	list_of_rows =[]
	for a in range(int(num_rows)):
		row = list_of_all[start:end]
		start += 6
		end += 6
		list_of_rows.append(row)

	# print list_of_rows[0:2]
	# print" "
	#will either be from 1 or 2 depending what is returned when used during working hourss
	list_of_rows = list_of_rows[2:]


	count = 0
	for a in list_of_rows:
		date = dt.datetime.strptime(a[0],'%m/%d/%Y').date()
		list_of_rows[count][0] = date
		count += 1

	end_date = list_of_rows[0][0]	
	list_of_rows = list(reversed(list_of_rows))
	#print list_of_rows


	#EXECUTE PLANE DATE DATA TO FIND START DATE

	#append all plane positions to final_combined
	# final_combined = []
	list_pl = dict_of_comp[key]
	plane_dates_adsb ={}
	start_dates_ls =[]
	for plane in list_pl:
		page_url = "https://flight-data.adsbexchange.com/activity?inputSelect=registration&registration="+str(plane)
		print page_url
		page = requests.get(page_url).text
		time.sleep(15)
		soup = BeautifulSoup(page, "lxml")
		#.dates is the class of the links in the html
		date_list_pl =[]
		for items in soup.select(".dates"):
			# print(urljoin(page_url,items['href']))
			a = urljoin(page_url,items['href'])
			date1 = a[-10:]
			date = dt.datetime.strptime(date1,'%Y-%m-%d').date()
			date_list_pl.append(date)

		#if only 1 data point no correlation 
		if len(date_list_pl)> 1:	
			start_date = date_list_pl[-1]
			date_list_pl = list(reversed(date_list_pl))
			start_dates_ls.append(start_date)
			key_pl = plane
			plane_dates_adsb.setdefault(key_pl, [])
			plane_dates_adsb[key_pl].append(date_list_pl)
		else:
			print 'This plane does not have dates (or has only one date)'
			print " "
			print plane
			continue

	for pl_key in plane_dates_adsb:
		# print pl_key
		for dates_listed in plane_dates_adsb[pl_key]:
			start_date = min(dates_listed)
			print start_date
			print end_date
			day_list = [start_date + dt.timedelta(days=x) for x in range((end_date-start_date).days +1)]
			d_and_p =[]
			for d in day_list:
				element = [d,0]
				d_and_p.append(element)

			for a in range(len(d_and_p)):
				day_of_week = d_and_p[a][0].strftime('%a')
				for b in list_of_rows:
					# day_b = b[0].strftime('%d')
					if d_and_p[a][0] == b[0]:
						d_and_p[a][1] = b[4]
					elif d_and_p[a][0] != b[0] and (day_of_week == 'Sat' or day_of_week == 'Sun'):
						#last known price value
						prev_price = d_and_p[a-1][1]
						d_and_p[a][1] = prev_price

			#other dates that were zeros were all holidays -> checked https://www.nyse.com/markets/hours-calendars
			for e in range(len(d_and_p)):
				if d_and_p[e][1] == 0:
					prev_price2 = d_and_p[e-1][1]		
					d_and_p[e][1] = prev_price2


			#here the prices are floating numbers -> important for plotting
			prices = []
			for c in range(len(d_and_p)):
				val = float(d_and_p[c][1])
				d_and_p[c][1] = val
				prices.append(val)

			# print prices	

			days = len(d_and_p)
			print days
			#519 days

			#COMPARISON OF DAY_LIST AND WHEN PLANES FLEW 
			#place a one in a list if the lists match 
			planes = [0] * days
			count = 0
			for date in day_list:
				for date_pl in dates_listed:
					if date == date_pl:
						planes[count] = 1
				count += 1

			# print planes			
			print len(planes)

			plane_pos =[]
			for b in range(days):
				index = b
				if planes[b] == 1:
					plane_pos.append(index)	
					# final_combined.append(index)		

			xs = np.linspace(0,(days-1),days)
			#print xs
			#print len(xs)

			density = gaussian_kde(plane_pos)
			density.covariance_factor = lambda : .05
			density._compute_covariance()
			density_p = density(xs)
			# print density_p

			cross_corr(prices, density_p,key, pl_key, "Price")
			# window(prices,density_p,key, pl_key ,"Price", 1)
			



	#FOR COMBINING ALL PLANES
	if len(plane_dates_adsb) >1:
		start_date_all = max(start_dates_ls)
		day_list_all = [start_date_all + dt.timedelta(days=x) for x in range((end_date-start_date_all).days +1)]
		d_and_p =[]
		for d in day_list_all:
			element = [d,0]
			d_and_p.append(element)

		for a in range(len(d_and_p)):
			day_of_week = d_and_p[a][0].strftime('%a')
			for b in list_of_rows:
				# day_b = b[0].strftime('%d')
				if d_and_p[a][0] == b[0]:
					d_and_p[a][1] = b[4]
				elif d_and_p[a][0] != b[0] and (day_of_week == 'Sat' or day_of_week == 'Sun'):
					#last known price value
					prev_price = d_and_p[a-1][1]
					d_and_p[a][1] = prev_price

		#other dates that were zeros were all holidays -> checked https://www.nyse.com/markets/hours-calendars
		for e in range(len(d_and_p)):
			if d_and_p[e][1] == 0:
				prev_price2 = d_and_p[e-1][1]		
				d_and_p[e][1] = prev_price2


		#here the prices are floating numbers -> important for plotting
		prices = []
		for c in range(len(d_and_p)):
			val = float(d_and_p[c][1])
			d_and_p[c][1] = val
			prices.append(val)

		# print prices	

		days = len(d_and_p)
		print days
		
		#COMPARISON OF DAY_LIST AND WHEN PLANES FLEW 
		#place a one in a list if the lists match
		#key_pl is the N-number
		
		# print date_list_pl_all
		plane_pos_all =[]
		planes = [0] * days
		for key_pl in plane_dates_adsb:
			print "!!!"
			date_list_pl_all = plane_dates_adsb[key_pl]
			print plane_dates_adsb[key_pl]
			
			count = 0
			for date in day_list_all:
				for date_pl in date_list_pl_all:
					for each_date in date_pl:
						if date == each_date:
							# print each_date
							planes[count] += 1
				count += 1
				###IMPORTANT TO NOTE THE MAX FOR ANY DAY IS 1 -> this shows did any of them 
				#fly today -> maybe should look at making it 0-3
			for b in range(days):
				index = b
				if planes[b] == 1:
					plane_pos_all.append(index)	
					# final_combined.append(index)
				elif planes[b] == 2:
					plane_pos_all.append(index)
					plane_pos_all.append(index)
				elif planes[b] ==3:
					plane_pos_all.append(index)
					plane_pos_all.append(index)
					plane_pos_all.append(index)		

		print planes
		print" "
		print plane_pos_all			
		print len(plane_pos_all)

		xs = np.linspace(0,(days-1),days)
		#print xs
		# print len(xs)

		density = gaussian_kde(plane_pos_all)
		density.covariance_factor = lambda : .05
		density._compute_covariance()
		density_p_all = density(xs)
				# print density_p

		cross_corr_all(prices, density_p_all,key, 'ALL', "Price")
		# window(prices,density_p_all,key,"ALL" ,"Price", 1)

			

		
