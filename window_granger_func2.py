
"""Windowed assessment of Granger causality. Extra variables returned so that they can be saved 
and used to compute the 3D graphs in F_values."""





def window_granger_func(adj_prices, density_plane_log, order_num , stock, pl_key):
	import matplotlib.pyplot as plt
	import scipy.stats as sci
	from scipy.stats import gaussian_kde
	import numpy as np
	import time
	
	key_name = stock.upper()
	order = order_num
	F_Val_t1adj =[]
	F_Val_t1pl =[]
	
	# density_plane_log = planes.tolist()
	#Feature standardisation - remove the mean and divide by standard deviation 
	def mean_and_sd(data):
		mean = float(sum(data))/float(len(data))

		squares = []
		for a in data:
			b = a - mean
			square_b = b**2
			squares.append(square_b)
		variance = float((sum(squares))/float(len(data) -1))

		sd = variance**0.5

		return mean, sd

	mean_pl, sd_pl = mean_and_sd(density_plane_log)
	mean_pri, sd_pri = mean_and_sd(adj_prices)

	den_plane_log_stan_full = []
	for a in density_plane_log:
		b = float(a-mean_pl)/float(sd_pl)
		den_plane_log_stan_full.append(b)

	adj_pri_stan_full = []
	for a in adj_prices:
		b = float(a-mean_pri)/float(sd_pri)
		adj_pri_stan_full.append(b)	

	#this window goes through every 60 day section first section starting at day 0 ending day 59
	#second starting day 1 ending day 60
	for a in range(len(adj_pri_stan_full)):
		start = a
		end = a + 60
		#ends when end of window reaches end of data
		if end <= (len(adj_pri_stan_full)-1):
			adj_pri_stan = adj_pri_stan_full[start:end]
			den_plane_log_stan = den_plane_log_stan_full[start:end]
			number_of_data_points = len(adj_pri_stan)
			#the max number of rows in the X matrix for order 1 would be nodp - order
			rows = number_of_data_points - order
			#X matrix is (rows x 2) as there are 2 data sets, column one: adj_log column two: density_plane_log
			#starts at index of order and finishes at index of number_of_data_points -1
			list_of_x = []
			for a in range(order,number_of_data_points):
				list_of_x.append(adj_pri_stan[a])
				list_of_x.append(den_plane_log_stan[a])

			X = np.array(list_of_x).reshape(rows,2)
			# print X
			# print ' '


			#M matrix is (rows x (2*order))
			list_of_M =[]
			for row in range(rows):
				t = row + order
				single_row =[]
				for a in range(1,order+1):
					t_minus = t - a
					single_row.append(adj_pri_stan[t_minus])
					single_row.append(den_plane_log_stan[t_minus])
				list_of_M.extend(single_row)	

			columns = 2*order	
			# print len(list_of_M)
			# print rows*columns
			M = np.array(list_of_M).reshape(rows,columns)
			# print M
			# print " "

			# M_tran = np.transpose(M)
			# MtranM = np.dot(M_tran,M)
			# MtranM_inverse = np.linalg.inv(MtranM)
			# MtranM_inverseMtran = np.dot(MtranM_inverse,M_tran)

			MtranM_inverseMtran = np.linalg.pinv(M)
			a_hat = np.dot(MtranM_inverseMtran, X)

			# print"AHAT"
			#ahat has dimension of (2*order x 2)
			# print a_hat
			# print a_hat.shape

			# print "A HAT SQUARE"
			a_hat_sq = a_hat**2
			# print a_hat_sq

			# print 'M'
			# print M.shape
			#plot graphs of the lists of X produced to show how well the model fits
			x_model = np.dot(M,a_hat)
			# print x_model
			# print x_model.shape

			x_model = x_model.tolist()
			#breaks it down into list of rows
			model_adj =[]
			model_pl =[]
			for row in x_model:
				model_adj.append(row[0])
				model_pl.append(row[1])

			# print x_model[1:4]

			# print" "
			# print model_adj[1:4]

			# print model_pl[1:4]

			actual_adj_stan = adj_pri_stan[order:]
			actual_pl_stan = den_plane_log_stan[order:]
			#same number of rows different number of columns
			X_adj = np.array(actual_adj_stan).reshape(rows,1)
			X_pl = np.array(actual_pl_stan).reshape(rows,1)
			dof = rows - (2*order)

			
			
			H = np.dot(M,MtranM_inverseMtran)
			I = np.identity(rows)
			minus = I - H
			X_tran_adj = np.transpose(X_adj)
			X_tran_adjminus = np.dot(X_tran_adj,minus)
			a = np.dot(minus,X_adj)
			SSE_adj = np.dot(X_tran_adjminus,X_adj)
			MSE_adj = SSE_adj/dof
			MSE_adj = abs(MSE_adj[0,0])
			M_tran = np.transpose(M)
			MtranM = np.dot(M_tran,M)
			MtranM_inverse = np.linalg.inv(MtranM)
			# MtranM_inverseMtran = np.dot(MtranM_inverse,M_tran)


			C_adj = MSE_adj*MtranM_inverse
			list_of_se_adj =[]
			for a in range(0,2*order):
				val = abs(C_adj[a,a])
				if val >=0:
					list_of_se_adj.append(val**0.5)
					stock1a = stock
				else:
					print "ISSUE"
					print MSE_adj

					print val
					list_of_se_adj.append(val**0.5)	
					stock1a = 'PROB_adj'
			beta_adj = a_hat[:,0]
			t_adj = beta_adj/list_of_se_adj
			p_adj =[]
			for a in t_adj:
				if a >= 0:
					p_adj_el= sci.t.sf(a,dof)*2
				elif a < 0:
					p_adj_el= sci.t.cdf(a,dof)*2
				p_adj.append(p_adj_el)


			X_tran_pl = np.transpose(X_pl)
			X_tran_plminus = np.dot(X_tran_pl,minus)
			SSE_pl = np.dot(X_tran_plminus,X_pl)
			MSE_pl = SSE_pl/dof
			MSE_pl = abs(MSE_pl[0,0])
			C_pl = MSE_pl*MtranM_inverse
			list_of_se_pl =[]
			for a in range(0,2*order):
				val = abs(C_pl[a,a])
				if val >=0:
					list_of_se_pl.append(val**0.5)
					stock1 = stock1a
				else:
					list_of_se_pl.append(0)	
					stock1 = stock1a + 'PROB_pl'
			beta_pl = a_hat[:,1]	
			t_pl= beta_pl/list_of_se_pl
			t_pl = t_pl.tolist()
			p_pl =[]
			for a in t_pl:
				if a >= 0:
					p_pl_el= sci.t.sf(a,dof)*2
				elif a < 0:
					p_pl_el= sci.t.cdf(a,dof)*2
				p_pl.append(p_pl_el)


			p_val =[]
			for a in range(len(p_adj)):
				p_val.append(p_adj[a])
				p_val.append(p_pl[a])
			p_values_matrix = np.array(p_val).reshape(2*order,2)
			# print p_values_matrix
			
			def hinton(matrix, max_weight=None, ax=None):
					ax = ax if ax is not None else plt.gca()

					if not max_weight:
						max_weight = 2 ** np.ceil(np.log(np.abs(matrix).max()) / np.log(2))

					ax.patch.set_facecolor('gray')
					ax.set_aspect('equal', 'box')
					ax.xaxis.set_major_locator(plt.NullLocator())
					ax.yaxis.set_major_locator(plt.NullLocator())
					ax.set_ylabel('P values')

					for (x, y), w in np.ndenumerate(matrix):
						color = 'white' if w > 0 else 'black'
						size = np.sqrt(np.abs(w) / max_weight)
						rect = plt.Rectangle([x - size / 2, y - size / 2], size, size,facecolor=color, edgecolor=color)
						ax.add_patch(rect)

					ax.autoscale_view()
					ax.invert_yaxis()
				


			p_val_t =np.transpose(p_values_matrix)
			hinton(p_val_t, max_weight=1)
			plt.savefig("Windowgrangerfinal/"+str(key_name)+"/"+str(order_num)+"/T_test_start"+str(start)+"Order"+str(order_num)+"Com"+str(stock1)+"_Pl"+str(pl_key)+".png")
			plt.close()

			actual_adj_stan = adj_pri_stan[order:]
			actual_pl_stan = den_plane_log_stan[order:]
			#same number of rows different number of columns
			X_adj = np.array(actual_adj_stan).reshape(rows,1)
			X_pl = np.array(actual_pl_stan).reshape(rows,1)

			#M matrices are (rows x order)
			list_of_M_adj =[]
			list_of_M_pl =[]
			for row in range(rows):
				#takes into account of where we are starting from order
				t = row + order
				single_row_adj =[]
				single_row_pl =[]
				for a in range(1,order+1):
					t_minus = t - a
					single_row_adj.append(adj_pri_stan[t_minus])
					single_row_pl.append(den_plane_log_stan[t_minus])
				list_of_M_adj.extend(single_row_adj)
				list_of_M_pl.extend(single_row_pl)	

			# print len(list_of_M)
			M_adj = np.array(list_of_M_adj).reshape(rows,order)
			M_pl = np.array(list_of_M_pl).reshape(rows,order)
			# print M
			# print " "

			MtranM_inverseMtran_adj = np.linalg.pinv(M_adj)
			a_hat_adj = np.dot(MtranM_inverseMtran_adj, X_adj)
			x_model_adj = np.dot(M_adj,a_hat_adj)
			x_model_adj = x_model_adj.tolist()
			Resmodel_adj=[]
			for row in x_model_adj:
				Resmodel_adj.append(row[0])


			MtranM_inverseMtran_pl = np.linalg.pinv(M_pl)
			a_hat_pl = np.dot(MtranM_inverseMtran_pl, X_pl)
			x_model_pl = np.dot(M_pl,a_hat_pl)
			x_model_pl = x_model_pl.tolist()
			Resmodel_pl=[]
			for row in x_model_pl:
				Resmodel_pl.append(row[0])

			#RRSS restricted model's residual sum of squares
			RRSS_adj =0
			RRSS_pl =0
			for index in range(0,len(Resmodel_adj)):
				square_residuals_adj = (Resmodel_adj[index] - actual_adj_stan[index])**2
				square_residuals_pl = (Resmodel_pl[index] - actual_pl_stan[index])**2
				RRSS_adj += square_residuals_adj
				RRSS_pl += square_residuals_pl

			#sample size, T
			T = len(model_adj)

			#number of explanatory variables in the unrestricted regression, k
			#as mean is 0 (no constant), k = number of rows in a_hat 
			k = 2*order

			#number of restrictions in place, q  
			#in this test all beta coefficients are 0 for the null hypothesis
			q = order

			#unrestricted models's residual sum of squares
			URSS_adj = 0
			URSS_pl = 0
			for index in range(0,len(model_adj)):
				square_residuals_adj = (model_adj[index] - actual_adj_stan[index])**2
				square_residuals_pl = (model_pl[index] - actual_pl_stan[index])**2
				URSS_adj += square_residuals_adj
				URSS_pl += square_residuals_pl

			# print str(pl_key)+': '+str(order_num)+': ' + str(start)

			# to check that these are all correct with relation to graph
			# print 'actual_adj_stan[10:20]'
			# print actual_adj_stan[10:20]
			# print 'Resmodel_adj[10:20]'
			# print Resmodel_adj[10:20]
			# print 'model_adj[10:20]'
			# print model_adj[10:20]
			# print' '

			df2 = T-k	

			part_adj = float(RRSS_adj - URSS_adj)/float(URSS_adj)
			F_adj = part_adj * (float(T-k)/float(q))
			p_value_adj = sci.f.sf(F_adj, q, df2)
			# F_Val_t1adj.append(F_adj)

			part_pl = float(RRSS_pl - URSS_pl)/float(URSS_pl)
			F_pl = part_pl * (float(T-k)/float(q))
			p_value_pl = sci.f.sf(F_pl, q, df2)
			# F_Val_t1pl.append(F_pl)

			sig5 = sci.f.ppf(1-0.05, q, df2)
			sig1 = sci.f.ppf(1-0.01, q, df2)


			# #NEW FOR BIG GRAPH ONLY SHOWING ABOVE SIGNIFICANCE
			if F_adj >= sig1:
				F_Val_t1adj.append(F_adj)
			else:
				F_Val_t1adj.append(0)

			if F_pl >= sig1:
				F_Val_t1pl.append(F_pl)
			else:
				F_Val_t1pl.append(0)

			# print"F adj"
			# print F_adj
			# print " p val adj"
			# print p_value_adj
			# print "F pl"
			# print F_pl
			# print "p val pl"
			# print p_value_pl



			#want to plot the x results of the order
			x_a = range(order, len(den_plane_log_stan))	


			plt.figure(figsize=(20,13))
			plt.subplot(211)
			plt.title('Order:'+str(order_num)+' showing how Mdota_hat fits to real data Comp:'+str(stock)+" Pl:"+str(pl_key))
			plt.plot(x_a, adj_pri_stan[order:], color ='b', linewidth=0.5, label = "Original")
			plt.plot(x_a,model_adj, color ='g', linewidth=0.5, label = "Unrestricted")
			plt.plot(x_a,Resmodel_adj, color ='r', linewidth=0.5, label = "Restricted")
			plt.legend()
			plt.ylabel('Adjusted share price')
			plt.xlabel('Days')

			plt.subplot(212)
			plt.plot(x_a,den_plane_log_stan[order:], color ='b', linewidth=0.5)
			plt.plot(x_a, model_pl, color='g', linewidth=0.5)
			plt.plot(x_a,Resmodel_pl, color ='r', linewidth=0.5)
			plt.ylabel('Log density planes')
			plt.xlabel('Days')

			plt.savefig("Windowgrangerfinal/"+str(key_name)+"/"+str(order_num)+"/Start"+str(start)+"Order"+str(order_num)+"Com"+str(stock)+"_Pl"+str(pl_key)+".png")
			plt.close()

			#want to square the values of a_hat and put into a hinton diagram
			def hinton(matrix, max_weight=None, ax=None):
				ax = ax if ax is not None else plt.gca()

				if not max_weight:
					max_weight = 2 ** np.ceil(np.log(np.abs(matrix).max()) / np.log(2))

				ax.patch.set_facecolor('gray')
				ax.set_aspect('equal', 'box')
				ax.xaxis.set_major_locator(plt.NullLocator())
				ax.yaxis.set_major_locator(plt.NullLocator())

				for (x, y), w in np.ndenumerate(matrix):
					color = 'white' if w > 0 else 'black'
					size = np.sqrt(np.abs(w) / max_weight)
					rect = plt.Rectangle([x - size / 2, y - size / 2], size, size,facecolor=color, edgecolor=color)
					ax.add_patch(rect)

				ax.autoscale_view()
				ax.invert_yaxis()

			a_hat_t =np.transpose(a_hat)
			a_hat_sq_t = np.transpose(a_hat_sq)
			hinton(a_hat_t)
			plt.savefig("Windowgrangerfinal/"+str(key_name)+"/"+str(order_num)+"/AHAT_start"+str(start)+"Order"+str(order_num)+"Com"+str(stock)+"_Pl"+str(pl_key)+".png")
			plt.close()

		

	return F_Val_t1adj, F_Val_t1pl, sig5, sig1


					
