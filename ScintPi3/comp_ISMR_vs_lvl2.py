import h5py
import time
import math
import glob
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy.signal import freqz
import optparse


def PRN(GNSSid,num):
	if GNSSid == '00':
		return num
	elif GNSSid == '01':
		return num #same
	elif GNSSid == '02':
		return num+70
	elif GNSSid == '03':
		return num+140
	elif GNSSid == '06':
		if num>0 and num<25:
			return num+37
		elif num>24 and num<31:
			return num+38
	else:
		return num

def readingISMR_TOW(SAT,FILENAME):
	data = open(FILENAME,'r')
	data_lines= data.readline()
	data_lines= data.readlines()
	data.close()
	selected_sat=int(SAT)
	elev=[]
	azit=[]
	timerx5=[]
	timevec=[]
	s4=[]
	s42=[]
	phi=[]
	phi2=[]
	GPSfromUTC = (datetime(1980,1,6) - datetime(1970,1,1)).total_seconds()
	# print ('GPSfromUTC:',GPSfromUTC)
	for line in data_lines:
		split_data= line.split(',')
		len_split = len(split_data)
		if (int(split_data[2])==selected_sat):
			try:
				week=int(split_data[0])
				sec = int(split_data[1])
				timestamp= int(sec)
				elev.append(int(split_data[5]))
				azit.append(int(split_data[4]))
				s4.append(float(split_data[7]))
				s42.append(float(split_data[32]))
				phi.append(float(split_data[13]))
				phi2.append(float(split_data[38]))
				timevec.append(timestamp%86400)#return seconds of day
			except Exception as e:
				print ('e:',e)
	return timevec,azit,s4,s42,elev,phi,phi2

filename='//UARS_NAS01/scintpi3_data/sc000/proc/CSS_237.ismr'
prn = PRN('00',27)
ismrtime,azit,ismr_s4_1,ismr_s4_2,elev,ismr_phi1,ismr_phi2=readingISMR_TOW(prn,filename)
print(len(ismrtime),len(ismr_s4_1))

dic={}
gpslist=[]
gallist=[]
bdslist=[]
sbslist=[]
glolist=[]
# gnsslist=['00'] # only GPS
gnssdic={'00':['GPS',gpslist],'01':['SBS',sbslist],'02':['GAL',gallist],'03':['BDS',bdslist],'06':['GLO',glolist]}

h5filename='//UARS_NAS01/scintpi3_data/sc004/proc/sc3_lvl2_20210829_0001_967572.6875W_329918.2812N_v325.h5'
print ("Reading %s file"%(h5filename))
h5file = h5py.File(h5filename,'r+')
for conste in h5file.keys():
	if conste == 'GPS':
		GNSSid = '00'
	elif conste == 'SBS':
		GNSSid = '01'
	elif conste == 'GAL':
		GNSSid = '02'
	elif conste == 'BDS':
		GNSSid = '03'
	elif conste == 'GLO':
		GNSSid = '06'
	groups = h5file.get(conste)
	for member in groups.items():
		svid = member[0].replace('SVID','')
		gnssdic[GNSSid][1].append(int(svid))
		for each_param in groups.get(member[0]).keys():
			print ("%s_%s_%s"%(GNSSid,svid,each_param))
			dic["%s_%s_%s"%(GNSSid,svid,each_param)] = groups.get(member[0]).get(each_param)[0]
h5file.close()



scintpi_time = dic["00_027_S_TW"]%86400
scintpi_S401 = dic["00_027_S401"]
scintpi_SIG1 = dic["00_027_SIG1"]
scintpi_ELEV = dic["00_027_ELEV"]
plt.plot(scintpi_time,scintpi_S401,'--b')
plt.plot(ismrtime,ismr_s4_1,'-k')
# plt.plot(scintpi_time,scintpi_ELEV,'--g')
# plt.plot(ismrtime,elev,'-m')
plt.show()

plt.plot(scintpi_time,scintpi_SIG1,'--b')
plt.plot(ismrtime,ismr_phi1,'-k')
plt.show()
