import struct
import glob
import os
import numpy as np #sudo apt-get install python3-numpy
import time
import h5py #sudo apt-get install python3-h5py

datafolder='/home/jm/Documents/2020.FABLAB/scintpi3SW/325'
daylist=['20210801']
# daylist=['20210801']
sat_fields=['SNR1','SNR2','ELEV','TIME','AZIT','PHS1','PHS2']#'PSE1','PSE2'
gnssdic={0:'GPS',1:'SBS',2:'GAL',3:'BEI',6:'GLO'}
for daystring in daylist:
	raw_data_files=[]
	raw_data_files = glob.glob("%s/scintpi3_%s_*.bin"%(datafolder,daystring))
	underscores=-4#Number of underscores in path +1#this shouldnt change
	raw_data_files.sort(key=lambda x: x.split('_')[underscores])
	#Be carefull when we add some _ in the path, for each one add 1 on underscores
	if len(raw_data_files) == 0 :
		raw_input("No files on path.")
	dic={}
	f_week = np.zeros(shape=(1), dtype=np.uint16)
	f_towe = np.zeros(shape=(1), dtype=np.float32)
	f_leap = np.zeros(shape=(1), dtype=np.uint8)
	f_cons = np.zeros(shape=(1), dtype=np.uint8)
	f_sats = np.zeros(shape=(1), dtype=np.uint8)
	f_svid = np.zeros(shape=(1), dtype=np.uint8)
	f_elev = np.zeros(shape=(1), dtype=np.uint8)
	f_azit = np.zeros(shape=(1), dtype=np.int16)
	f_snr1 = np.zeros(shape=(1), dtype=np.uint8)
	f_snr2 = np.zeros(shape=(1), dtype=np.uint8)
	f_snr3 = np.zeros(shape=(1), dtype=np.uint8)
	f_pst1 = np.zeros(shape=(1), dtype=np.uint8)
	f_pst2 = np.zeros(shape=(1), dtype=np.uint8)
	f_pst3 = np.zeros(shape=(1), dtype=np.uint8)
	f_rst1 = np.zeros(shape=(1), dtype=np.uint8)
	f_rst2 = np.zeros(shape=(1), dtype=np.uint8)
	f_rst3 = np.zeros(shape=(1), dtype=np.uint8)
	f_cph1 = np.zeros(shape=(1), dtype=np.float32)
	f_cph2 = np.zeros(shape=(1), dtype=np.float32)
	f_cph3 = np.zeros(shape=(1), dtype=np.float32)
	f_rng1 = np.zeros(shape=(1), dtype=np.float32)
	f_rng2 = np.zeros(shape=(1), dtype=np.float32)
	f_rng3 = np.zeros(shape=(1), dtype=np.float32)
	f_long = np.zeros(shape=(1), dtype=np.float32)
	f_lati = np.zeros(shape=(1), dtype=np.float32)
	f_heig = np.zeros(shape=(1), dtype=np.float32)

	for singlefile in raw_data_files:
		print (singlefile)
		start_time = time.time()
		data = open(singlefile, "rb").read()
		DataSize = os.stat(singlefile)[6] # Get files sizes
		n_lines = DataSize//68
		week = np.zeros(shape=(n_lines), dtype=np.uint16)
		towe = np.zeros(shape=(n_lines), dtype=np.float32)
		leap = np.zeros(shape=(n_lines), dtype=np.uint8)
		cons = np.zeros(shape=(n_lines), dtype=np.uint8)
		sats = np.zeros(shape=(n_lines), dtype=np.uint8)
		svid = np.zeros(shape=(n_lines), dtype=np.uint8)
		elev = np.zeros(shape=(n_lines), dtype=np.uint8)
		azit = np.zeros(shape=(n_lines), dtype=np.int16)
		snr1 = np.zeros(shape=(n_lines), dtype=np.uint8)
		snr2 = np.zeros(shape=(n_lines), dtype=np.uint8)
		snr3 = np.zeros(shape=(n_lines), dtype=np.uint8)
		pst1 = np.zeros(shape=(n_lines), dtype=np.uint8)
		pst2 = np.zeros(shape=(n_lines), dtype=np.uint8)
		pst3 = np.zeros(shape=(n_lines), dtype=np.uint8)
		rst1 = np.zeros(shape=(n_lines), dtype=np.uint8)
		rst2 = np.zeros(shape=(n_lines), dtype=np.uint8)
		rst3 = np.zeros(shape=(n_lines), dtype=np.uint8)
		cph1 = np.zeros(shape=(n_lines), dtype=np.float32)
		cph2 = np.zeros(shape=(n_lines), dtype=np.float32)
		cph3 = np.zeros(shape=(n_lines), dtype=np.float32)
		rng1 = np.zeros(shape=(n_lines), dtype=np.float32)
		rng2 = np.zeros(shape=(n_lines), dtype=np.float32)
		rng3 = np.zeros(shape=(n_lines), dtype=np.float32)
		long = np.zeros(shape=(n_lines), dtype=np.float32)
		lati = np.zeros(shape=(n_lines), dtype=np.float32)
		heig = np.zeros(shape=(n_lines), dtype=np.float32)
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
			 heig[idx]) = struct.unpack("@ifBBBBbiBBBBBBBBBfffffffff", data[(68*idx):68*(idx+1)])
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
			dic["%02d_%03d_TIME"%(GNSSid,each_sat)] =timevec[idxarray][idxarray2]
			dic["%02d_%03d_ELEV"%(GNSSid,each_sat)] = f_elev[idxarray][idxarray2]
			dic["%02d_%03d_AZIT"%(GNSSid,each_sat)] = f_azit[idxarray][idxarray2]
			dic["%02d_%03d_SNR1"%(GNSSid,each_sat)] = f_snr1[idxarray][idxarray2]
			dic["%02d_%03d_SNR2"%(GNSSid,each_sat)] = f_snr2[idxarray][idxarray2]
			dic["%02d_%03d_PHS1"%(GNSSid,each_sat)] = f_cph1[idxarray][idxarray2]
			dic["%02d_%03d_PHS2"%(GNSSid,each_sat)] = f_cph2[idxarray][idxarray2]
			rows=len(dic["%02d_%03d_TIME"%(GNSSid,each_sat)])
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
