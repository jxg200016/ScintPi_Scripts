import struct
import glob
import os
import numpy as np #sudo apt-get install python3-numpy
import time
import h5py #sudo apt-get install python3-h5py
'''
i 4
f 4
BBBB 4
b 1
i 4
BBBBBBBBB 9
dddddd 48
fff 12
4+4+4+4+1+9+48+12 = 86
'''
datafolder=r'C:\Users\JmGomezs\Documents\Scintpi\data'  #where the uncompressed files are located
daylist=['20210807']
# daylist=['20210801']
#Be carefull some bin files could be wrong (analize why!)
sat_fields=['SNR1','SNR2','ELEV','T_TW','T_WN','AZIM','PHS1','PHS2']#'PSE1','PSE2'
gnssdic={0:'GPS',1:'SBS',2:'GAL',3:'BDS',6:'GLO'}
for daystring in daylist:
	raw_data_files=[]
	raw_data_files = glob.glob("%s/scintpi3_%s_*.bin"%(datafolder,daystring))
	underscores=-4#Number of underscores in path +1#this shouldnt change
	raw_data_files.sort(key=lambda x: x.split('_')[underscores])
	#Be carefull when we add some _ in the path, for each one add 1 on underscores
	if len(raw_data_files) == 0 :
		raw_input("No files on path.")
	dic={}
	f_week = np.zeros(shape=(1), dtype=np.int32)
	f_towe = np.zeros(shape=(1), dtype=np.float32)
	f_leap = np.zeros(shape=(1), dtype=np.uint8)
	f_cons = np.zeros(shape=(1), dtype=np.uint8)
	f_sats = np.zeros(shape=(1), dtype=np.uint8)
	f_svid = np.zeros(shape=(1), dtype=np.uint8)
	f_elev = np.zeros(shape=(1), dtype=np.int8)
	f_azit = np.zeros(shape=(1), dtype=np.int32)
	f_snr1 = np.zeros(shape=(1), dtype=np.uint8)
	f_snr2 = np.zeros(shape=(1), dtype=np.uint8)
	f_snr3 = np.zeros(shape=(1), dtype=np.uint8)
	f_pst1 = np.zeros(shape=(1), dtype=np.uint8)
	f_pst2 = np.zeros(shape=(1), dtype=np.uint8)
	f_pst3 = np.zeros(shape=(1), dtype=np.uint8)
	f_rst1 = np.zeros(shape=(1), dtype=np.uint8)
	f_rst2 = np.zeros(shape=(1), dtype=np.uint8)
	f_rst3 = np.zeros(shape=(1), dtype=np.uint8)
	f_cph1 = np.zeros(shape=(1), dtype=np.float64)
	f_cph2 = np.zeros(shape=(1), dtype=np.float64)
	f_cph3 = np.zeros(shape=(1), dtype=np.float64)
	f_rng1 = np.zeros(shape=(1), dtype=np.float64)
	f_rng2 = np.zeros(shape=(1), dtype=np.float64)
	f_rng3 = np.zeros(shape=(1), dtype=np.float64)
	f_long = np.zeros(shape=(1), dtype=np.float32)
	f_lati = np.zeros(shape=(1), dtype=np.float32)
	f_heig = np.zeros(shape=(1), dtype=np.float32)

	for singlefile in raw_data_files:
		print (singlefile)
		start_time = time.time()
		data = open(singlefile, "rb").read()
		DataSize = os.stat(singlefile)[6] # Get files sizes
		n_lines = DataSize//96 #only 32,48,96,128,256,etc.
		week = np.zeros(shape=(n_lines), dtype=np.int32) #4
		towe = np.zeros(shape=(n_lines), dtype=np.float32)#4
		leap = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		cons = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		sats = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		svid = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		elev = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		azit = np.zeros(shape=(n_lines), dtype=np.int32)#4
		snr1 = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		snr2 = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		snr3 = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		pst1 = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		pst2 = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		pst3 = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		rst1 = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		rst2 = np.zeros(shape=(n_lines), dtype=np.uint8)#1
		rst3 = np.zeros(shape=(n_lines), dtype=np.uint8)#1 26
		cph1 = np.zeros(shape=(n_lines), dtype=np.float64)#8
		cph2 = np.zeros(shape=(n_lines), dtype=np.float64)#8
		cph3 = np.zeros(shape=(n_lines), dtype=np.float64)#8
		rng1 = np.zeros(shape=(n_lines), dtype=np.float64)#8
		rng2 = np.zeros(shape=(n_lines), dtype=np.float64)#8
		rng3 = np.zeros(shape=(n_lines), dtype=np.float64)#8 # 74
		long = np.zeros(shape=(n_lines), dtype=np.float32)#4
		lati = np.zeros(shape=(n_lines), dtype=np.float32)#4
		heig = np.zeros(shape=(n_lines), dtype=np.float32)#4
		for idx in range(0,n_lines):
			(week[idx],
			 towe[idx],
			 leap[idx],
			 cons[idx],
			 sats[idx],
			 svid[idx],
			 elev[idx],
			 azit[idx],
			 snr1[idx],
			 snr2[idx],
			 snr3[idx],
			 pst1[idx],
			 pst2[idx],
			 pst3[idx],
			 rst1[idx],
			 rst2[idx],
			 rst3[idx],
			 cph1[idx],
			 cph2[idx],
			 cph3[idx],
			 rng1[idx],
			 rng2[idx],
			 rng3[idx],
			 long[idx],
			 lati[idx],
			 heig[idx]) = struct.unpack("@ifBBBBbiBBBBBBBBBddddddfff", data[(96*idx):96*(idx+1)][:-4])
			# print (week[idx],
			#  towe[idx],
			#  leap[idx],
			#  cons[idx],
			#  sats[idx],
			#  svid[idx],
			#  elev[idx],
			#  azit[idx],
			#  snr1[idx],
			#  snr2[idx],
			#  snr3[idx],
			#  pst1[idx],
			#  pst2[idx],
			#  pst3[idx],
			#  rst1[idx],
			#  rst2[idx],
			#  rst3[idx],
			#  cph1[idx],
			#  cph2[idx],
			#  cph3[idx],
			#  rng1[idx],
			#  rng2[idx],
			#  rng3[idx],
			#  long[idx],
			#  lati[idx],
			#  heig[idx])
		f_week = np.hstack((f_week, week))
		f_towe = np.hstack((f_towe, towe))
		f_leap = np.hstack((f_leap, leap))
		f_cons = np.hstack((f_cons, cons))
		f_sats = np.hstack((f_sats, sats))
		f_svid = np.hstack((f_svid, svid))
		f_elev = np.hstack((f_elev, elev))
		f_azit = np.hstack((f_azit, azit))
		f_snr1 = np.hstack((f_snr1, snr1))
		f_snr2 = np.hstack((f_snr2, snr2))
		f_snr3 = np.hstack((f_snr3, snr3))
		f_pst1 = np.hstack((f_pst1, pst1))
		f_pst2 = np.hstack((f_pst2, pst2))
		f_pst3 = np.hstack((f_pst3, pst3))
		f_rst1 = np.hstack((f_rst1, rst1))
		f_rst2 = np.hstack((f_rst2, rst2))
		f_rst3 = np.hstack((f_rst3, rst3))
		f_cph1 = np.hstack((f_cph1, cph1))
		f_cph2 = np.hstack((f_cph2, cph2))
		f_cph3 = np.hstack((f_cph3, cph3))
		f_rng1 = np.hstack((f_rng1, rng1))
		f_rng2 = np.hstack((f_rng2, rng2))
		f_rng3 = np.hstack((f_rng3, rng3))
		f_long = np.hstack((f_long, long))
		f_lati = np.hstack((f_lati, lati))
		f_heig = np.hstack((f_heig, heig))
		print("--- %s seconds ---" % (time.time() - start_time))

	timevec = ( (f_towe- f_leap)%86400)/86400.0*24.0
	constellations = np.unique(f_cons)
	print (constellations)
	# input("Checkhere")

	h5filename = raw_data_files[0].replace('.bin','.h5')
	h5filename = h5filename.replace('scintpi3_','sc3_lvl0_')
	fileh5 = h5py.File(h5filename,'w')

	print ("Creating HDF5 file : %s"%(h5filename))

	for GNSSid in constellations :
		idxarray   = (f_cons == GNSSid) #& (arr < (eachminute+60) ) # bool array
		satellites = np.unique(f_svid[idxarray])
		tmp_timevec = timevec[idxarray]
		tmp_svidvec = f_svid[idxarray]
		validsats = (satellites != 0 )
		for each_sat in satellites[validsats]:
			idxarray2 = (tmp_svidvec == each_sat)

			dic["%02d_%03d_T_TW"%(GNSSid,each_sat)] = f_towe[idxarray][idxarray2]
			dic["%02d_%03d_T_WN"%(GNSSid,each_sat)] = f_week[idxarray][idxarray2]
			dic["%02d_%03d_ELEV"%(GNSSid,each_sat)] = f_elev[idxarray][idxarray2]
			dic["%02d_%03d_AZIM"%(GNSSid,each_sat)] = f_azit[idxarray][idxarray2]
			dic["%02d_%03d_SNR1"%(GNSSid,each_sat)] = f_snr1[idxarray][idxarray2]
			dic["%02d_%03d_SNR2"%(GNSSid,each_sat)] = f_snr2[idxarray][idxarray2]
			dic["%02d_%03d_PHS1"%(GNSSid,each_sat)] = f_cph1[idxarray][idxarray2]
			dic["%02d_%03d_PHS2"%(GNSSid,each_sat)] = f_cph2[idxarray][idxarray2]
			rows=len(dic["%02d_%03d_T_TW"%(GNSSid,each_sat)])
			#wtf?
			print (each_sat)
			sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid],each_sat))
			for field in sat_fields:
				print ("/%s/SVID%03d_%s"%(gnssdic[GNSSid],each_sat,field))
				datatype= type(dic["%02d_%03d_%s"%(GNSSid,each_sat,field)][0])
				dataset = sub_group.create_dataset("%s"%(field), (1,rows), dtype =datatype)
				dataset[...] = dic["%02d_%03d_%s"%(GNSSid,each_sat,field)]

	print("--- %s seconds ---" % (time.time() - start_time))
	fileh5.close()
