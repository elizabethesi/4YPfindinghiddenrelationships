"""Manages the output of the sorting function.
Groups companies together in a dictionary with company symbol as the key 
the lowercase of the trading letters without ^letter(if this was the first form
given in alphabetical list as checked AFSI as an exampple) so 
that it will be ready to be placed inside url. Place the N numbers in the key."""

from Sorting_function import sorting_function


lmc_example = sorting_function('MASTER.txt', 'NYSE2.csv', 0.6)

#make symbols lowercase and reject remove ^letter
for a in lmc_example:
	sym = str(a[3])
	if any('^' in s for s in sym):
		pos = sym.index('^')
		sym = sym[:pos]
	sym = sym.lower()	
	a[3] = sym	


#will have same key -> no need to order
dict_of_comp ={}
for b in range(0,len(lmc_example)):
	key = lmc_example[b][3]
	dict_of_comp.setdefault(key, [])
	dict_of_comp[key].append(lmc_example[b][1])

print dict_of_comp
print len(dict_of_comp)
