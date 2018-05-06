
def sorting_function(master, NYSE2, number):
	remove_list =["CORPORATION", "CORP", "CO", "INCORPORATED", "INC", "COMPANY", "LLC", "LTD", "LIMITED"]

	#MASTER downloaded from FAA website
	master = open(master, "r")
	contents = master.read()
	headings = contents[1:395]
	#want to create a list from these headings 
	headings_list = headings.split(",")
	categories = len(headings_list)
	info_pl = contents[397:]
	info_list = info_pl.split(",")
	#the MASTER file ends with a comma thus there is an extra item
	num_items = len(info_list) - 1
	number_of_planes = float(num_items)/float(categories)
	#create a list within a list for all 314419 planes
	#the end numbers have \r\n before the number (first one just has \n)
	#use .strip() when needed 
	start = 0
	end = categories
	plane_list =[]
	for b in range(int(number_of_planes)):
		ind_plane_list =[]
		plane = info_list[start:end]
		for a in plane:
			ind_plane_list.append(a)
		plane_list.append(ind_plane_list)
		start = end
		end = start + categories

	print len(plane_list)

	corporation_ls =[]	
	for c in plane_list:
		name_1 = c[6]
		#'3' - citizen corporation owned, name of owner not blank
		if c[5] == '3' and len(name_1) >= 1:
			#type of aircraft '4' -fixed wing single engine, '5' - Fixed wing multi engine, '6' - Rotorcraft
			if c[18] == '4' or c[18] =='5' or c[18] == '6':
				#year manufactured - removed if in 1980s and 1970s
				if '198' not in c[4] or '197' not in c[4]:
					c[0] = c[0].strip()
					corporation_ls.append(c)
	#split name into words
	for d in corporation_ls:
		names = d[6]
		#NEW remove full stops and removed management condition
		names = names.replace(".","")
		names = names.replace("(","")
		names = names.replace(")","")
		words = names.split()	
		word_ls = [i for i in words if i not in remove_list]
		d[6] = word_ls	

	#CONCATENATE INITIALS -> helps with rejection as single letters throw up more matches
	#with the other single letters
	#[['H', 'B', 'A'], 'N63TT', ['H', 'B', 'FULLER'], 'FUL']
	#[['J', 'F', 'P'], 'N737XM', ['J', 'P', 'MORGAN', 'CHASE', '&'], 'JPM']
	#problem -> 3,JPMORGAN CHASE BANK (some jp morgan planes like this others like jpmorgan)
	for comps in corporation_ls:
		length_name = len(comps[6])
		if length_name >1:
			sub =[]
			con_ls= []
			index = 0
			for word in comps[6]:
				if len(word) ==1:
					#it is an initial
					sub.append(word)
					index += 1
				else:
					#beginning single letters accounted for only
					break
			if len(sub) > 1:
				#join initial to next word 
				concat = "".join(sub)
				con_ls.append(str(concat))
				rest = comps[6][index:]
				combin = con_ls + rest
				comps[6] = combin

	print len(corporation_ls)
	#118887 now in plane list for comparison	
	import csv
	file_reader = csv.reader(open(NYSE2, 'rb'), delimiter=',')
	list_of_rows =[]
	for row in file_reader:
	    list_of_rows.append(row)
	#index 1 contains name of firm  

	#CHECK FIRST ROW
	#Master names are in capitals, do not contain punctuation  
	for a in list_of_rows:
		comp = a[1]
		comp = comp.replace(".","")
		comp = comp.replace(",","")
		comp = comp.replace("&#39;","")
		comp = comp.upper()
		comp = comp.replace("(THE)","")
		comp = comp.replace("(","")
		comp = comp.replace(")", "")
		a[1] = comp	
	list_of_rows.sort(key=lambda x: x[1])

	"""getting rid of duplicates which represent stocks to the power of a
	all stocks with ^ have a market cap of 0
	can not just remove rows with symbols containing ^ as ALP^Q does not have
	another vairation and some are different clases .A or .B """

	#PROBLEM: this sorting may not return the common share form of stock (need
	#to investigate) or there may not be one

	#due to how the list is ordered -> returns company name associated with most simple for of stock

	#NEW -> this needs to include first 
	corp_no_dup=[list_of_rows[0]]
	for b in range(1,len(list_of_rows)):
		list_com= list_of_rows[b]
		name = list_com[1]
		prev_name = list_of_rows[b-1][1]
		if name != prev_name:
			corp_no_dup.append(list_com)		

	print len(corp_no_dup)
	#split name into words
	for c in corp_no_dup:
		names2 = c[1]
		words2 = names2.split()
		word_ls2 = [i for i in words2 if i not in remove_list]
		c[1] = word_ls2	

	#concatenate intials
	for comps in corp_no_dup:
		length_name = len(comps[1])
		if length_name >1:
			sub =[]
			con_ls= []
			index = 0
			for word in comps[1]:
				if len(word) ==1:
					sub.append(word)
					index += 1
				else:
					#beginning single letters accounted for only
					break
			if len(sub) > 1:
				concat = "".join(sub)
				con_ls.append(str(concat))
				rest = comps[1][index:]
				combin = con_ls + rest
				comps[1] = combin	
				
	#COMPARISON
	#
	
	match_info=[]
	high_match =[]
	good_match =[]
	#RANDOM TESTER
	import random
	#corporation_ls = random.sample(corporation_ls,sample_size)
	for plane in corporation_ls:
		#NEW 
		#adding N as prefx to N number 
		p_num = "N" + str(plane[0])
		p_name = plane[6]
		p_name_len = len(p_name)
		#NEW
		#remove check for airline companies (some called air)
		#AVIATION IS DIFFERENT AS MAY SET UP A SUB COMPANY
		if any('AIRLINE' in s for s in p_name) or any('AERO' in s for s in p_name) or ("AIR" in p_name and "LINES" in p_name)\
		or ("FEDERAL" in p_name and "EXPRESS" in p_name) or ("BOEING" in p_name) or("WELLS" in p_name and "FARGO" in p_name)\
		or ("FLYING" in p_name and "CLUB" in p_name) or ("AIRCRAFT" in p_name) or ("TEXTRON" in p_name)\
		or ("UNIVERSITY" in p_name) or ("ACADEMY" in p_name) or ("FLYING" in p_name and "SERVICE" in p_name) or ("FLYING" in p_name and "SERVICES" in p_name)\
		or ("MUSEUM" in p_name) or ("COLLEGE" in p_name) or any('HELICOPTER' in s for s in p_name) or ("AIR" in p_name) or ("MEDICAL" in p_name)\
		or ("LOCKHEED" in p_name and "MARTIN" in p_name) or ("AIR" in p_name and "CHARTER" in p_name) or ("AIR" in p_name and "CHARTERS" in p_name) or ("FLYERS" in p_name)\
		or ("NORTHROP" in p_name and "GRUMMAN" in p_name) or ("JP" in p_name and "MORGAN" in p_name) or ("BANK" in p_name and "OF" in p_name and "AMERICA"in p_name)\
		or ("AIRWAYS" in p_name) or ("BANK" in p_name and "OF" in p_name and "UTAH" in p_name):
			continue
		else:	
			for comp in corp_no_dup:
				comp_sym = comp[0]
				comp_name = comp[1]
				comp_name_len = len(comp_name)
				#NEW
				if ("AIRLINE" in comp_name) or ("AIRLINES" in comp_name) or ("AIR" in comp_name and "LINES" in comp_name)\
				 or("PARCEL" in comp_name and "SERVICE" in comp_name) or ("BOEING" in comp_name) or("WELLS" in comp_name and "FARGO" in comp_name)\
				 or("LOCKHEED" in comp_name and "MARTIN" in comp_name) or ("AIR" in comp_name and "LEASE"in comp_name)\
				 or ("AIR" in comp_name and "GROUP"in comp_name) or ("PHI" in comp_name): 
					continue
				else:	
				#one is smaller other is smaller, both the same length
					if p_name_len <= comp_name_len and p_name_len >0:
						overlap =[]
						for a in p_name:
							overlapA = [item for item in comp_name if item == a]
							if len(overlapA) > 0:
								overlap.extend(overlapA)
						overlap_len = len(overlap)
						#DUPLICATION
						dupes = [x for x in p_name if x in p_name[int(p_name.index(x))+1:]]
						dupes_comp = [x for x in comp_name if x in comp_name[int(comp_name.index(x))+1:]]
						if (len(dupes) >0 and overlap_len>0):
						#not normally more than one repeated word, and if both have a repeat likely to be exactly the same
						#so can have an overlap of over 1
							if (dupes[0] in overlap):
								overlap_len = overlap_len -1
						elif (len(dupes_comp) >0 and overlap_len>0):
							if dupes_comp[0] in overlap:
								overlap_len = overlap_len -1
						#should be over the smaller one 
						overlap_per = float(overlap_len)/float(p_name_len)
					elif comp_name_len < p_name_len and comp_name_len >0:
						overlap =[]
						
						for a in comp_name:
							overlapA = [item for item in p_name if item == a]
							if len(overlapA)>0:
								overlap.extend(overlapA)
						overlap_len = len(overlap)
						#DUPLICATION
						dupes = [x for x in p_name if x in p_name[int(p_name.index(x))+1:]]
						dupes_comp = [x for x in comp_name if x in comp_name[int(comp_name.index(x))+1:]]
						if (len(dupes) >0 and overlap_len>0):
						#not normally more than one repeated word, and if both have a repeat likely to be exactly the same
						#so can have an overlap of over 1
							if (dupes[0] in overlap):
								overlap_len = overlap_len -1
						elif (len(dupes_comp) >0 and overlap_len>0):
							if dupes_comp[0] in overlap:
								overlap_len = overlap_len -1	
						overlap_per = float(overlap_len)/float(comp_name_len)
					matching = [p_name, p_num, comp_name, comp_sym]	
					#NEW - correction for high items to be in order for next checking part
					if overlap_per >= number:
						match_info.append(matching)
						if overlap_per ==1:
							high_match.append(matching)	
					

	# if the same N number comes up multiple times have not found correct answer
	# sort by N number if the N num is same as previous - already sorted due to loop

	len_s_m = len(match_info)


	low_match_checker = []
	#put all the duplicates in seperate lists and search between those lists 
	#look for much higher overlap

	#each plane can only have one company match
	#match_info already ordered by plane
	#want to make subgroups and only search through sub groups
	index = 0
	for a in range(1, len_s_m):
		match_curr = match_info[a]
		pl_num = match_curr[1]
		pl_num_prev = match_info[a-1][1] 
		pl_nam = match_curr[0]
		comp_nam = match_curr[2]
		comp_sym = match_curr[3]
		#if number matches the next but not the previous, start of group
		#what to do with a = 0
		#end of a group -> indexing 

		#only match put in list
		#allowed this to be 1 word overlap as clearly unusual word as has not matched with anything else
		if a < len_s_m-1:	
			if pl_num != pl_num_prev:
				
				#end of a group
				#want to test plane name with all company names from index up until but not including a
				match_now = match_info[index:a]
				overlap_R=[]
				for match_line in match_now:
					plane = match_line[0]
					comp = match_line[2]
					overlap = []
					if len(plane) <= len(comp):
						for words in plane:
							overlapA = [item for item in comp if item == words]
							if len(overlapA) > 0:
								overlap.append(overlapA)
						overlap_ratio = ((float(len(overlap))/ float(len(plane))) + (float(len(overlap))/ float(len(comp))))/float(2)
						#find index of longest overlap and choose that -> what if there are multiple
						#decided to discard all if multiple as likely to be "Bank of ..."
					else:
						for words in comp:
							overlapA = [item for item in plane if item == words]
							if len(overlapA) > 0:
								overlap.append(overlapA)
						overlap_ratio = ((float(len(overlap))/ float(len(plane))) + (float(len(overlap))/ float(len(comp))))/float(2)
					overlap_R.append(overlap_ratio)
			#but none of them should be empty		
				#if len(overlap_R) > 0:		
				maximum = max(overlap_R)
				list_index_of_max = [i for i, j in enumerate(overlap_R) if j == maximum]
					#can not just be 1 word overlap
					#if you make len condition too high miss out on the ones that slipped through high and med
				if len(list_index_of_max) == 1:
					index_use = list_index_of_max[0]
					best = match_now[index_use]
					best_pl = best[0]
					best_comp = best[2]
					#match first word
					if best_pl[0] == best_comp[0]:
						low_match_checker.append(best)	
				index = a
		#DIFFERENT FOR END OF LIST
		elif a == len_s_m-1:
			
			#want to include final item
			#if last one is differnet end of a group and a single match at end
			#if last one is the same as previous it is in the final group
			if pl_num == pl_num_prev:
				
				#in the end group
				#print" "
				#print"Final"
				#print match_curr
				match_now = match_info[index:a+1]
				#print" "
				#print"Match Now"
				#print match_now
				overlap_R=[]
				for match_line in match_now:
					plane = match_line[0]
					comp = match_line[2]
					overlap = []
					if len(plane) <= len(comp):
						for words in plane:
							overlapA = [item for item in comp if item == words]
							if len(overlapA) > 0:
								overlap.append(overlapA)
						
							#do it over bigger works
						overlap_ratio = ((float(len(overlap))/ float(len(plane))) + (float(len(overlap))/ float(len(comp))))/float(2)
						
						overlap_R.append(overlap_ratio)
					else:
						for words in comp:
							overlapA = [item for item in plane if item == words]
							if len(overlapA) > 0:
								overlap.append(overlapA)
						overlap_ratio = ((float(len(overlap))/ float(len(plane))) + (float(len(overlap))/ float(len(comp))))/float(2)
				
						overlap_R.append(overlap_ratio)		
				#if len(overlap_R) > 0:
					
				maximum = max(overlap_R)
				
				list_index_of_max = [i for i, j in enumerate(overlap_R) if j == maximum]
					#more than one word overlap, best match and first word 
			
				if len(list_index_of_max) == 1:
					index_use = list_index_of_max[0]
					best = match_now[index_use]
					best_pl = best[0]
					best_comp = best[2]
					#match first word
					if best_pl[0] == best_comp[0]:
						low_match_checker.append(best)
			elif pl_num != pl_num_prev:	
				#single different item on end					
				match_now = match_info[index:a]
				overlap_R=[]
				for match_line in match_now:
					plane = match_line[0]
					comp = match_line[2]
					overlap = []
					if len(plane) <= len(comp):
						for words in plane:
							overlapA = [item for item in comp if item == words]
							if len(overlapA) > 0:
								overlap.append(overlapA)
							#do it over bigger works
						overlap_ratio = ((float(len(overlap))/ float(len(plane))) + (float(len(overlap))/ float(len(comp))))/float(2)
						overlap_R.append(overlap_ratio)
					else:
						for words in comp:
							overlapA = [item for item in plane if item == words]
							if len(overlapA) > 0:
								overlap.append(overlapA)
						overlap_ratio = ((float(len(overlap))/ float(len(plane))) + (float(len(overlap))/ float(len(comp))))/float(2)
						overlap_R.append(overlap_ratio)		
				#if len(overlap_R) > 0:		
				maximum = max(overlap_R)
				list_index_of_max = [i for i, j in enumerate(overlap_R) if j == maximum]
					#more than one word overlap, best match and first word 
				if len(list_index_of_max) == 1:
					index_use = list_index_of_max[0]
					best = match_now[index_use]
					best_pl = best[0]
					best_comp = best[2]
					#match first word
					if best_pl[0] == best_comp[0]:
						low_match_checker.append(best)
				low_match_checker.append(match_curr)
						
	f = open('SF_'+str(NYSE2)+'_'+str(number)+'.txt','a')

	for c in low_match_checker:
		#print c
		f.write('\n' + str(c))
		#print" "
	print len(low_match_checker)

	f.close()
	number_of_matches = len(low_match_checker)
	return low_match_checker

#written to compte the DET graph

# numbers = [1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1]
# matches_count =[]
# for a in numbers:
# 	number_of_matches = sorting_function('MASTER.txt', 'NYSE2.csv', a)
# 	matches_count.append(number_of_matches)


# print matches_count













