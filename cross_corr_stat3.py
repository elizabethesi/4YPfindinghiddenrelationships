"""Cross-correlation function. Using both pearson and Spearman."""

def cross_corr(x_prices, y_planes,stock, num ,vorp):
	import scipy.stats as sci
	import matplotlib.pyplot as plt
	import numpy as np
	from scipy.stats import gaussian_kde
	import scipy.stats as sci
	from scipy.stats import t
#list of numbers of lag positions
	lag_list = range(-(len(x_prices))+1, len(x_prices))	
	last = max(lag_list)
	#print lag_list
	#-490 -> 490
	#the y artcile can move 490 days to the left and 490 days to the right, maximum positions when only one day of 
	#overlap
	pear_corr=[]
	pear_p_values=[]
	spear_corr=[]
	spear_p_values=[]

	first = 1-last
	# print first
	# print last
	lag_range = range(first+150,last-150)


	for a in lag_range:
		#there need to be at least two days or move as otherwise the standard deviation of a single number is 0
		#the standard deviation is used in the denominator of the correlation coefficients and thus returns nan/inf
		#PROBLEM: The standard deviation would also be 0 if the values included were all the same -> STEVE: 
		#SHOULD I ADAPT MY FUNCTION FOR THIS although it is very unlikely that the first 2 or 3 prices or densities
		#are exactly the same?

		#planes sliding
		#first position lag -489, range of plane density [489:491] (just final data point) 
		#for prices just first [0:2], second position lag -488, range of plane [488:491] (
		# last 2 days), for prices first 2 days [0:3], when 0 lag is reached plane [0:491],
		#prices [0,491], lag 1 plane [0:490] and prices [1:491], last lag 489

		#when plane density to the left it is lagging, when to the right it is leading
		if a <= 0:
			price_sect = x_prices[0:(last + a +1)]
			plane_sect = y_planes[abs(a):(last+1)]
			pear = sci.pearsonr(price_sect, plane_sect)
			spear = sci.spearmanr(price_sect, plane_sect)
			days = len(price_sect)
			t_pear = float(pear[0] * np.sqrt(days-2))/float(np.sqrt(1-(pear[0]**2)))
			p_val_p = t.sf(np.abs(t_pear), (days-2))
			t_sp = float(spear[0] * np.sqrt(days-2))/float(np.sqrt(1-(spear[0]**2)))
			p_val_sp = t.sf(np.abs(t_sp), (days-2))
			pear_corr.append(pear[0])
			pear_p_values.append(np.log(p_val_p))
			spear_corr.append(spear[0])
			spear_p_values.append(np.log(p_val_sp))

		elif a > 0:
			price_sect = x_prices[a:(last+1)]
			plane_sect = y_planes[0:(last+1-a)]
			pear = sci.pearsonr(price_sect, plane_sect)
			spear = sci.spearmanr(price_sect, plane_sect)
			days = len(price_sect)
			t_pear = float(pear[0] * np.sqrt(days-2))/float(np.sqrt(1-(pear[0]**2)))
			p_val_p = t.sf(np.abs(t_pear), (days-2))
			t_sp = float(spear[0] * np.sqrt(days-2))/float(np.sqrt(1-(spear[0]**2)))
			p_val_sp = t.sf(np.abs(t_sp), (days-2))
			pear_corr.append(pear[0])
			pear_p_values.append(np.log(p_val_p))
			spear_corr.append(spear[0])
			spear_p_values.append(np.log(p_val_sp))

	#NUMPY.LOG		

	
	x =lag_range
	# f, (ax1,ax2,ax3) = plt.subplots(3)

	plt.figure(figsize=(15,9))
	plt.subplot(411)
	plt.title('Cross-correlation between stock '+str(vorp)+' and plane density  Company:' +str(stock)+ ' Plane:'+ str(num))
	plt.plot(x,pear_corr, color='b', linewidth=1.5, label ='Pearson')
	plt.plot(x,spear_corr, color ='r', linewidth=1.5, label='Spearman')
	plt.legend()
	axes1 = plt.gca()
	plt.ylabel('Correlation coefficients')
	plt.xlabel('Lag times /days')
	axes1.set_xlim([min(lag_list),last])
	axes1.set_ylim(-1,1)	

	plt.subplot(412)
	plt.plot(x,pear_p_values, color='b', linewidth=1.5)
	plt.plot(x,spear_p_values, color ='r', linewidth=1.5)	
	axes2 = plt.gca()
	plt.ylabel('Log of P values')
	plt.xlabel('Lag times /days')
	axes2.set_xlim([min(lag_list),last])
	
	xp = range(len(x_prices))
	# print len(x_for_p)
	# print len(x_prices)
	# print x_for_p
	plt.subplot(413)
	plt.plot(xp, x_prices, color ='black', linewidth=1.5)
	axes3 = plt.gca()
	plt.ylabel('Share ' +str(vorp), color ='black')
	plt.xlabel('Days')
	axes3.set_xlim(0,(len(x_prices)-1))
	
	
	plt.subplot(414)
	plt.plot(xp, y_planes, color ='green', linewidth=1.5)
	axes3 = plt.gca()
	plt.ylabel('Plane density', color ='green')
	plt.xlabel('Days')
	axes3.set_xlim(0,(len(y_planes)-1))
	
	# plt.savefig("Crosscorrfinal/"+str(stock)+"/"+str(vorp)+"_Crosscorr"+str(stock)+str(num)+".png")
	# plt.close()
	plt.show()
	
	
