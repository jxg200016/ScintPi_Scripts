import h5py
import time
import math
import glob
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
start_time = time.time()

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

def PRN(gnssid,num):
	if gnssid == '00':
		return num
	elif gnssid == '01':
		return num #same
	elif gnssid == '02':
		return num+70
	elif gnssid == '03':
		return num+140
	elif gnssid == '06':
		if num>0 and num<25:
			return num+37
		elif num>24 and num<31:
			return num+38
	else:
		return num

def pow10(ampdB):
    return math.pow(10.0,ampdB/10.0)
def s4_1min_1freq(powerData1,timevec,elevaData,azitmData):
	""" s4 is a public function that finds the S4 index for a list of
	power_amplitudes.

			   S4 = ((<P^2> - <P>^2) / (<P>^2))^(1/2)
			   Find the standard error according to the
			   following formula:
			   S4_M = S4 / (n)^(1/2)
			   where n is the number of data points used to find
			   the S4 value.
	Exceptions: SyntaxError is raised if windowSize is 0 or negative
	"""
	#TODO : empezar desde el primer minuto del tiempo, no desde el inicio del dictionaries
	#TODO : calcular s4 para l1 y l2 al mismo tiempo, deberia reducir la mitad del tiempo
	#TODO : dont take into account snr2 if this comes with a lot of 0000000 zeros
	s4_values1=[]

	s4_times=[]
	s4_avgSNR1 = [] #
	s4_avgSNR2 = [] #
	s4_points1 = [] #    s4_points_per_minute

	s4_timesr=[]
	s4_elev=[]
	s4_azit=[]

	for eachminute in range(0,1440):
		s4_times.append(eachminute/60.0)

	tmp_amplitudes1 = []
	tmp_amplitudesdB1=[]
	tmp_elevations = []
	tmp_azimuths   = []

	init_index=0

	arr=np.array(timevec)+np.ones([len(timevec)])*(18.0/3600.0) # #SEPTENTRIO USES DATA from 1 MINUTE GPS TIME
	########################
	for eachminute in s4_times:
		idxarray   = (arr >= eachminute) & (arr < (eachminute+(1/60.0)) )# bool array
		tmp_amplitudesdB1 = powerData1[idxarray]
		tmp_elevations   = elevaData[idxarray]
		tmp_azimuths     = azitmData[idxarray]
		tmp_amplitudes1=list(map(pow10,tmp_amplitudesdB1))#use numpy.power


		if len(tmp_amplitudes1)>0:
			s4_1 = np.std(tmp_amplitudes1,ddof=1) / np.mean(tmp_amplitudes1)
		else:
			s4_1 = float("nan")

		s4_values1.append(s4_1)
		s4_avgSNR1.append(np.mean(tmp_amplitudesdB1))
		s4_timesr.append(eachminute+1/60.0) #Septentrio has the timestamp 1 min in advance
		s4_points1.append(len(tmp_amplitudes1))
		s4_elev.append(np.mean(tmp_elevations))
		s4_azit.append(np.mean(tmp_azimuths))

	return s4_values1,s4_timesr,s4_points1,s4_elev,s4_azit,s4_avgSNR1

