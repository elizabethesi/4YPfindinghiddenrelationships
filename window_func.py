"""Assesses the correlation within windowed periods of a set length of 'days'"""

def window(adj_price, density_p, key ,pl_key, days):
	import scipy.stats as sci
	import matplotlib.pyplot as plt
	import numpy as np
	from scipy.stats import t

	pear_corr=[]
	pear_p_values=[]
	spear_corr=[]
	spear_p_values=[]

	#for each window evaluate the pearson and spearman correlation coefficients
	#and their corresponding p-values

	for a in range(len(adj_price)):
		start = a
		end = a + days
		if end <= (len(adj_price)-1):
			adj_pricesub = adj_price[start:end]
			density_psub = density_p[start:end]
			pear = sci.pearsonr(adj_pricesub,density_psub)
			spear = sci.spearmanr(adj_pricesub,density_psub)
			t_pear = float(pear[0] * np.sqrt(days-2))/float(np.sqrt(1-(pear[0]**2)))
			p_val_p = t.sf(np.abs(t_pear), (days-2))
			t_sp = float(spear[0] * np.sqrt(days-2))/float(np.sqrt(1-(spear[0]**2)))
			p_val_sp = t.sf(np.abs(t_sp), (days-2))
			pear_corr.append(pear[0])
			pear_p_values.append(np.log(p_val_p))
			spear_corr.append(spear[0])
			spear_p_values.append(np.log(p_val_sp))

		

	#graph that displays this information for each plane and saves it 
	x = range(0, len(pear_corr))
	plt.figure(figsize=(15,9))
	plt.subplot(411)
	plt.title('Rolling Window Correlation of '+str(days)+' Days Between Stock Price and Logged Plane Density  Company:' +str(key)+ ' Plane:'+ str(pl_key))
	plt.plot(x,pear_corr, color='b', linewidth=1.5, label ='Pearson')
	plt.plot(x,spear_corr, color ='r', linewidth=1.5, label='Spearman')
	plt.legend()
	plt.ylabel('Correlation coefficients')
	plt.xlabel('Start Day of '+str(days)+' Day Windows')

	plt.subplot(412)
	plt.plot(x,pear_p_values, color='b', linewidth=1.5)
	plt.plot(x,spear_p_values, color ='r', linewidth=1.5)	
	plt.ylabel('Log of P values')
	plt.xlabel('Start Day of '+str(days)+' Day Windows')

	
	xp = range(len(adj_price))
	plt.subplot(413)
	plt.plot(xp, adj_price, color ='black', linewidth=1.5)
	axes3 = plt.gca()
	plt.ylabel('Share Price' , color ='black')
	plt.xlabel('Days')
	
	
	plt.subplot(414)
	plt.plot(xp, density_p, color ='green', linewidth=1.5)
	axes3 = plt.gca()
	plt.ylabel('Plane Density', color ='green')
	plt.xlabel('Days')

	plt.tight_layout()
	
	plt.show()
	plt.savefig("WindowFunctionFinal/"+str(key)+"/LOGWindow"+str(days)+"days"+str(pl_key)+".png")
	# plt.close()	

	return pear_p_values	
			