import h5py
import time
import glob
import numpy as np
import matplotlib.pyplot as plt
import optparse
#TODO CHECK CODE TEC (CTEC is weird...)

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
def main(datafolder,daystring):
	# datafolder=r'C:\Users\JmGomezs\Documents\Scintpi\data'
	# daylist= ['20210720']
	# daystring="20210808"
	#septentrio sbf files avaliable?
	#v325 will not work until I read tow and week :(
	SEP = False

	raw_data_files=[]
	raw_data_files = glob.glob("%s/sc3_lvl0_%s_*.h5"%(datafolder,daystring))
	for hdf5file in raw_data_files:
		print(hdf5file)
		dic={}
		sep_dic={}
		maxsats=38
		gpslist=[]
		gallist=[]
		bdslist=[]
		sbslist=[]
		glolist=[]
		gnsslist=['00','01','02','03','06']
		gnssdic={'00':['GPS',gpslist],'01':['SBS',sbslist],'02':['GAL',gallist],'03':['BDS',bdslist],'06':['GLO',glolist]}
		gnssname=['GPS','SBAS','GALILEO','BeiDou','GLONAS']
		in_fields=['SNR1','SNR2','PHS1','PHS2','ELEV','T_TW','T_WN','AZIM','PSE1','PSE2']
		out_fields=['SNR1','SNR2','ELEV','T_TW','T_WN','AZIM','PTEC','CTEC','PHS1','PHS2']
		sep_out_fields=['S_T_TW','S_TEC']
		for GNSSid in gnssdic:
			for sat in range(0,maxsats):
				for field in in_fields:
					dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]
				for field in sep_out_fields:
					sep_dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]

		# h5filename = "%s/%s"%(datafolder,hdf5file)
		h5filename = hdf5file
		print ("Reading *.h5 file")
		h5file = h5py.File(h5filename,'r')
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
					# print ("%s_%s_%s"%(GNSSid,svid,each_param))
					dic["%s_%s_%s"%(GNSSid,svid,each_param)] = groups.get(member[0]).get(each_param)[0]
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
					GNSSid = '00'
				elif conste == 'GAL':
					GNSSid = '02'
				elif conste == 'BDS':
					GNSSid = '03'
				elif conste == 'GLO':
					GNSSid = '06'
				groups = s_h5file.get(conste)
				for member in groups.items():
					svid = member[0].replace('SVID','')
					gnssdic[GNSSid][1].append(int(svid))
					for each_param in groups.get(member[0]).keys():
						print ("SEP - %s_%03d_%s"%(GNSSid,int(svid),each_param))
						sep_dic["%s_%03d_%s"%(GNSSid,int(svid),each_param)] = groups.get(member[0]).get(each_param)[0]
			s_h5file.close()

		'''
		Septentrio data loaded
		'''

		for GNSSid in gnsslist:
			for eachsat in gnssdic[GNSSid][1]:
				notempty = len(dic["%s_%03d_T_TW"%(GNSSid,eachsat)])
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

					tec = (-rphase2*L2_wlen+rphase1*L1_wlen)/0.104
					tec = remove_spikes(tec,0.225)
					tec=np.hstack((tec,tec[-1]))

					SaveMin = np.nanmin(tec)
					tec =tec - np.ones(len(tec))*SaveMin
					dic["%s_%03d_PTEC"%(GNSSid,eachsat)]  = tec
					cphase1 = dic["%s_%03d_PSE1"%(GNSSid,eachsat)]
					cphase2 = dic["%s_%03d_PSE2"%(GNSSid,eachsat)]
					dic["%s_%03d_CTEC"%(GNSSid,eachsat)] = np.subtract(cphase2,cphase1)/0.104
					#we re-write carrierphases witout jumps
					dic["%s_%03d_PHS1"%(GNSSid,eachsat)] = rphase1
					dic["%s_%03d_PHS2"%(GNSSid,eachsat)] = rphase2

		print ("Creating HDF5 file : %s"%(h5filename))
		h5filename = h5filename.replace('sc3_lvl0','sc3_lvl1')
		fileh5 = h5py.File(h5filename,'w')
		for GNSSid in gnsslist:
			group = fileh5.create_group("%s"%(gnssdic[GNSSid][0]))
			for eachsat in gnssdic[GNSSid][1]:
				# print (eachsat)
				rows=len(dic["%s_%03d_%s"%(GNSSid,eachsat,'T_TW')])
				if rows>0:
					sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid][0],eachsat))
					for field in out_fields:
						# print ("/%s/SVID%03d-%s"%(gnssdic[GNSSid][0],eachsat,field))
						datatype= type(dic["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
						dataset = sub_group.create_dataset("%s"%(field), (1,rows), dtype =datatype)
						dataset[...] = dic["%s_%03d_%s"%(GNSSid,eachsat,field)]

					if SEP:
						sep_rows=len(sep_dic["%s_%03d_%s"%(GNSSid,eachsat,'S_T_TW')])
						if sep_rows:
							for field in sep_out_fields:
								print ("/%s/SVID%03d-%s"%(gnssdic[GNSSid][0],eachsat,field))
								datatype= type(sep_dic["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
								dataset = sub_group.create_dataset("%s"%(field), (1,sep_rows), dtype =datatype)
								dataset[...] = sep_dic["%s_%03d_%s"%(GNSSid,eachsat,field)]

		fileh5.close()

if __name__=="__main__":
	parser = optparse.OptionParser()
	parser.add_option('-p',"--path",dest='datapath',type="string",default="~/Documents/")
	parser.add_option('-d',"--day", dest='daystring',type="string",default="20210808")
	(op, args) = parser.parse_args()
	main(op.datapath,op.daystring)
