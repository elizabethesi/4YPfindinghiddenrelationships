
"""These 2 functions together remove the general trend of the composite function from the share price,
leaving one with the true value of that stock. The function is split into 2 functions as the composite only 
needs to be evaluated once for all the companies within that exchange, and so saves time. The functions combine
data collection by webscraping and the evaluation.""" 


#stock function updated:
#on yahoo finance some of the stocks have rows which are empty except for a repeated date and a
#divided ammount, this row needed to not be considered

def trendtakeawayfunction_composite(startdate, enddate, composite):
	import os
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

	from selenium import webdriver
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	from selenium.webdriver.common.keys import Keys



	start = dt.date(int(startdate[6:]), int(startdate[:2]), int(startdate[3:5])-1)
	end = dt.date(int(enddate[6:]), int(enddate[:2]), int(enddate[3:5])-1)
	#loads roughly 100 rows per full scroll to bottom = 100 business days
	days1 = np.busday_count( start, end )

	#had to update version of chromedriver
	chromedriver = "/Users/Esi/Downloads/chromedriver-2"
	os.environ["webdriver.chrome.driver"] = chromedriver
	driver = webdriver.Chrome(chromedriver)
	#wait to load, so new buttons appear
	wait = WebDriverWait(driver, 10)
	driver.get("https://finance.yahoo.com/quote/"+str(composite)+"/history?p="+str(composite))

	#open up date selection
	wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "svg[class^=Va][data-icon=CoreArrowDown]"))).click()
	#inputs the required start date
	item = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name=startDate]")))
	item.clear()
	item.send_keys(startdate)
	#inputs the required end date
	item = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name=endDate]")))
	item.clear()
	item.send_keys(enddate)
	#clicks the 'done' blue button
	wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-test=date-picker-menu] button[class*=Bgc]"))).click()
	#clicks the 'apply' blue button
	wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-reactid='25']"))).click()
	time.sleep(5)

	#AJAX issue only scrapes part of full table, rest of table has not loaded yet
	#scroll designated number of times for all table to be loaded 
	#int rounds down however all dates captured as the first 100 are already on screen
	for a in range(0, int(float(days1)/float(100))):
		driver.execute_script("window.scrollTo(0, 100000);")
		time.sleep(2)

	html = driver.page_source
	#parses the HTML
	soup = BeautifulSoup(html,"lxml")
	tables = soup.findChildren('table')
	


	my_table = tables[1]
	"""There are 7 columns Date -> Volume """
	list_of_all =[]
	#final rown line that includes a sentence this row should not be considered as returns a none type 
	num_rows = len(my_table.findAll('tr'))
	rows = my_table.findAll('tr')
	for a in range(0,(num_rows-1)):	
		row = rows[a]
		col = row.findAll('td')
		for cell in col:
			value = cell.string
			value = value.replace(',','')
			list_of_all.append(str(value))
	driver.quit()


	end = 7
	start = 0
	list_of_rows =[]
	for a in range(int(num_rows-2)):
		row = list_of_all[start:end]
		start += 7
		end += 7
		list_of_rows.append(row)

	
	count = 0
	for a in list_of_rows:
		date = dt.datetime.strptime(a[0],'%b %d %Y').date()
		list_of_rows[count][0] = date
		count += 1

	end_date = list_of_rows[0][0]
	list_of_rows = list(reversed(list_of_rows))
	start_date = list_of_rows[0][0]
	# print start_date
	# print end_date

	day_list = [start_date + dt.timedelta(days=x) for x in range((end_date-start_date).days +1)]
	d_and_p =[]
	for d in day_list:
		element = [d,0]
		d_and_p.append(element)

	#need to add in prices for weekends and national holidays as flights could still happen on these days
	for a in range(len(d_and_p)):
		day_of_week = d_and_p[a][0].strftime('%a')
		#closing price in index 4, close and adjusted close are the same
		for b in list_of_rows:
			day_b = b[0].strftime('%d')
			if d_and_p[a][0] == b[0]:
				d_and_p[a][1] = b[4]
			elif d_and_p[a][0] != b[0] and (day_of_week == 'Sat' or day_of_week == 'Sun'):
				#last known price value
				prev_price = d_and_p[a-1][1]
				d_and_p[a][1] = prev_price

	#other dates that were zeros can assume to be holidays (previously checked)
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

	days = len(d_and_p)
	# print days
	# print len(prices)
	# print " "
	#582 days

	###Linear Regression
	list_of_days = range(0,days)
	y_vec = np.asarray(prices)
	y_vec = y_vec[None,:]

	for a in range(days):
		list_of_days.append(1)
	B = np.array(list_of_days).reshape(2,days)

	B_tran = np.transpose(B)
	BB_tran = np.dot(B,B_tran)
	BB_tran_inverse = np.linalg.inv(BB_tran)
	B_tran_BB_tran_inverse = np.dot(B_tran,BB_tran_inverse)
	w = np.dot(y_vec, B_tran_BB_tran_inverse)
	y_of_line = np.dot(w,B)
	y_of_line = y_of_line.tolist()
	y_of_line = y_of_line[0]

	return end_date, prices, y_of_line
	#more efficient to split into 2 functions as the same y_of_line data will be used for 
	#multiple companies so do not want to keep recalling the same information

