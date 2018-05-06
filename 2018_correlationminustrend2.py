"""In use file which can be changed to call different functions"""



from organising_NYSE import dict_of_comp
from trendtakeawayfunction3 import trendtakeawayfunction_composite
from trendtakeawayfunction3 import trendtakeawayfunction_stock
from cross_corr_stat3 import cross_corr
from window_func import window
from granger_function4 import granger_function
from window_granger_func2 import window_granger_func

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

import pickle

def hinton(matrix, max_weight=None, ax=None):
		ax = ax if ax is not None else plt.gca()

		if not max_weight:
			max_weight = 2 ** np.ceil(np.log(np.abs(matrix).max()) / np.log(2))

		ax.patch.set_facecolor('gray')
		ax.set_aspect('equal', 'box')
		ax.xaxis.set_major_locator(plt.NullLocator())
		ax.yaxis.set_major_locator(plt.NullLocator())
		ax.set_ylabel('Order')
		ax.set_xlabel('Prices and Planes')

		for (x, y), w in np.ndenumerate(matrix):
			color = 'white' if w > 0 else 'black'
			size = np.sqrt(np.abs(w) / max_weight)
			rect = plt.Rectangle([x - size / 2, y - size / 2], size, size,facecolor=color, edgecolor=color)
			ax.add_patch(rect)

		ax.autoscale_view()
		ax.invert_yaxis()

order_list = [1,2,3,4,5,6,7,8]
#startdate can be discussed
startdate = "06/09/2016"
#returns from 8 June 2016 onwards (1 day before)
#BE AWARE THAT IF YOU CHANGE THIS TO A WEEKEND THE WEEKDAY AFTER IT WILL COME UP, WILL HAVE NO WAY OF
#KNOWING PREVIOUS DAY DATE -> only a problem if we want to call different sized windows, probably better
#to grab all info in one go 
#if end date chosen (ie today is a weekend) previous work day taken

#if looking at stock on NYSE -> have chosen the composite NYSE index (^NYA), other opptions such as NASDAQ, Dow Jones
#S&P 500 were considered
aggregate_url = "https://finance.yahoo.com/quote/^NYA/history?p=^NYA"
#when looking at a stock on the NASDAQ (they should provide a similar general trend as looking at a large number of stocks
#over a long period should depict general confidence levels of investors of stocks)
# aggregate_url = "https://finance.yahoo.com/quote/^IXIC/history?p=^IXIC"

#only want data up until yesterday as today has not yet closed (depending on time the code was executed)
now = dt.datetime.now() 
# enddate = now.strftime("%m/%d/%Y")

#for comparison with data collected for trend not taken away - last data poitn 18th of Jan
enddate ="03/28/2018"
#ends day before
print enddate
# end_date = (now - dt.timedelta(days=1)).date()
#end_date should be the last date in the yahoo finance table, just minusing one day from current day
#does not wor for weekends or holidays
# print end_date
# print" "
bandwidth = 0.05

end_date, prices, y_of_line = trendtakeawayfunction_composite(startdate, enddate, "^NYA")
print 'ENDDATE'
print end_date

