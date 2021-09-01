import glob
import h5py
import numpy as np
import time
from datetime import datetime
import optparse

def get_comma_separated_args(option, opt, value, parser):
	setattr(parser.values, option.dest, value.split(','))
'''
 - This versions converts the time from tow and week number to unixtime
 - this versions doesnt read the last line of the files, it could be incomplete.
 - the leap second could be not right, this field comes from F9P,
	preferably the leap second must be differentiated manually.
'''
start_time = time.time()
# datafolder='/home/jm/Documents/2020.FABLAB/scintpi3SW/rawIQ1470_ismr'
# datafolder=r'C:\Users\JmGomezs\Documents\Scintpi\data'  #where the uncompressed files are located
# daylist=['20210831']
# for daystring in daylist:
# 	raw_data_files=[]
# 	raw_data_files = glob.glob("%s\scintpi3_%s_*.dat"%(datafolder,daystring))
# 	underscores=5#Number of underscores in path +1
# 	raw_data_files.sort(key=lambda x: x.split('_')[underscores])
# 	#Be carefull when we add some _ in the path, for each one add 1 on underscores
# 	if len(raw_data_files) == 0 :
# 		raw_input("No files on path.")
# 	for singlefile in raw_data_files:
# 		print (singlefile)
# 	print ("If files are not ordered, check the number of underscores")
def main(raw_data_files):
	'''
	Declaring dictionaries
	'''
	gnsslist=['00','01','02','03','06']
	gnssdic={0:'GPS',1:'SBS',2:'GAL',3:'BDS',6:'GLO'}
	gnssname=['GPS','SBAS','GALILEO','BEIDOU','GLONAS']
	sat_fields=['SNR1','SNR2','ELEV','T_TW','T_WN','AZIM','PHS1','PHS2','PSE1','PSE2']#

	dic={}
	# maxsats= 38
	# for GNSSid in gnssdic:
	# 	for sat in range(1,maxsats):
	# 		for field in sat_fields:
	# 			dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]
	#
	# for field in sat_fields:
	# 	dic["%s_%03d_%s"%(GNSSid,131,field)] =[]
	# for field in sat_fields:
	# 	dic["%s_%03d_%s"%(GNSSid,133,field)] =[]
	# for field in sat_fields:
	# 	dic["%s_%03d_%s"%(GNSSid,136,field)] =[]
	# for field in sat_fields:
	# 	dic["%s_%03d_%s"%(GNSSid,138,field)] =[]
	'''
	Yes, generally, flat-text files are not an ideal way to store data. Use a different serialization method.
	numpy.save and numpy.load implement the .npy binary serialization format.
	It is faster, more memory efficient, and much more portable (not to mention you don't loose info on floats).

	2173	173017.903	18	00	010	62	035	51	47	21426468.306473	1	21426465.862924	1	112596851.075557	1	87737794.660164	1	-119523.093750	-768758.062500	529.890991
	col0 = WEEK
	col1 = T_TW
	col2 = leapseconds
	col3 = GNSSid
	col4 = svidvec
	col5 = elevaData
	col6 = AZIM
	col7 = snr1
	col8 = snr2min
	col9 = PSE1
	col11= PSE2 # 10
	col13= PHS1 # 11
	col15= PHS2 # 12

	'''
	cols2read = [0,1,2,3,4,5,6,7,8,9,11,13,15]
	fulldata=np.zeros((len(cols2read)))
	for FILENAME in raw_data_files:
		print ("reading:",FILENAME)
		data = np.loadtxt(open(FILENAME,'rt').readlines()[:-1],delimiter='\t',usecols=cols2read, dtype=None)# unpack=True
		fulldata=np.vstack((fulldata,data))
	f_cons = fulldata[:,3]
	f_svid = fulldata[:,4]
	constellations = np.unique(f_cons)
	print(constellations)

	filefinal =raw_data_files[0]
	h5filename = filefinal.replace('.dat','.h5')
	h5filename = h5filename.replace('scintpi3_','sc3_lvl0_')
	print ("Creating HDF5 file : %s"%(h5filename))
	fileh5 = h5py.File(h5filename,'w')

	for GNSSid in constellations :
		idxarray   = (f_cons == GNSSid) #& (arr < (eachminute+60) ) # bool array
		satellites = np.unique(f_svid[idxarray])
		# tmp_timevec = timevec[idxarray]
		tmp_svidvec = f_svid[idxarray]
		validsats = (satellites != 0 )
		for each_sat in satellites[validsats]:
			idxarray2 = (tmp_svidvec == each_sat)

			dic["%02d_%03d_T_TW"%(GNSSid,each_sat)] = fulldata[:,1][idxarray][idxarray2]
			dic["%02d_%03d_T_WN"%(GNSSid,each_sat)] = fulldata[:,0][idxarray][idxarray2]
			dic["%02d_%03d_ELEV"%(GNSSid,each_sat)] = fulldata[:,5][idxarray][idxarray2]
			dic["%02d_%03d_AZIM"%(GNSSid,each_sat)] = fulldata[:,6][idxarray][idxarray2]
			dic["%02d_%03d_SNR1"%(GNSSid,each_sat)] = fulldata[:,7][idxarray][idxarray2]
			dic["%02d_%03d_SNR2"%(GNSSid,each_sat)] = fulldata[:,8][idxarray][idxarray2]
			dic["%02d_%03d_PHS1"%(GNSSid,each_sat)] = fulldata[:,11][idxarray][idxarray2]
			dic["%02d_%03d_PHS2"%(GNSSid,each_sat)] = fulldata[:,12][idxarray][idxarray2]
			dic["%02d_%03d_PSE1"%(GNSSid,each_sat)] = fulldata[:,9][idxarray][idxarray2]
			dic["%02d_%03d_PSE2"%(GNSSid,each_sat)] = fulldata[:,10][idxarray][idxarray2]
			rows=len(dic["%02d_%03d_T_TW"%(GNSSid,each_sat)])
			#wtf?
			# print (each_sat)
			sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid],each_sat))
			#5 minutes * 60 sec * 20 samples per second =
			if len(dic["%02d_%03d_%s"%(GNSSid,each_sat,'T_TW')]) > 5*60*20 : #only if we have at least 5 minutes of data
				for field in sat_fields:
					# print ("/%s/SVID%03d_%s"%(gnssdic[GNSSid],each_sat,field))
					datatype= type(dic["%02d_%03d_%s"%(GNSSid,each_sat,field)][0])
					dataset = sub_group.create_dataset("%s"%(field), (1,rows), dtype =datatype)
					dataset[...] = dic["%02d_%03d_%s"%(GNSSid,each_sat,field)]

	print("--- %s seconds ---" % (time.time() - start_time))
	fileh5.close()

if __name__=="__main__":
	parser = optparse.OptionParser()
	parser.add_option('-p',"--path",dest='datapath',type="string",default=r'C:\Users\JmGomezs\Documents\Scintpi\data')
	parser.add_option('-d',"--day", dest='daystring',type="string",default="20210825")
	parser.add_option('-f', '--files',
				type='string',
				action='callback',
				callback=get_comma_separated_args,
				dest = 'files_args_list')
	(op, args) = parser.parse_args()
	# print ("op.foo_args_list:", op.foo_args_list)
	# main(op.datapath,op.daystring)
	main(op.files_args_list)