def trendtakeawayfunction_stock(startdate, enddate, stock, prices, y_of_line):
	import os
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

	from selenium import webdriver
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	from selenium.webdriver.common.keys import Keys



	start = dt.date(int(startdate[6:]), int(startdate[:2]), int(startdate[3:5])-1)
	end = dt.date(int(enddate[6:]), int(enddate[:2]), int(enddate[3:5])-1)
	
	days1 = np.busday_count( start, end )	
	
	chromedriver = "/Users/Esi/Downloads/chromedriver-2"
	os.environ["webdriver.chrome.driver"] = chromedriver
	driver = webdriver.Chrome(chromedriver)
	wait = WebDriverWait(driver, 10)
	driver.get("https://finance.yahoo.com/quote/"+str(stock)+"/history?p="+str(stock))

	wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "svg[class^=Va][data-icon=CoreArrowDown]"))).click()
	item = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name=startDate]")))
	item.clear()
	item.send_keys(startdate)
	item = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name=endDate]")))
	item.clear()
	item.send_keys(enddate)
	wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-test=date-picker-menu] button[class*=Bgc]"))).click()
	wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-reactid='25']"))).click()
	time.sleep(3)

	
	for a in range(0, int(float(days1)/float(100))):
		driver.execute_script("window.scrollTo(0, 100000);")
		time.sleep(4)

	html = driver.page_source
	soup = BeautifulSoup(html,"lxml")
	tables = soup.findChildren('table')
	# print tables[1]
	#AJAX issue only scrapes part of full table, rest of table has not loaded yet


	my_table = tables[1]
	"""There are 7 columns Date -> Volume """
	list_of_all =[]
	#dodgy final rown line that includes a sentence this row should not be considered
	#as returns a none type 
	num_rows = len(my_table.findAll('tr'))
	rows = my_table.findAll('tr')
	for a in range(0,(num_rows-1)):	
		row = rows[a]
		col = row.findAll('td')
		for cell in col:
			value = cell.string
			# print value
			list_of_all.append(str(value))
			
	driver.quit()

	indices =[]
	for index in range(len(list_of_all)):
		if list_of_all[index] == "None":
			i = index -1
			indices.append(i)
			indices.append(index)
	list_of_all_r = [i for j, i in enumerate(list_of_all) if j not in indices]	
	
	list_of_all =[]
	for a in list_of_all_r:
		value = a.replace(',','')
		list_of_all.append(str(value))



	end = 7
	start = 0
	list_of_rows =[]
	for a in range(len(list_of_all)/end):
		row = list_of_all[start:end]
		start += 7
		end += 7
		list_of_rows.append(row)

	
	count = 0
	for a in list_of_rows:
		date = dt.datetime.strptime(a[0],'%b %d %Y').date()
		list_of_rows[count][0] = date
		count += 1

	end_date = list_of_rows[0][0]	
	list_of_rows = list(reversed(list_of_rows))
	start_date = list_of_rows[0][0]
	print start_date
	print end_date


	day_list = [start_date + dt.timedelta(days=x) for x in range((end_date-start_date).days +1)]
	d_and_p =[]
	for d in day_list:
		element = [d,0]
		d_and_p.append(element)

	for a in range(len(d_and_p)):
		day_of_week = d_and_p[a][0].strftime('%a')
		#closing price in index 4, close and adjuusted close are the same
		for b in list_of_rows:
			day_b = b[0].strftime('%d')
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
	prices_dy = []
	for c in range(len(d_and_p)):
		val = float(d_and_p[c][1])
		d_and_p[c][1] = val
		prices_dy.append(val)

	#need to log and take away offset as both data sets are on a very different scale

	log_prices = np.log10(prices).tolist()
	log_line = np.log10(y_of_line).tolist()
	log_dy = np.log10(prices_dy).tolist()


	offset = -log_prices[0] + log_dy[0]
	log_line_offset =[]
	for value in log_line:
		a = value + offset
		log_line_offset.append(a)

	
	adjusted=[]
	days = len(y_of_line)
	# print len(log_dy)
	# print len(log_line_offset)
	for a in range(days):
		val = log_dy[a] - log_line_offset[a]
		adjusted.append(val)

	return adjusted	


	# Previously used to make graph depicted but not analysed for each company 

	#plot graph of NYSE prices against days
	# x = range(0,days)
	# plt.figure(figsize=(9,9))
	# plt.subplot(311)
	# plt.title('NYSE aggregate price')
	# plt.plot(x,prices, color='b', linewidth=1)
	# plt.plot(x,y_of_line, color='r', linewidth=1, label ='Linear')
	# # plt.plot(x,y_of_line_s, color='g', linewidth=1.5, label ='Square')
	# # plt.plot(x,y_of_line_c, color='m', linewidth=1.5, label ='Cubic')
	# # plt.legend()
	# plt.ylabel('Price in $')
	# plt.xlabel('Days')

	# # plt.subplot(412)
	# # plt.title('Log of NYSE aggregate price')
	# # plt.plot(x,log_prices, color='b', linewidth=1.5)
	# # plt.plot(x,log_line, color='r', linewidth=1.5, label ='Linear')
	# # plt.ylabel('Log price')
	# # plt.xlabel('Days')

	# plt.subplot(313)
	# plt.title('Adjusted Log ' +str(stock)+' price')
	# plt.plot(x,adjusted, color='k', linewidth=1.5, label ='Adjusted')
	# plt.ylabel('Log price')
	# plt.xlabel('Days')

	# plt.subplot(312)
	# plt.title('Log ' +str(stock)+ ' price')
	# plt.plot(x,log_dy, color='k', linewidth=1)
	# plt.plot(x,log_line_offset, color='r', linewidth=1, label ='Linear')
	# plt.ylabel('Log price')
	# plt.xlabel('Days')
	# plt.tight_layout()
	# plt.show()




