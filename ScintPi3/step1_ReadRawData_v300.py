import glob
import h5py
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
'''
 - This versions converts the time string to 1...23.999 hours
 - this versions doesnt read the last line of the files, it could be incomplete due to errors.
 - This versions has the universal time
'''
start_time = time.time()
# print("--- %s seconds ---" % (time.time() - start_time))

datafolder='~/MyPath/ ' #where the uncompressed files are located
daylist= ['20210309','20210310','20210311']
for daystring in daylist:
	raw_data_files=[]
	raw_data_files = glob.glob("%s/scintpi3_%s_*.dat"%(datafolder,daystring))
	underscores=3
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
	gnssdic={'00':'GPS','01':'SBS','02':'GAL','03':'BDS','06':'GLO'}
	gnssname=['GPS','SBAS','GALILEO','BEIDOU','GLONAS']
	sat_fields=['SNR1','SNR2','ELEV','TIME','AZIT','PHS1','PHS2']#'PSE1','PSE2'

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

	00	00	0.05	21	03	13	00	007	15	145	44	38	21458167.671917	1	21458150.153654	1	112763492.215492	1	87867608.106569	2	-119522.976562	-768758.125000	528.211975
	col6 : gnssid
	col7: svid
	col8 : elev
	col9 : azit
	col10: SNR1
	col11: SNR2
	col16: carrierphase1
	col18: carrierphase2

	datetime_str = split_data[3]+'/'+split_data[4]+'/'+split_data[5]+' '+ split_data[0]+':'+split_data[1]+':'+split_data[2]
	datetime_object = datetime.strptime(datetime_str, '%y/%m/%d %H:%M:%S.%f')
	# print 'datetime.timestamp:', float(totimestamp(datetime_object))
	'''

	cols2read = [0,1,2,6,7,8,9,10,11,16,18]
	fulldata=np.zeros((len(cols2read)))
	for FILENAME in raw_data_files:
		print ("reading file:",FILENAME)
		'''
		sacrifice the last line just in case the file had been cutted abruptally.
		'''
		data = np.loadtxt(open(FILENAME,'rt').readlines()[:-1],delimiter='\t',usecols=cols2read, dtype=None)
        #data = np.loadtxt(open(FILENAME,'rt'),delimiter='\t',usecols=cols2read, dtype=None)
		fulldata=np.vstack((fulldata,data))

	# GPSfromUTC = (datetime(1980,1,6) - datetime(1970,1,1)).total_seconds()
    #Universal Time
	timevec = np.add(np.add(fulldata[:,0],fulldata[:,1]/60.0 ), fulldata[:,2]/3600.0)
	# timevec = np.add(np.add(fulldata[:,0]*3600,fulldata[:,1]*60.0 ), fulldata[:,2])

	gnssvec = fulldata[:,3] #
	svidvec = fulldata[:,4]

	filefinal =raw_data_files[0]
	h5filename = filefinal.replace('.dat','.h5')
	h5filename = h5filename.replace('scintpi3_','sc3_lvl0_')
    print ("Creating HDF5 file : %s"%(h5filename))
	fileh5 = h5py.File(h5filename,'w')
	for GNSSid in gnsslist:
		group = fileh5.create_group("%s"%(gnssdic[GNSSid]))
		#get data for this constellation
		idxarray = (gnssvec == int(GNSSid))# helps alot with process time
		tmp_timevec = timevec[idxarray]
		tmp_svidvec = fulldata[:,4][idxarray]
		if GNSSid!='01':
			for eachsat in range(1,maxsats):
				idxarray2 = (tmp_svidvec == eachsat)
				'''
				indices2 solves a bugg in the first version, this bugg repetead samples.
				'''
				tmp_timeu = timevec[idxarray][idxarray2]
				tmp_timeuu,indices2,counts =  np.unique(tmp_timeu,return_index=True,return_counts=True)#TO avoid repeat data
				dic["%s_%03d_TIME"%(GNSSid,eachsat)] = timevec[idxarray][idxarray2][indices2]
				dic["%s_%03d_ELEV"%(GNSSid,eachsat)] = fulldata[:,5][idxarray][idxarray2][indices2]
				dic["%s_%03d_AZIT"%(GNSSid,eachsat)] = fulldata[:,6][idxarray][idxarray2][indices2]
				dic["%s_%03d_SNR1"%(GNSSid,eachsat)] = fulldata[:,7][idxarray][idxarray2][indices2]
				dic["%s_%03d_PHS1"%(GNSSid,eachsat)] = fulldata[:,9][idxarray][idxarray2][indices2]
				dic["%s_%03d_SNR2"%(GNSSid,eachsat)] = fulldata[:,8][idxarray][idxarray2][indices2]
				dic["%s_%03d_PHS2"%(GNSSid,eachsat)] = fulldata[:,10][idxarray][idxarray2][indices2]
				rows=len(dic["%s_%03d_SNR1"%(GNSSid,eachsat)])
				rows2=len(dic["%s_%03d_SNR2"%(GNSSid,eachsat)])
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
				print ("eachsat:",eachsat)
				idxarray2 = (tmp_svidvec == eachsat)

				tmp_timeu = timevec[idxarray][idxarray2]
				tmp_timeuu,indices2 =  np.unique(tmp_timeu,return_index=True)
				dic["%s_%03d_TIME"%(GNSSid,eachsat)] = timevec[idxarray][idxarray2][indices2]
				dic["%s_%03d_ELEV"%(GNSSid,eachsat)] = fulldata[:,5][idxarray][idxarray2][indices2]
				dic["%s_%03d_AZIT"%(GNSSid,eachsat)] = fulldata[:,6][idxarray][idxarray2][indices2]
				dic["%s_%03d_SNR1"%(GNSSid,eachsat)] = fulldata[:,7][idxarray][idxarray2][indices2]
				dic["%s_%03d_SNR2"%(GNSSid,eachsat)] = fulldata[:,8][idxarray][idxarray2][indices2]
				dic["%s_%03d_PHS1"%(GNSSid,eachsat)] = fulldata[:,9][idxarray][idxarray2][indices2]
				dic["%s_%03d_PHS2"%(GNSSid,eachsat)] = fulldata[:,10][idxarray][idxarray2][indices2]
				rows=len(dic["%s_%03d_TIME"%(GNSSid,eachsat)])
				# print ("rows:",rows)
				if rows>0:
					sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid],eachsat))
					for field in sat_fields:
						#print ("/%s/SVID%03d-%s"%(gnssdic[GNSSid],eachsat,field))
						datatype= type(dic["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
						dataset = sub_group.create_dataset("%s"%(field), (1,rows), dtype =datatype)
						dataset[...] = dic["%s_%03d_%s"%(GNSSid,eachsat,field)]
	fileh5.close()
	print("--- This process took %s seconds ---" % (time.time() - start_time))