'''
Reading HDF5 file
'''
# datafolder='/home/jm/Documents/2020.FABLAB/scintpi3SW/rawIQ1470_ismr'
# daylist = ['20210308','20210309','20210310','20210311']
datafolder=r'C:\Users\JmGomezs\Documents\Scintpi\data'
daylist= ['20210314']
for daystring in daylist:
	ismr = False
	dic={}
	dic_out={}
	maxsats=38
	gnsslist=['00','01','02','03','06']
	# gnsslist=['00'] # only GPS
	gnssdic={'00':'GPS','01':'SBS','02':'GAL','03':'BEI','06':'GLO'}
	gnssname=['GPS','SBAS','GALILEO','BBEIDOU','GLONAS']
	in_fields =['SNR1','ELEV','TIME','AZIT']
	out_fields=['S4L1','ELEV','TIME','AZIT','NSA1','SNR1'] # 1 min resolution # add 1 min TEC
	sep_fields=['S_S4L1','S_ELEV','S_TIME']

	for GNSSid in gnssdic:
		if GNSSid != '01':
			for sat in range(0,maxsats):
				for field in in_fields:
					dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]
				for field in out_fields:
					dic_out["%s_%03d_%s"%(GNSSid,sat,field)] =[]
				for field in sep_fields:
					dic_out["%s_%03d_%s"%(GNSSid,sat,field)] =[]
		else :
			sbas_list=[131,133,136,138]
			for sat in sbas_list:
				for field in in_fields:
					dic["%s_%03d_%s"%(GNSSid,sat,field)] =[]
				for field in out_fields:
					dic_out["%s_%03d_%s"%(GNSSid,sat,field)] =[]
				for field in sep_fields:
					dic_out["%s_%03d_%s"%(GNSSid,sat,field)] =[]

	raw_data_files=[]
	raw_data_files = glob.glob("%s/sc2_lvl0_%s*.h5"%(datafolder,daystring))
	raw_data_files.sort()

	for h5filename in raw_data_files:
		file_daystring = h5filename.split('/')[-1].split('_')[2]
		print ('file_daystring:',file_daystring)
		# raw_input("checkerrors")
		print ("Reading %s file"%(h5filename))
		h5file = h5py.File(h5filename,'r+')
		for conste in h5file.keys():
			if conste == 'GPS':
				gnssid = '00'
			elif conste == 'SBS':
				gnssid = '01'
			elif conste == 'GAL':
				gnssid = '02'
			elif conste == 'BEI':
				gnssid = '03'
			elif conste == 'GLO':
				gnssid = '06'
			groups = h5file.get(conste)
			for member in groups.items():
				svid = member[0].replace('SVID','')
				for each_param in groups.get(member[0]).keys():
					# print ("%s_%s_%s"%(gnssid,svid,each_param))
					dic["%s_%03d_%s"%(gnssid,int(svid),each_param)] = groups.get(member[0]).get(each_param)[0]
		h5file.close()


		for GNSSid in gnsslist:
			if GNSSid !='01':
				for eachsat in range(0,maxsats):
					notempty = len(dic["%s_%03d_TIME"%(GNSSid,eachsat)])
					print (GNSSid, eachsat)
					if notempty != 0 :
						#GETTING HIGH RESOLUTION DATA
						powerDataL1 = dic["%s_%03d_SNR1"%(GNSSid,eachsat)]
						# timevec   =   (dic["%s_%03d_TIME"%(GNSSid,eachsat)]%86400)/86400.0*24.0
						timevec   =   (dic["%s_%03d_TIME"%(GNSSid,eachsat)])
						elevaData =   dic["%s_%03d_ELEV"%(GNSSid,eachsat)]
						azitmData =   dic["%s_%03d_AZIT"%(GNSSid,eachsat)]
						s4L1_values,s4_timesr,s4_points1,s4_elev,s4_azit,snr1min=s4_1min_1freq(powerDataL1,timevec,elevaData,azitmData)

						# s4L1_values,s4_timesr,s4_points,s4_elev,s4_azit=s4_1min(powerDataL1,timevec,elevaData,azitmData)
						# s4L2_values,s4_timesr,s4_points,s4_elev,s4_azit=s4_1min(powerDataL2,timevec,elevaData,azitmData)
						#WRITTING LOW RESOLUTION DATA
						dic_out["%s_%03d_S4L1"%(GNSSid,eachsat)] = s4L1_values
						dic_out["%s_%03d_SNR1"%(GNSSid,eachsat)] = snr1min
						dic_out["%s_%03d_NSA1"%(GNSSid,eachsat)] = s4_points1
						dic_out["%s_%03d_TIME"%(GNSSid,eachsat)] = s4_timesr
						dic_out["%s_%03d_ELEV"%(GNSSid,eachsat)] = s4_elev
						dic_out["%s_%03d_AZIT"%(GNSSid,eachsat)] = s4_azit

						if ismr :
							prn = PRN(GNSSid,eachsat)
							# ismrtime,azit,s4,s42,elev,ismr_phi1,ismr_phi2=readingISMR(prn)
							# filename="/home/jm/Documents/2020.FABLAB/scintpi3SW/rawIQ1470_ismr/ljic%s.ismr"%(file_daystring)
							filename="/home/jm/Documents/2020.FABLAB/scintpi3SW/rawIQ1470_ismr/PALM_%s.ismr"%(file_daystring)
							ismrtime,azit,ismr_s4_1,ismr_s4_2,elev,ismr_phi1,ismr_phi2=readingISMR_TOW(prn,filename)
							# complete all the minutes for sigma phi
							ismrtime_res = [ x%10 for x in ismrtime]
							zip_object = zip(ismrtime, ismrtime_res)
							new_ismrtime = []
							for list1_i, list2_i in zip_object:
								new_ismrtime.append(list1_i-list2_i)

							complete_ismr_S4_1 = []
							complete_ismr_S4_2 = []
							complete_ismrtime = []
							complete_ismrelev = []
							for eachminute in range(0,1440):
								try :
									complete_ismr_S4_1.append(ismr_s4_1[new_ismrtime.index(eachminute*60.0)])
									complete_ismrelev.append(elev[new_ismrtime.index(eachminute*60.0)])#Justo to verify
								except Exception as e:
									complete_ismr_S4_1.append(float("nan"))
									complete_ismrelev.append(float("nan"))
								try :
									complete_ismr_S4_2.append(ismr_s4_2[new_ismrtime.index(eachminute*60.0)])
								except Exception as e:
									complete_ismr_S4_2.append(float("nan"))
								complete_ismrtime.append(eachminute*60.0)

							complete_ismrtime_1to24 = []
							for eachtime in complete_ismrtime:
								complete_ismrtime_1to24.append((eachtime%86400)/86400*24)
							dic_out["%s_%03d_S_S4L1"%(GNSSid,eachsat)] = complete_ismr_S4_1
							dic_out["%s_%03d_S_S4L2"%(GNSSid,eachsat)] = complete_ismr_S4_2 #+ np.ones((len(complete_ismr_phi1)))*(init_time//86400)*86400.0
							dic_out["%s_%03d_S_ELEV"%(GNSSid,eachsat)] = complete_ismrelev
							dic_out["%s_%03d_S_TIME"%(GNSSid,eachsat)] = complete_ismrtime_1to24
							#
							# fig = plt.figure(figsize=(14,8)) # ASPECT RATIO 4:3 OR 16:9
							# ax=fig.add_subplot(2,1,1)
							# plt.title("L1 S4 GPS-%d "%(eachsat) )
							# ax.plot(s4_timesr,s4L1_values,'-o',ms=2,zorder=4,color='m',label='SC3 S4')
							#
							# ax.plot(complete_ismrtime_1to24,complete_ismr_S4_1,'-ok',ms=2,zorder=5,label='ISMR')
							# ax2=ax.twinx()
							# ax2.plot(complete_ismrtime_1to24,complete_ismrelev,'-b',ms=2,zorder=5,label='ISMR_elev')
							# ax.set_ylim(ymin=0,ymax=np.nanmax(complete_ismr_S4_1))
							# ax.set_ylabel("0-1")
							# ax.grid(True,which='minor',linestyle='--',linewidth=0.1,zorder=6,color='gray')
							# ax.grid(True,which='major',linestyle='--',linewidth=0.4,zorder=6,color='gray')
							# ax.legend()
							#
							# ax=fig.add_subplot(2,1,2)
							# plt.title("L2 S4 GPS-%d "%(eachsat) )
							# ax.plot(s4_timesr,s4L2_values,'-o',ms=2,zorder=4,color='m',label='SC3 S4')
							# ax.plot(complete_ismrtime_1to24,complete_ismr_S4_2,'-ok',ms=2,zorder=5,label='ISMR')
							# ax.set_ylim(ymin=0,ymax=np.nanmax(complete_ismr_S4_2))
							# ax.set_xlabel("Seconds of day")
							# ax.set_ylabel("0-1")
							# ax.grid(True,which='minor',linestyle='--',linewidth=0.1,zorder=6,color='gray')
							# ax.grid(True,which='major',linestyle='--',linewidth=0.4,zorder=6,color='gray')
							# ax.legend()
							# plt.show()

			else :
				try:
					sbas_sats=[131,133,136,138]
					for eachsat in sbas_sats:
						notempty = len(dic["%s_%03d_TIME"%(GNSSid,eachsat)])
						print (eachsat)
						if notempty != 0 :
							#GETTING HIGH RESOLUTION DATA
							powerDataL1 = dic["%s_%03d_SNR1"%(GNSSid,eachsat)]
							timevec   =   dic["%s_%03d_TIME"%(GNSSid,eachsat)]
							elevaData =   dic["%s_%03d_ELEV"%(GNSSid,eachsat)]
							azitmData =   dic["%s_%03d_AZIT"%(GNSSid,eachsat)]

							s4L1_values,s4_timesr,s4_points1,s4_elev,s4_azit,snr1min=s4_1min_1freq(powerDataL1,timevec,elevaData,azitmData)

							dic_out["%s_%03d_S4L1"%(GNSSid,eachsat)] = s4L1_values
							dic_out["%s_%03d_SNR1"%(GNSSid,eachsat)] = snr1min
							dic_out["%s_%03d_NSA1"%(GNSSid,eachsat)] = s4_points1
							dic_out["%s_%03d_TIME"%(GNSSid,eachsat)] = s4_timesr
							dic_out["%s_%03d_ELEV"%(GNSSid,eachsat)] = s4_elev
							dic_out["%s_%03d_AZIT"%(GNSSid,eachsat)] = s4_azit
							print("SBAS")

				except Exception as e:
					print ('e:',e)
					input("Check errors.................")

		h5filename = h5filename.replace('sc2_lvl0','sc2_lvl2')
		print ("Creating HDF5 file : %s"%(h5filename))
		fileh5 = h5py.File(h5filename,'w')
		for GNSSid in gnsslist:
			group = fileh5.create_group("%s"%(gnssdic[GNSSid]))
			if GNSSid != '01':
				for eachsat in range(0,maxsats):
					rows=len(dic_out["%s_%03d_%s"%(GNSSid,eachsat,'TIME')])
					if rows>0:
						sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid],eachsat))
						for field in out_fields:
							# print ("/%s/SVID%02d-%s"%(gnssdic[GNSSid],eachsat,field))
							datatype= type(dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
							dataset = sub_group.create_dataset("%s"%(field), (1,rows), dtype =datatype)
							dataset[...] = dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)]

						rowsSEP=len(dic_out["%s_%03d_%s"%(GNSSid,eachsat,'S_TIME')])
						if rowsSEP>0:
							for field in sep_fields:
								datatype= type(dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
								dataset = sub_group.create_dataset("%s"%(field), (1,rowsSEP), dtype =datatype)
								dataset[...] = dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)]
			else :
				try:
					sbas_sats=[131,133,136,138]
					for eachsat in sbas_sats:
						rows=len(dic_out["%s_%03d_%s"%(GNSSid,eachsat,'TIME')])
						if rows>0:
							sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid],eachsat))
							for field in out_fields:
								# print ("/%s/SVID%02d-%s"%(gnssdic[GNSSid],eachsat,field))
								datatype= type(dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
								dataset = sub_group.create_dataset("%s"%(field), (1,rows), dtype =datatype)
								dataset[...] = dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)]

							rowsSEP=len(dic_out["%s_%03d_%s"%(GNSSid,eachsat,'S_TIME')])
							if rowsSEP>0:
								for field in sep_fields:
									datatype= type(dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
									dataset = sub_group.create_dataset("%s"%(field), (1,rowsSEP), dtype =datatype)
									dataset[...] = dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)]
				except Exception as e:
					print ('e2:',e)
					input("Check errors.................")

		fileh5.close()
		print("--- %s seconds ---" % (time.time() - start_time))
