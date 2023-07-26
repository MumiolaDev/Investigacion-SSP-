# Import libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import pandas
#import seaborn as sns
import matplotlib as mpl


#import matplotlib.colors as colors # For the colored 1d histogram routine
from matplotlib.ticker import NullFormatter
from matplotlib.colors import LogNorm
from matplotlib.ticker import LogFormatterMathtext
import copy as copy


datos = pandas.read_csv('data_bbeta.csv')
x = datos['beta']
y = datos['anisotropy']
 
#x = datos['radialDistance']
#y = datos['B']  
#y = datos['protonDensity'] 
#y = datos['protonTemp'] 

# Creating bins
x_min = np.min(x)
x_max = np.max(x)
  
y_min = np.min(y)
y_max = np.max(y)
  
x_bins = np.logspace(np.log10(x_min), np.log10(x_max), 60)
y_bins = np.logspace(np.log10(y_min), np.log10(y_max), 60)




fig, ax0 = plt.subplots( figsize =(10, 7)) #10, 7 inicialmente


# Creating plotmasked_array
#plt.hist2d(x, y, bins = [x_bins, y_bins], cmap = plt.cm.plasma,cmin=1)

hist , xedges, yedges = np.histogram2d(x,y, bins = (x_bins, y_bins), density = True) #, density= True al final me cambia el grafico
hist = hist.T
with np.errstate(divide='ignore', invalid='ignore'):  # suppress division by zero warnings
    hist *= 1 / hist.max(axis=0, keepdims=True)
    #hist = 
#hist = np.nan_to_num(hist, nan=0, posinf=0, neginf=0)



#masked_array = np.ma.array(hist, mask=np.isnan(hist))
my_cmap = mpl.cm.get_cmap("plasma")
my_cmap.set_under('w',0.00001)


im = ax0.pcolormesh(xedges, yedges, hist, cmap=my_cmap,vmin=0.001) #gnuplot #despues del masked va   , cmap=plt.cm.plasma

#plt.title("Magnetic Field PSP")  
ax0.set_title("Beta vs Anisotropy PSP")  
ax0.set_xlabel('Beta') 
ax0.set_ylabel('A') 



# show plot

#plt.yscale('log')
#plt.xscale('log')
ax0.set_xscale('log')
ax0.set_yscale('log')



#dens and magnetic y temp x
ax0.set_xlim( min(x), 1 )
#a, b = np.polyfit(x, y, deg=1)

#ax0.set_ylim(5 , max(y))
fig.colorbar(im, ax=ax0)


#f1 = 30000*x**(-1.0)

ax0.set_xlim( 0.06, 400.1)
ax0.set_ylim( 0.29, 200)



#magnetic
#plt.xlim(0.07, 1.01)
#beta vs ani
#plt.xlim(0.06, 400.1)
#plt.ylim(0.29, 200)


#plt.plot(x, f1)
#plt.legend(['f(x) = 30000*x**(-1.0)'])
plt.tight_layout()
plt.savefig('Beta_norm.png')
plt.close(fig)


#profe pablo codigo
#nbeta = 203
#nbetam1 = nbeta-1
#betamax = 52.01d0
#betamin = 0.009d0
#dbeta = (betamax-betamin)/double(nbetam1)
#;betarr = dindgen(nbeta)*dbeta+betamin
#betarr = 10^((ALOG10(betamax)-ALOG10(betamin))*DINDGEN(nbeta)/DOUBLE(nbetam1)+ALOG10(betamin))
