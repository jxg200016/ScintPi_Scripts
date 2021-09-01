#!/usr/bin/env python
# coding: utf-8

# In[1]:


import h5py
import time
import math
import numpy
from datetime import datetime
from matplotlib import pyplot
import matplotlib.dates as mdates
# from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import optparse
import glob
start_time = time.time()
new_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# import matplotlib.pyplot as plt

'''
Reading HDF5 file
'''
def main(datafolder,daystring):
		raw_data_files=[]
		print("%s/sc3_lvl2_%s*.h5"%(datafolder,daystring) )
		raw_data_files = glob.glob("%s/sc3_lvl2_%s*.h5"%(datafolder,daystring))
		raw_data_files.sort()

		for h5filename in raw_data_files:#could process all files from different stations
			dic={}
			gnsslist=['00','01','02','03','06']
			gpslist=[]
			gallist=[]
			bdslist=[]
			sbslist=[]
			glolist=[]
			# gnsslist=['00'] # only GPS
			# gnssdic={'00':'GPS','01':'SBS','02':'GAL','03':'BDS','06':'GLO'}
			gnssdic={'00':['GPS',gpslist],'01':['SBS',sbslist],'02':['GAL',gallist],'03':['BDS',bdslist],'06':['GLO',glolist]}
			in_fields =['PTEC','T_TW','ELEV','S_TW','S401']

			# out_fields=['S4L1','S4L2','ELEV','TIME','AZIT','NSA1','NSA2'] # 1 min resolution # add 1 min TEC
			for GNSSid in gnssdic:
				if GNSSid!='01':
					for sat in range(1,38):
						for field in in_fields:
							dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]
				else :
					sbas_list=[131,133,136,138]
					for sat in sbas_list:
						for field in in_fields:
							dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]

			maxsats = 0
			print ("Reading %s file"%(h5filename))
			h5file = h5py.File(h5filename,'r+')
			for conste in h5file.keys():
				if conste == 'GPS':
					gnssid = '00'
				elif conste == 'SBS':
					gnssid = '01'
				elif conste == 'GAL':
					gnssid = '02'
				elif conste == 'BDS':
					gnssid = '03'
				elif conste == 'GLO':
					gnssid = '06'

				groups = h5file.get(conste)
				for member in groups.items():
					maxsats = maxsats + 1
					svid = member[0].replace('SVID','')
					gnssdic[gnssid][1].append(int(svid))
					for each_param in groups.get(member[0]).keys():
						dic["%s_%03d_%s"%(gnssid,int(svid),each_param)] = groups.get(member[0]).get(each_param)[0]
			h5file.close()

			print ("maxsats:",maxsats)


			#Initializing Figure :
			pyplot.close('all')
			pyplot.ioff()
			maxcol = 5
			maxrow = int(numpy.ceil(maxsats/maxcol))


			fig, axs = pyplot.subplots(maxrow, maxcol, figsize=(12, 12), dpi=1800) #,constrained_layout = True

			each_row = 0
			each_col = 0
			for GNSSid in gnsslist:
				for eachsat in gnssdic[GNSSid][1]:
					notempty = len(dic["%s_%03d_T_TW"%(GNSSid,eachsat)])
					if notempty != 0 :
						svid = "%2d"%eachsat
						if GNSSid == '00':
							sc2_coid = ' GPS'+ svid
						elif GNSSid == '01':
							sc2_coid = ' SBS'+ svid
						elif GNSSid == '02':
							sc2_coid = ' GAL'+ svid
						elif GNSSid == '03':
							sc2_coid = ' BEI'+ svid
						elif GNSSid == '06':
							sc2_coid = ' GLO'+ svid

						#[:-1] last value of TIME is 0 again, so to avoid it
						SC3_TEC  = (dic["%s_%03d_PTEC"%(GNSSid,eachsat)])
						SC3_TTIME =(dic["%s_%03d_T_TW"%(GNSSid,eachsat)])
						SC3_TIME = (dic["%s_%03d_S_TW"%(GNSSid,eachsat)][:-1] %86400 )/86400.0*24.0
						SC3_ELEV =  dic["%s_%03d_ELEV"%(GNSSid,eachsat)][:-1]
						SC3_S401 =  dic["%s_%03d_S401"%(GNSSid,eachsat)][:-1]*30.0

						SC3_TTIME_DIFF = numpy.diff(SC3_TTIME)
						for timex in range(0,2):
							SC3_TTIME[numpy.argmax(SC3_TTIME_DIFF)-1]=float("nan")
							SC3_TTIME[numpy.argmax(SC3_TTIME_DIFF)]=float("nan")
							SC3_TTIME_DIFF[numpy.argmax(SC3_TTIME_DIFF)] = 0


						texttime = 1

			#             axs[each_row, each_col].plot(SC3_TIME, SC3_SNR_1,'-',color='#d62728',linewidth=0.5)
			#             axs[each_row, each_col].plot(SC3_TIME, SC3_SNR_2,'-k',linewidth=0.5,alpha=0.5)
			#             axs[each_row, each_col].plot(SEP_TIME, SEP_TEC,'-k',linewidth=1)
						axs[each_row, each_col].plot(SC3_TIME, SC3_S401,'-',color='#d62728',linewidth=0.3)
						axs[each_row, each_col].plot(SC3_TTIME, SC3_TEC,'-',color='k',linewidth=0.9)#
						axs2=axs[each_row, each_col].twinx()
						axs2.plot(SC3_TIME, SC3_ELEV,'-',color='#1f77b4',linewidth=0.8)
			#             axs2.plot(SC3_TIME, SC3_ELEV,'o',color='#1f77b4',ms=0.25)
			#             axs[each_row, each_col].plot(SC3_TIME, SC3_ELEV,'-',color='#1f77b4',linewidth=0.8)
						axs[each_row, each_col].text(texttime,22,sc2_coid,fontsize=7,weight='bold')

						if each_col == 0:
							axs[each_row, each_col].set_ylabel('rTEC&S4*30', fontsize = 7)
							axs[each_row, each_col].grid(True,which='minor',linestyle='--',linewidth=0.1)
							axs[each_row, each_col].grid(True,which='major',linestyle='--',linewidth=0.4)
							axs[each_row, each_col].set_yticks(numpy.arange(0, 30.1, step=6))  # Set label locations
							axs2.set_yticks(numpy.arange(0, 90.1, step=18))  # Set label locations
							axs[each_row, each_col].tick_params(axis='y',which='major', width=0.7, labelsize=5)#X and y labels font size
							axs2.tick_params(axis='y',which='major', width=0.7, labelsize=5)#X and y labels font size
							axs[each_row, each_col].set_xticks(numpy.arange(0, 24.1, step=3))  # Set label locations
							pyplot.setp(axs[each_row, each_col].get_xmajorticklabels(), visible=False)
							pyplot.setp(axs2.get_ymajorticklabels(), visible=False)

						if each_row == (maxrow-1):
							axs[each_row, each_col].set_xlabel('Universal Time', fontsize = 7)
							axs[each_row, each_col].set_xticks(numpy.arange(0, 24.1, step=3))  # Set label locations
							axs[each_row, each_col].set_yticks(numpy.arange(0, 30.1, step=6))  # Set label locations.
							axs2.set_yticks(numpy.arange(0, 90.1, step=18))  # Set label locations
							axs[each_row, each_col].grid(True,which='minor',linestyle='--',linewidth=0.1)
							axs[each_row, each_col].grid(True,which='major',linestyle='--',linewidth=0.4)
							axs[each_row, each_col].tick_params(axis='x',which='major', width=0.7, labelsize=5)#X and y labels
							axs2.tick_params(axis='y',which='major', width=0.7, labelsize=5)#X and y labels font size font size
							pyplot.setp(axs[each_row, each_col].get_xmajorticklabels(), visible=False)
							pyplot.setp(axs2.get_ymajorticklabels(), visible=False)
						else:
							axs[each_row, each_col].set_xticks(numpy.arange(0, 24.1, step=3))  # Set label locations
							axs[each_row, each_col].set_yticks(numpy.arange(0, 30.1, step=6))  # Set label locations.
							axs2.set_yticks(numpy.arange(0, 90.1, step=18))  # Set label locations
							axs2.tick_params(axis='y',which='major', width=0.7, labelsize=5)
							axs[each_row, each_col].grid(True,which='minor',linestyle='--',linewidth=0.1)
							axs[each_row, each_col].grid(True,which='major',linestyle='--',linewidth=0.4)
							pyplot.setp(axs[each_row, each_col].get_xmajorticklabels(), visible=False)
							pyplot.setp(axs2.get_ymajorticklabels(), visible=False)
							if each_col == (maxcol-1):
								pyplot.setp(axs2.get_ymajorticklabels(), visible=True)


						axs[each_row, each_col].set_ylim(0, 30.1)
						axs[each_row, each_col].set_xlim(0, 24.1)
						axs2.set_ylim(0,90.1)
						each_col = each_col + 1
						if each_col == maxcol:
							each_row=each_row+1
							each_col = 0

			# # Hide x labels and tick labels for top plots and y ticks for right plots.
			for ax in axs.flat:
				ax.label_outer()
			#     ax2= ax.twinx()
			#     ax2.label_outer()


			#pyplot.show()
			pngfilename = h5filename.replace('h5','png').replace('proc','plots')
			print(pngfilename)
			pyplot.savefig(pngfilename)
			print("--- %s seconds ---" % (time.time() - start_time))


# datafolder=r'\\UARS_NAS01\scintpi3_data\sc004\proc'
# hdf5file ='sc3_lvl2_20210823_0001_967572.6250W_329918.3438N_v325.h5'

if __name__=="__main__":
	parser = optparse.OptionParser()
	parser.add_option('-p',"--path",dest='datapath',type="string",default=r'\\UARS_NAS01\scintpi3_data\sc000\proc')
	parser.add_option('-d',"--day", dest='daystring',type="string",default="20210823")
	(op, args) = parser.parse_args()
	main(op.datapath,op.daystring)
# In[ ]:
