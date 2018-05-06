

#This script was used to create the 3D graph that displayed the significance of the F-test for Granger 
#causality for each 60 window

#call seperately for planes and prices

#requires that you know the keys in the dictionaries aved in the pickle files
#and the names of the pickle files

import pickle


#how to open a pickle file - saved a dictionary

prices = open("Windowgrangerfinal/DY/fvaluesprices.pkl","rb")
F_dict_adj = pickle.load(prices)

planes = open("Windowgrangerfinal/DY/fvaluesplanes.pkl","rb")
F_dict_pl = pickle.load(planes)


from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np


#one version of the grpah that was not liked

# fig = plt.figure()
# ax = fig.gca(projection='3d')

# # Make data.
# x= range(len(F_dict_pl['N68VP'][0]))
# X= np.array(x)
# # X = np.arange(-5, 5, 0.25)
# y = range(1,9)
# Y = np.array(y)
# # Y = np.arange(-5, 5, 0.25)
# X, Y = np.meshgrid(X, Y)

# Z = np.array(F_dict_pl['N68VP'])
# # Z = np.array(z_list)
# # .reshape(len(F_dict_adj['N115CT'][0]),8)
# print Z

# # Plot the surface.
# surf = ax.plot_surface(X, Y, Z, cmap=cm.Reds,
#                        linewidth=0, antialiased=False)

# # Customize the z axis.
# # ax.set_zlim(-1.01, 1.01)
# # ax.zaxis.set_major_locator(LinearLocator(10))
# ax.zaxis.set_major_formatter(FormatStrFormatter('%.0f'))
# ax.set_title('F values for plane N68VP (planes)')
# ax.set_xlabel('Start Day')
# ax.set_ylabel('Order')
# ax.set_zlabel('F value')
# # Add a color bar which maps values to colors.
# fig.colorbar(surf, shrink=0.5, aspect=5)
# ax.view_init(elev=55.)
# plt.show()

#preferred version of the graph

fig = plt.figure()
ax = fig.gca(projection='3d')


def cc(arg):
    return mcolors.to_rgba(arg, alpha=0.6)

print len(F_dict_adj['N48VP'])
print len(F_dict_adj['N48VP'][0])

x= range(len(F_dict_adj['N48VP'][0]))
xs = np.array(x)
verts = []
zs = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0,7.0, 8.0]
for z in zs:
	z = int(z-1)
	# print F_dict_adj['N115CT'][0]
	ys = np.array(F_dict_adj['N48VP'][z])

	ys[0], ys[-1] = 0, 0
	verts.append(list(zip(xs, ys)))

poly = PolyCollection(verts, facecolors=[cc('r'), cc('g'), cc('b'),
                                         cc('y'), cc('r'), cc('g'), cc('b'), cc('y')])
poly.set_alpha(0.7)
ax.add_collection3d(poly, zs=zs, zdir='y')

ax.set_title('F values for N48VP (prices)')
ax.set_xlabel('Start Date')
ax.set_xlim3d(0, len(F_dict_adj['N48VP'][0]))
ax.set_ylabel('Order')
ax.set_ylim3d(0, 8)
ax.set_zlabel('F value')
ax.set_zlim3d(0, 20)

plt.show()










# print "CHECK"
# print F_dict_adj['ALL'][0][:10]
# print " "
# print F_dict_adj['ALL'][1][:10]