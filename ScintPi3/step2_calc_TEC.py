import h5py
import time
import glob
import numpy as np
import matplotlib.pyplot as plt

'''
Declaring some functions
'''
def remove_spikes(data,threshold):
	diff_phase = np.diff(data)
	diff_phase_removed = np.where((-threshold<diff_phase) & (diff_phase<threshold),diff_phase,float("nan"))
	return np.nancumsum(diff_phase_removed)

def replace_zeros_by_nans(carrierphase):
	return np.where(carrierphase!=0,carrierphase,float("nan"))

def remove_cycleslips(carrierphase,threshold):
	diff_phase = np.diff(carrierphase)
	righavg = leftavg = np.zeros((len(diff_phase)))
	leftavg[1: ]= diff_phase[:-1]
	righavg[:-1]= diff_phase[1:]
	avg=leftavg+righavg
	diff_phase_removed = np.where((-threshold<diff_phase) & (diff_phase<threshold),diff_phase,avg)
	return np.nancumsum(diff_phase_removed)

def getwavelengths(conste):
	if conste == '00':
		return 0.19029367,0.24421021
	elif conste == '01':
		return 0.19029367,0.24421021 #This values work for SBAS L1,L2
	elif conste == '02':
		return 0.19029367,0.24834937 #This values work for GALILEO L1,L2 #0.25482805
	elif conste == '03':
		return 0.19203949,0.24834937 #0.19203949 , 0.24834937
	elif conste == '06':
		return 0.18713637,0.2406039
	else :
		print ('Error with Constellation')
		return 0,0

'''
Reading HDF5 file
'''
datafolder=r'C:\Users\JmGomezs\Documents\Scintpi\data'
daylist= ['20210720']
#septentrio sbf files avaliable?
SEP = False
for daystring in daylist:
	raw_data_files=[]
	raw_data_files = glob.glob("%s/sc3_lvl0_%s_*.h5"%(datafolder,daystring))
	hdf5file = raw_data_files[0].split('/')[-1]
	print(hdf5file)
	dic={}
	sep_dic={}
	maxsats=38
	gnsslist=['00','01','02','03','06']
	gnssdic={'00':'GPS','10':'GPS','01':'SBS','02':'GAL','03':'BDS','06':'GLO'}
	gnssname=['GPS','GALILEO','BeiDou','GLONAS']
	sat_fields=['SNR1','SNR2','PHS1','PHS2','ELEV','TIME','AZIT']
	out_fields=['SNR1','SNR2','ELEV','TIME','AZIT','TEC','PHS1','PHS2']
	sep_out_fields=['S_TIME','S_TEC']
	for GNSSid in gnssdic:
		for sat in range(0,maxsats):
			for field in sat_fields:
				dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]
			for field in sep_out_fields:
				sep_dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]

	# h5filename = "%s/%s"%(datafolder,hdf5file)
	h5filename = hdf5file
	print ("Reading *.h5 file")
	h5file = h5py.File(h5filename,'r')
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
			svid = member[0].replace('SVID','')
			for each_param in groups.get(member[0]).keys():
				print ("%s_%s_%s"%(gnssid,svid,each_param))
				dic["%s_%s_%s"%(gnssid,svid,each_param)] = groups.get(member[0]).get(each_param)[0]
	h5file.close()

	'''
	Reading SEPTENTRIO DATA only if is avaliable
	'''
	if SEP:
		datafolder  ='/media/jm/WD4TB/2021_ScintPi_paper/sc3_rawdata'
		s_hdf5file  ='ROJ_SEP_TEC1Hz_DOY730.h5'
		s_h5filename = "%s/%s"%(datafolder,s_hdf5file)
		print ("Reading *.h5 file")
		s_h5file = h5py.File(s_h5filename,'r')
		for conste in s_h5file.keys():
			if conste == 'GPS':
				gnssid = '00'
			elif conste == 'GAL':
				gnssid = '02'
			elif conste == 'BDS':
				gnssid = '03'
			elif conste == 'GLO':
				gnssid = '06'
			groups = s_h5file.get(conste)
			for member in groups.items():
				svid = member[0].replace('SVID','')
				for each_param in groups.get(member[0]).keys():
					print ("SEP - %s_%03d_%s"%(gnssid,int(svid),each_param))
					sep_dic["%s_%03d_%s"%(gnssid,int(svid),each_param)] = groups.get(member[0]).get(each_param)[0]
		s_h5file.close()

	'''
	Septentrio data loaded
	'''

	for GNSSid in gnsslist:
		for eachsat in range(0,maxsats):
			notempty = len(dic["%s_%03d_TIME"%(GNSSid,eachsat)])
			if notempty != 0 :
				L1_wlen, L2_wlen = getwavelengths(GNSSid)
				phase1=np.array(dic["%s_%03d_PHS1"%(GNSSid,eachsat)])
				phase2=np.array(dic["%s_%03d_PHS2"%(GNSSid,eachsat)])

				phase1 = replace_zeros_by_nans(phase1)
				phase2 = replace_zeros_by_nans(phase2)

				'''
				#the next function returns the original len-1 value
				'''
				rphase1 = remove_cycleslips(phase1,2000)
				rphase2 = remove_cycleslips(phase2,2000)
				#So one value is added
				rphase1=np.hstack((rphase1,rphase1[-1]))
				rphase2=np.hstack((rphase2,rphase2[-1]))

				tec = (-phase2*L2_wlen+phase1*L1_wlen)/0.104
				tec = remove_spikes(tec,0.225)
				tec=np.hstack((tec,tec[-1]))
				SaveMin = np.nanmin(tec)
				tec =tec - np.ones(len(tec))*SaveMin
				dic["%s_%03d_TEC"%(GNSSid,eachsat)]  = tec
				#we re-write carrierphases witout jumps
				dic["%s_%03d_PHS1"%(GNSSid,eachsat)] = rphase1
				dic["%s_%03d_PHS2"%(GNSSid,eachsat)] = rphase2

	print ("Creating HDF5 file : %s"%(h5filename))
	h5filename = h5filename.replace('sc3_lvl0','sc3_lvl1')
	fileh5 = h5py.File(h5filename,'w')
	for GNSSid in gnsslist:
		group = fileh5.create_group("%s"%(gnssdic[GNSSid]))
		for eachsat in range(1,maxsats):
			rows=len(dic["%s_%03d_%s"%(GNSSid,eachsat,'TIME')])
			if rows>0:
				sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid],eachsat))
				for field in out_fields:
					print ("/%s/SVID%03d-%s"%(gnssdic[GNSSid],eachsat,field))
					datatype= type(dic["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
					dataset = sub_group.create_dataset("%s"%(field), (1,rows), dtype =datatype)
					dataset[...] = dic["%s_%03d_%s"%(GNSSid,eachsat,field)]

				if SEP:
					sep_rows=len(sep_dic["%s_%03d_%s"%(GNSSid,eachsat,'S_TIME')])
					if sep_rows:
						for field in sep_out_fields:
							print ("/%s/SVID%03d-%s"%(gnssdic[GNSSid],eachsat,field))
							datatype= type(sep_dic["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
							dataset = sub_group.create_dataset("%s"%(field), (1,sep_rows), dtype =datatype)
							dataset[...] = sep_dic["%s_%03d_%s"%(GNSSid,eachsat,field)]

	fileh5.close()
