import glob
import h5py
import numpy as np
import time
from datetime import datetime
'''
 - This versions converts the time from tow and week number to unixtime
 - this versions doesnt read the last line of the files, it could be incomplete.
 - the leap second could be not right, this field comes from F9P,
	preferably the leap second must be differentiated manually.
'''
start_time = time.time()
# datafolder='/home/jm/Documents/2020.FABLAB/scintpi3SW/rawIQ1470_ismr'
datafolder=r'C:\Users\JmGomezs\Documents\Scintpi\data'  #where the uncompressed files are located
daylist=['20210720']
for daystring in daylist:
	raw_data_files=[]
	raw_data_files = glob.glob("%s\scintpi3_%s_*.dat"%(datafolder,daystring))
	underscores=5#Number of underscores in path +1
	raw_data_files.sort(key=lambda x: x.split('_')[underscores])
	#Be carefull when we add some _ in the path, for each one add 1 on underscores
	if len(raw_data_files) == 0 :
		raw_input("No files on path.")
	for singlefile in raw_data_files:
		print (singlefile)
	print ("If files are not ordered, check the number of underscores")
	'''
	Declaring dictionaries
	'''
	gnsslist=['00','01','02','03','06']
	gnssdic={'00':'GPS','10':'GPS','01':'SBS','02':'GAL','03':'BDS','06':'GLO'}
	gnssname=['GPS','SBAS','GALILEO','BEIDOU','GLONAS']
	sat_fields=['SNR1','SNR2','ELEV','T_TW','AZIM','PHS1','PHS2']#'PSE1','PSE2'

	dic={}
	maxsats= 38
	for GNSSid in gnssdic:
		for sat in range(1,maxsats):
			for field in sat_fields:
				dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]

	for field in sat_fields:
		dic["%s_%03d_%s"%(GNSSid,131,field)] =[]
	for field in sat_fields:
		dic["%s_%03d_%s"%(GNSSid,133,field)] =[]
	for field in sat_fields:
		dic["%s_%03d_%s"%(GNSSid,136,field)] =[]
	for field in sat_fields:
		dic["%s_%03d_%s"%(GNSSid,138,field)] =[]
	'''
	Yes, generally, flat-text files are not an ideal way to store data. Use a different serialization method.
	numpy.save and numpy.load implement the .npy binary serialization format.
	It is faster, more memory efficient, and much more portable (not to mention you don't loose info on floats).
	'''
	cols2read = [0,1,2,3,4,5,6,7,8,13,15]
	fulldata=np.zeros((len(cols2read)))
	for FILENAME in raw_data_files:
		print ("reading:",FILENAME)
		data = np.loadtxt(open(FILENAME,'rt').readlines()[:-1],delimiter='\t',usecols=cols2read, dtype=None)# unpack=True
		fulldata=np.vstack((fulldata,data))

	# GPSfromUTC = (datetime(1980,1,6) - datetime(1970,1,1)).total_seconds()
	#Universal Time = TOW - leapseconds
	timevec = ( (fulldata[:,1]- fulldata[:,2])%86400)/86400.0*24.0
	gnssvec = fulldata[:,3] #
	svidvec = fulldata[:,4]

	filefinal =raw_data_files[0]
	h5filename = filefinal.replace('.dat','.h5')
	h5filename = h5filename.replace('scintpi3_','sc3_lvl0_')
	print ("Creating HDF5 file : %s"%(h5filename))
	fileh5 = h5py.File(h5filename,'w')
	for GNSSid in gnsslist:
		group = fileh5.create_group("%s"%(gnssdic[GNSSid]))
		idxarray = (gnssvec == int(GNSSid))# helps alot with process time
		tmp_timevec = timevec[idxarray]
		tmp_svidvec = fulldata[:,4][idxarray]
		if GNSSid!='01':
			for eachsat in range(1,maxsats):
				idxarray2 = (tmp_svidvec == eachsat)
				dic["%s_%03d_T_TW"%(GNSSid,eachsat)] = timevec[idxarray][idxarray2]
				dic["%s_%03d_ELEV"%(GNSSid,eachsat)] = fulldata[:,5][idxarray][idxarray2]
				dic["%s_%03d_AZIM"%(GNSSid,eachsat)] = fulldata[:,6][idxarray][idxarray2]
				dic["%s_%03d_SNR1"%(GNSSid,eachsat)] = fulldata[:,7][idxarray][idxarray2]
				dic["%s_%03d_SNR2"%(GNSSid,eachsat)] = fulldata[:,8][idxarray][idxarray2]
				dic["%s_%03d_PHS1"%(GNSSid,eachsat)] = fulldata[:,9][idxarray][idxarray2]
				dic["%s_%03d_PHS2"%(GNSSid,eachsat)] = fulldata[:,10][idxarray][idxarray2]
				rows=len(dic["%s_%03d_T_TW"%(GNSSid,eachsat)])
				if rows>0:
					sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid],eachsat))
					for field in sat_fields:
						print ("/%s/SVID%03d-%s"%(gnssdic[GNSSid],eachsat,field))
						datatype= type(dic["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
						dataset = sub_group.create_dataset("%s"%(field), (1,rows), dtype =datatype)
						dataset[...] = dic["%s_%03d_%s"%(GNSSid,eachsat,field)]
		else :
			sbas_sats=[131,133,136,138]
			for eachsat in sbas_sats:
				idxarray2 = (tmp_svidvec == eachsat)
				dic["%s_%03d_T_TW"%(GNSSid,eachsat)] = timevec[idxarray][idxarray2]
				dic["%s_%03d_ELEV"%(GNSSid,eachsat)] = fulldata[:,5][idxarray][idxarray2]
				dic["%s_%03d_AZIM"%(GNSSid,eachsat)] = fulldata[:,6][idxarray][idxarray2]
				dic["%s_%03d_SNR1"%(GNSSid,eachsat)] = fulldata[:,7][idxarray][idxarray2]
				dic["%s_%03d_SNR2"%(GNSSid,eachsat)] = fulldata[:,8][idxarray][idxarray2]
				dic["%s_%03d_PHS1"%(GNSSid,eachsat)] = fulldata[:,9][idxarray][idxarray2]
				dic["%s_%03d_PHS2"%(GNSSid,eachsat)] = fulldata[:,10][idxarray][idxarray2]
				rows=len(dic["%s_%03d_T_TW"%(GNSSid,eachsat)])
				# print ("rows:",rows)
				if rows>0:
					sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid],eachsat))
					for field in sat_fields:
						print ("/%s/SVID%03d-%s"%(gnssdic[GNSSid],eachsat,field))
						datatype= type(dic["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
						dataset = sub_group.create_dataset("%s"%(field), (1,rows), dtype =datatype)
						dataset[...] = dic["%s_%03d_%s"%(GNSSid,eachsat,field)]
	fileh5.close()
	print("--- This process took %s seconds ---" % (time.time() - start_time))