for key in dict_of_comp:
	key = key.upper()
	key_name = key.upper()
	#the key holds the stock 
	#more efficient to get data for whole period and take away general trend then adjust number of days accordingly
	#WILL IT BE AN ISSUE THAT THE GENERAL TREND IS EVALUATED OVER A LONGER PERIOD THAN THE ACTUAL PLANE DATA UNDER 
	#CONSIDERATION??? -> thought that this is actually better as longer periods make pattern more general and better
	#follows a straight line

	# adj_log_price = trendtakeawayfunction(startdate, enddate, "^NYA", key)
	adj_log_price = trendtakeawayfunction_stock(startdate, enddate, key, prices, y_of_line)
	# output is a list of the adjusted log values of the share price
	
	days_log_p = len(adj_log_price)
	key = key.lower()

	#EXECUTE PLANE DATE DATA TO FIND START DATE

	#scraping plane dates
	final_combined = []
	list_pl = dict_of_comp[key]
	plane_dates_adsb ={}
	start_dates_ls =[]
	for plane in list_pl:
		page_url = "https://flight-data.adsbexchange.com/activity?inputSelect=registration&registration="+str(plane)
		print page_url
		page = requests.get(page_url).text
		# print page
		time.sleep(15)
		#lxml is the chosen parser for html for BeautifulSoup
		soup = BeautifulSoup(page, "lxml")
		#.dates is the class of the links in the html
		date_list_pl =[]
		for items in soup.select(".dates"):
			# print urljoin(page_url,items['href'])
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
	
	F_dict_adj ={}
	F_dict_pl ={}
	for pl_key in plane_dates_adsb:
		# print pl_key
		for dates_listed in plane_dates_adsb[pl_key]:
			start_date = min(dates_listed)
			# print start_date
			day_list = [start_date + dt.timedelta(days=x) for x in range((end_date-start_date).days +1)]
			print len(day_list)
			#cutting the length of days in the adjusted log price list
			days = len(day_list)
			diff = days_log_p - days
			# print diff
			adj_log_price_days = adj_log_price[diff:]
			# print " "
			# print len(adj_log_price_days)
			# print days

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
			# print len(planes)

			plane_pos =[]
			for b in range(days):
				index = b
				if planes[b] == 1:
					plane_pos.append(index)	
					final_combined.append(index)
			

			xs = np.linspace(0,(days-1),days)
			#print xs
			print len(xs)

			#KERNEL DENSITY ESTIMATION
			density = gaussian_kde(plane_pos)
			density.covariance_factor = lambda : bandwidth
			density._compute_covariance()
			density_p = density(xs)
			#removing days at end and beggining as they are not fully informed
			if bandwidth == 0.008:
				density_p = density_p[6:len(density_p)-6]
			elif bandwidth == 0.05:	
				density_p = density_p[30:len(density_p)-30]
			density_p = density_p.tolist()

			print adj_log_price_days
			max_p = max(adj_log_price_days)
			print max_p
			min_p = min(adj_log_price_days)
			print min_p
			diff = max_p-min_p
			prices= []
			for a in adj_log_price_days:
				price = float((a-min_p))/float(diff)
				prices.append(price)

			multi_p= np.array(prices, dtype=float)*1000
			multi_p.tolist()


			#need to make positions for price data inorder to apply same kernel density estimation
			#higher share price value more kernels added at this position
			positions =[]
			index = 0
			for a in multi_p:
				list_of_pos = [index]*int(a)
				positions.extend(list_of_pos)
				index += 1
			xs = np.linspace(0,(len(adj_log_price_days)-1),len(adj_log_price_days))
			densitypri = gaussian_kde(positions)
			densitypri.covariance_factor = lambda : bandwidth
			densitypri._compute_covariance()
			density_price = densitypri(xs)
			if bandwidth == 0.008:
				density_price = density_price[6:len(density_price)-6]
			elif bandwidth == 0.05:	
				density_price = density_price[30:len(density_price)-30]
			adj_prices = density_price.tolist()	

			# cross_corr(adj_prices, density_p,key, pl_key, "Price")
			# window(adj_prices, density_p, key ,pl_key,60)

			##added for granger
			F_val_lofl_adj=[]
			F_val_lofl_pl=[]
			p_value_list =[]
			for a in order_list:
				p_value_adj, p_value_pl = granger_function(adj_prices, density_p , a , key, pl_key)
				# F_Val_t1adj, F_Val_t1pl, sig5, sig1= window_granger_func(adj_prices, density_p , a , key, pl_key)
				# F_val_lofl_adj.append(F_Val_t1adj)
				# F_val_lofl_pl.append(F_Val_t1pl)
				# x = range(len(F_Val_t1adj))
				# plt.figure(figsize=(20,13))
				# plt.title('F values for each 60 day block determining in each window how beneficial to include the beta terms')
				# plt.plot(x,F_Val_t1adj, 'b^', label ='Adjusted Prices')
				# plt.plot(x,F_Val_t1pl, 'r^', label='Plane Density')
				# plt.axhline(y=sig5, color='g', linestyle='-', label= "Significance Level 5%")
				# plt.axhline(y=sig1, color='y', linestyle='-', label= "Significance Level 1%")
				# plt.legend()
				# plt.ylabel('F values for F test')
				# plt.xlabel('60 Day Blocks')
				# plt.savefig("Windowgrangerfinal/"+str(key)+"/"+str(a)+"/order"+str(a)+"FVal_for_every_2m"+"Com"+str(key)+"_Pl"+str(pl_key)+".png")
				# plt.close()
				p_value_list.append(p_value_adj)
				p_value_list.append(p_value_pl)
			# print "P Value List"	
			# print p_value_list
			P_Val = np.array(p_value_list).reshape(len(order_list),2)
			P_Val_t = np.transpose(P_Val)
			hinton(P_Val_t)
			plt.savefig("Grangerfinal/"+str(key)+"/P_value_of_F_test"+"Com"+str(key)+"_Pl"+str(pl_key)+".png")
			plt.close()
			# F_dict_adj[str(pl_key)] = F_val_lofl_adj
			# F_dict_pl[str(pl_key)] = F_val_lofl_pl

	#FOR COMBINING ALL PLANES
	if len(plane_dates_adsb) >1:
		start_date_all = max(start_dates_ls)
		day_list_all = [start_date_all + dt.timedelta(days=x) for x in range((end_date-start_date_all).days +1)]
		# print day_list_all
		days_for_planes = len(day_list_all)
		diff_all = days_log_p - days_for_planes
		adj_log_price_days_pl = adj_log_price[diff_all:]

		
		#COMPARISON OF DAY_LIST AND WHEN PLANES FLEW 
		#place a one in a list if the lists match
		#key_pl is the N-number
		
		# print date_list_pl_all
		plane_pos_all =[]
		#for each plane
		for key_pl in plane_dates_adsb:
			date_list_pl_all = plane_dates_adsb[key_pl]
			# print plane_dates_adsb[key_pl]
			planes = [0] * days_for_planes
			
			count = 0
			for date in day_list_all:
				for date_pl in date_list_pl_all:
					for each_date in date_pl:
						if date == each_date:
							# print each_date
							planes[count] = 1
				count += 1
				
				#want plane positions to range from 0-3 for dycom
				#3 if all planes flew on that day
			n_number_keys = plane_dates_adsb.keys()
			num_of_planes = len(n_number_keys)
			for b in range(days_for_planes):
				#index refers to the day position of the flight this is needed to calculate the kernel density 
				index = b
				#want to achieve this for any number of planes (dycom has/had 3)
				# if planes[b] == 1:
				# 	plane_pos_all.append(index)	
				# elif planes[b] ==2:
				# 	plane_pos_all.append(index)
				# 	plane_pos_all.append(index)
				# elif planes[b] ==3:
				# 	plane_pos_all.append(index)
				# 	plane_pos_all.append(index)
				# 	plane_pos_all.append(index)	

				#if all 3 planes flew on one day the day position would be entered 3 times	
				#this will only be 1 not neccessary but not incorrect 
				for a in range(1, num_of_planes):
					if planes[b] == a:
						l = [index]*a
						plane_pos_all.extend(l)	

		print len(plane_pos_all)
		
		xs = np.linspace(0,(days_for_planes-1),days_for_planes)
		#print xs
		# print len(xs)

		density = gaussian_kde(plane_pos_all)
		density.covariance_factor = lambda : bandwidth
		density._compute_covariance()
		density_p_all = density(xs)
		if bandwidth == 0.008:
			density_p_all = density_p_all[6:len(density_p_all)-6]
		elif bandwidth == 0.05:	
			density_p_all = density_p_all[30:len(density_p_all)-30]
		density_p_all = density_p_all.tolist()
		
		

		max_p = max(adj_log_price_days_pl)
		min_p = min(adj_log_price_days_pl)
		diff = max_p-min_p
		prices= []
		for a in adj_log_price_days_pl:
			price = float((a-min_p))/float(diff)
			prices.append(price)

		multi_p= np.array(prices, dtype=float)*1000
		multi_p.tolist()


		positions =[]
		index = 0
		for a in multi_p:
			list_of_pos = [index]*int(a)
			positions.extend(list_of_pos)
			index += 1
		xs = np.linspace(0,(len(adj_log_price_days_pl)-1),len(adj_log_price_days_pl))
		densitypri = gaussian_kde(positions)
		densitypri.covariance_factor = lambda : bandwidth
		densitypri._compute_covariance()
		density_price = densitypri(xs)
		if bandwidth == 0.008:
			density_price = density_price[6:len(density_price)-6]
		elif bandwidth == 0.05:	
			density_price = density_price[30:len(density_price)-30]
		adj_prices_all = density_price.tolist()	
		

		# cross_corr(adj_prices_all, density_p_all,key, 'ALL', "Prices")
		# window(adj_prices_all,density_p_all,key,"ALL",60)
		##added for granger test
		F_val_lofl_adj=[]
		F_val_lofl_pl=[]
		p_value_list =[]	
		for a in order_list:
			p_value_adj, p_value_pl = granger_function(adj_prices_all, density_p_all , a , key,'ALL')
			# F_Val_t1adj, F_Val_t1pl, sig5, sig1= window_granger_func(adj_prices_all, density_p_all , a , key, 'ALL')
			# F_val_lofl_adj.append(F_Val_t1adj)
			# F_val_lofl_pl.append(F_Val_t1pl)
			# x = range(len(F_Val_t1adj))
			# plt.figure(figsize=(20,13))
			# plt.title('F values for each 60 day block determining in each window how beneficial to include the beta terms')
			# plt.plot(x,F_Val_t1adj, 'b^', label ='Adjusted Prices')
			# plt.plot(x,F_Val_t1pl, 'r^', label='Plane Density')
			# plt.axhline(y=sig5, color='g', linestyle='-', label= "Significance Level 5%")
			# plt.axhline(y=sig1, color='y', linestyle='-', label= "Significance Level 1%")
			# plt.legend()
			# plt.ylabel('F values for F test')
			# plt.xlabel('60 Day Blocks')
			# plt.savefig("Windowgrangerfinal/"+str(key)+"/"+str(a)+"/order"+str(a)+"FVal_for_every_2m"+"Com"+str(key)+"_PlALL.png")
			# plt.close()
			p_value_list.append(p_value_adj)
			p_value_list.append(p_value_pl)
		P_Val = np.array(p_value_list).reshape(len(order_list),2)
		P_Val_t = np.transpose(P_Val)
		hinton(P_Val_t)
		plt.savefig("Grangerfinal/"+str(key)+"/P_value_of_F_test"+"Com"+str(key)+"ALL.png")
		plt.close()	
		# F_dict_adj['ALL'] = F_val_lofl_adj
		# F_dict_pl['ALL'] = F_val_lofl_pl
	# print " "
	# print " "
	# print " "
	# print " "	
	# print F_dict_adj
	# print F_dict_pl
	# f= open("Windowgrangerfinal/"+str(key)+"/fvaluesprices.pkl","w+")
	# pickle.dump(F_dict_adj, f, pickle.HIGHEST_PROTOCOL)
	# f.close()
	# g= open("Windowgrangerfinal/"+str(key)+"/fvaluesplanes.pkl","w+")
	# pickle.dump(F_dict_pl, g, pickle.HIGHEST_PROTOCOL)
	# f.close()
	
