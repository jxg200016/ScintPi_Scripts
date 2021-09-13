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
start_time = time.time()

#TODO: Double check, compare with septentrio data
#TODO: Double check, when there are two satellite pass.

'''
Reading HDF5 file
'''
def main(datafolder,daystring):
	raw_data_files=[]
	raw_data_files = glob.glob("%s/sc3_lvl2_%s*.h5"%(datafolder,daystring))
	raw_data_files.sort()

	for h5filename in raw_data_files:#could process all files from different stations
		file_daystring = h5filename.split('/')[-1].split('_')[2]

		ismr = False
		dic={}
		dic_out={}
		maxsats=38
		gnsslist=['00','01','02','03','06']
		gpslist=[]
		gallist=[]
		bdslist=[]
		sbslist=[]
		glolist=[]
		# gnsslist=['00'] # only GPS
		gnssdic={'00':['GPS',gpslist],'01':['SBS',sbslist],'02':['GAL',gallist],'03':['BDS',bdslist],'06':['GLO',glolist]}
		in_fields =['S401','S402','SIG1','SIG2','ELEV','S_TW','S_WN','AZIM','NOS1','NOS2','SNR1','SNR2','PTEC','CTEC','T_TW','T_WN']
		out_fields=['S401','S402','SIG1','SIG2','ELEV','S_TW','S_WN','AZIM','NOS1','NOS2','SNR1','SNR2','PTEC'] # ,'PTEC','CTEC' , 1 min resolution # add 1 min TEC

		for GNSSid in gnssdic:
			if GNSSid != '01':
				for sat in range(0,maxsats):
					for field in in_fields:
						dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]

			else :
				sbas_list=[131,133,136,138]
				for sat in sbas_list:
					for field in in_fields:
						dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]


		print ('file_daystring:',file_daystring)
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
					# print ("%s_%s_%s"%(GNSSid,svid,each_param))
					dic["%s_%s_%s"%(GNSSid,svid,each_param)] = groups.get(member[0]).get(each_param)[0]
		h5file.close()

		for GNSSid in gnsslist:
			for eachsat in gnssdic[GNSSid][1]:
				# print(GNSSid,eachsat)
				avg_tec = []
				arr = np.array(dic["%s_%03d_T_TW"%(GNSSid,eachsat)]%86400)
				ptec = dic["%s_%03d_PTEC"%(GNSSid,eachsat)]
				for eachminute in range(0,1440):
					idxarray   = (arr >= eachminute*60.0) & (arr < (eachminute*60.0+(60.0)) )# bool array
					tmp_tec = ptec[idxarray]
					if len(tmp_tec)>0:
						avg_tec.append(np.mean(tmp_tec))
					else:
						avg_tec.append(float("nan"))
				dic["%s_%03d_PTEC"%(GNSSid,eachsat)] = avg_tec

		h5filename = h5filename.replace('sc3_lvl2','sc3_lvl3')
		print ("Creating HDF5 file : %s"%(h5filename))
		fileh5 = h5py.File(h5filename,'w')
		for GNSSid in gnsslist:
			# print (GNSSid)
			# print ("%s"%(gnssdic[GNSSid][0]))
			group = fileh5.create_group("%s"%(gnssdic[GNSSid][0]))
			for eachsat in gnssdic[GNSSid][1]:
				rows=len(dic["%s_%03d_%s"%(GNSSid,eachsat,'S_TW')])
				if rows>0:
					# print ("/%s/SVID%03d"%(gnssdic[GNSSid][0],eachsat))
					sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid][0],eachsat))
					for field in out_fields:
						datatype= type(dic["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
						veclengh= len(dic["%s_%03d_%s"%(GNSSid,eachsat,field)])
						dataset = sub_group.create_dataset("%s"%(field), (1,veclengh), dtype =datatype)
						dataset[...] = dic["%s_%03d_%s"%(GNSSid,eachsat,field)]
						# print ("/%s/SVID%03d-%s"%(gnssdic[GNSSid][0],eachsat,field))

		fileh5.close()
		print("--- %s seconds ---" % (time.time() - start_time))

if __name__=="__main__":
	parser = optparse.OptionParser()
	parser.add_option('-p',"--path",dest='datapath',type="string",default=r'\\UARS_NAS01\scintpi3_data\sc004\proc')
	parser.add_option('-d',"--day", dest='daystring',type="string",default="20210912")
	(op, args) = parser.parse_args()
	main(op.datapath,op.daystring)
