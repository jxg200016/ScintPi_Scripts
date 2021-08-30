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
def sigma_phi_std_filter(filteredphasedata,timevec):
	"""
	timevec is carrier phase timestamp in seconds from 0 to 24
	sigma_phi will estimate the sigma_phi from the phase
		resolution : 1 min
	"""
	sigmaPhiList=[]
	sigmaPhitime=[]
	times=[]
	frame =1
	for eachminute in range(0,1440):
		times.append(eachminute/60.0)
	arr=np.array(timevec)
	for eachminute in times:
		# print (eachminute,eachminute+60 )
		idxarray   = (arr >= eachminute) & (arr < (eachminute+(1/60.0) ) ) # bool array
		if len(timevec[idxarray])>0:
			# print ("len(idxarray):",len(timevec[idxarray]) )
			tmp_time = timevec[idxarray]
			phasedatafil = filteredphasedata[idxarray]
			if len(timevec[idxarray])>500:
				sigmaPhi= np.nanstd(phasedatafil)
				sigmaPhiList.append(sigmaPhi)
			else :
				sigmaPhiList.append(float("nan"))
		else :
			sigmaPhiList.append(float("nan"))
		sigmaPhitime.append(eachminute+(1/60.0))
	return sigmaPhiList,sigmaPhitime

def butter_highpass(cutoff, fs, order=6):
	"""
	Design a highpass filter.

	Args:
		- cutoff (float) : the cutoff frequency of the filter.
		- fs     (float) : the sampling rate.
		- order    (int) : order of the filter, by default defined to 5.
	"""
	# calculate the Nyquist frequency
	nyq = 0.5 * fs

	# design filter
	high = cutoff / nyq
	b, a = butter(order, high, btype='high', analog=False)

	# returns the filter coefficients: numerator and denominator
	return b, a

def butter_highpass_filter(data, cutoff, fs, order=6):
	b, a = butter_highpass(cutoff, fs, order=order)
	y = lfilter(b, a, data)
	return y

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

def pow10(ampdB):
	return math.pow(10.0,ampdB/10.0)
def s4_1min_2freq(powerData1,powerData2,timevec,elevaData,azitmData):
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
	s4_values2=[]
	s4_times=[]
	s4_avgSNR1 = [] #
	s4_avgSNR2 = [] #
	s4_points1 = [] #    s4_points_per_minute
	s4_points2 = [] #    s4_points_per_minute
	s4_timesr=[]
	s4_elev=[]
	s4_azit=[]

	for eachminute in range(0,1440):
		s4_times.append(eachminute/60.0)

	tmp_amplitudes1 = []
	tmp_amplitudesdB1=[]
	tmp_amplitudes2 = []
	tmp_amplitudesdB2=[]
	tmp_elevations = []
	tmp_azimuths   = []

	init_index=0

	arr=np.array(timevec)#+np.ones([len(timevec)])*(18.0/3600.0) # #SEPTENTRIO USES DATA from 1 MINUTE GPS TIME
	########################
	for eachminute in s4_times:
		idxarray   = (arr >= eachminute) & (arr < (eachminute+(1/60.0)) )# bool array
		tmp_amplitudesdB1 = powerData1[idxarray]
		tmp_amplitudesdB2 = powerData2[idxarray]
		tmp_elevations   = elevaData[idxarray]
		tmp_azimuths     = azitmData[idxarray]
		tmp_amplitudes1=np.power(10,np.array(tmp_amplitudesdB1)/10.0)
		tmp_amplitudes2=np.power(10,np.array(tmp_amplitudesdB2)/10.0)
		# tmp_amplitudes1=list(map(pow10,tmp_amplitudesdB1))#use numpy.power
		# tmp_amplitudes2=list(map(pow10,tmp_amplitudesdB2))
		if len(tmp_amplitudes1)>0:
			s4_1 = np.std(tmp_amplitudes1,ddof=1) / np.mean(tmp_amplitudes1)
		else:
			s4_1 = float("nan")

		if len(tmp_amplitudes2)>0:
			s4_2 = np.std(tmp_amplitudes2,ddof=1) / np.mean(tmp_amplitudes2)
		else:
			s4_2 = float("nan")

		s4_values1.append(s4_1)
		s4_values2.append(s4_2)
		s4_avgSNR1.append(np.mean(tmp_amplitudesdB1))
		s4_avgSNR2.append(np.mean(tmp_amplitudesdB2))
		s4_timesr.append(eachminute+1/60.0) #Septentrio has the timestamp 1 min in advance
		s4_points1.append(len(tmp_amplitudes1))
		s4_points2.append(len(tmp_amplitudes2))
		s4_elev.append(np.mean(tmp_elevations))
		s4_azit.append(np.mean(tmp_azimuths))

	return s4_values1,s4_values2,s4_timesr,s4_points1,s4_points2,s4_elev,s4_azit,s4_avgSNR1,s4_avgSNR2

'''
Reading HDF5 file
'''
# datafolder=r'C:\Users\JmGomezs\Documents\Scintpi\data'
# daylist= ['20210808']
def main(datafolder,daystring):
	raw_data_files=[]
	raw_data_files = glob.glob("%s/sc3_lvl1_%s*.h5"%(datafolder,daystring))
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
		in_fields =['SNR1','SNR2','ELEV','T_TW','T_WN','AZIM','PHS1','PHS2','PTEC','CTEC']
		out_fields=['S401','S402','SIG1','SIG2','ELEV','S_TW','S_WN','AZIM','NOS1','NOS2','SNR1','SNR2','PTEC','CTEC','T_TW','T_WN'] # 1 min resolution # add 1 min TEC
		sep_fields=['S_S401','S_S402','S_ELEV','S_S_TW']

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
				notempty = len(dic["%s_%03d_T_TW"%(GNSSid,eachsat)])
				print (GNSSid,eachsat,notempty)
				if notempty != 0 :
					#GETTING HIGH RESOLUTION DATA
					powerDataL1 = dic["%s_%03d_SNR1"%(GNSSid,eachsat)]
					powerDataL2 = dic["%s_%03d_SNR2"%(GNSSid,eachsat)]
					timevec   =   (dic["%s_%03d_T_TW"%(GNSSid,eachsat)]%86400)/86400.0*24.0
					nday = (dic["%s_%03d_T_TW"%(GNSSid,eachsat)][0]//86400 + dic["%s_%03d_T_TW"%(GNSSid,eachsat)][-1]//86400)//2
					elevaData =   dic["%s_%03d_ELEV"%(GNSSid,eachsat)]
					azitmData =   dic["%s_%03d_AZIM"%(GNSSid,eachsat)]
					dic_out["%s_%03d_CTEC"%(GNSSid,eachsat)] = dic["%s_%03d_CTEC"%(GNSSid,eachsat)]
					dic_out["%s_%03d_PTEC"%(GNSSid,eachsat)] = dic["%s_%03d_PTEC"%(GNSSid,eachsat)]
					dic_out["%s_%03d_T_TW"%(GNSSid,eachsat)] = dic["%s_%03d_T_TW"%(GNSSid,eachsat)]
					dic_out["%s_%03d_T_WN"%(GNSSid,eachsat)] = dic["%s_%03d_T_WN"%(GNSSid,eachsat)]
					dic_out["%s_%03d_S_WN"%(GNSSid,eachsat)] = np.ones((1440))*dic["%s_%03d_T_WN"%(GNSSid,eachsat)][notempty//2]

					rphase1=np.array(dic["%s_%03d_PHS1"%(GNSSid,eachsat)])
					rphase2=np.array(dic["%s_%03d_PHS2"%(GNSSid,eachsat)])

					init_time = timevec[0]

					phasedatarad1 = rphase1*2*np.pi
					phasedatarad2 = rphase2*2*np.pi

					cutoffsc3 = 1.0 #Cut off 1Hz
					fs = 10.0 #TODO not always is 10Hz

					fdetrended1 = butter_highpass_filter(phasedatarad1, cutoffsc3, fs, order=6)
					fdetrended2 = butter_highpass_filter(phasedatarad2, cutoffsc3, fs, order=6)

					#thresholded detrended by filter
					threshold=0.5
					tfdetrended1 = np.where((-threshold<fdetrended1) & (fdetrended1<threshold),fdetrended1,float("nan"))
					tfdetrended2 = np.where((-threshold<fdetrended2) & (fdetrended2<threshold),fdetrended2,float("nan") )

					fsigma1R,fsigmtime1R = sigma_phi_std_filter(tfdetrended1,timevec)
					fsigma2R,fsigmtime2R = sigma_phi_std_filter(tfdetrended2,timevec)


					s4L1_values,s4L2_values,s4_timesr,s4_points1,s4_points2,s4_elev,s4_azit,snr1min,snr2min=s4_1min_2freq(powerDataL1,powerDataL2,timevec,elevaData,azitmData)
					#WRITTING LOW RESOLUTION DATA
					dic_out["%s_%03d_S401"%(GNSSid,eachsat)] = s4L1_values
					dic_out["%s_%03d_S402"%(GNSSid,eachsat)] = s4L2_values
					dic_out["%s_%03d_SNR1"%(GNSSid,eachsat)] = snr1min
					dic_out["%s_%03d_SNR2"%(GNSSid,eachsat)] = snr2min
					dic_out["%s_%03d_NOS1"%(GNSSid,eachsat)] = s4_points1
					dic_out["%s_%03d_NOS2"%(GNSSid,eachsat)] = s4_points2
					dic_out["%s_%03d_S_TW"%(GNSSid,eachsat)] = np.round(np.array(s4_timesr)/24.0*86400.0 + np.ones(len(s4_timesr))*nday*86400.0)#TODO CHECK IT LATER 18 SEC
					dic_out["%s_%03d_ELEV"%(GNSSid,eachsat)] = s4_elev
					dic_out["%s_%03d_AZIM"%(GNSSid,eachsat)] = s4_azit
					dic_out["%s_%03d_SIG1"%(GNSSid,eachsat)] = fsigma1R
					dic_out["%s_%03d_SIG2"%(GNSSid,eachsat)] = fsigma2R

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
							complete_ismrtime_1to24.append((eachtime%86400)/86400.0*24.0)
						dic_out["%s_%03d_S_S401"%(GNSSid,eachsat)] = complete_ismr_S4_1
						dic_out["%s_%03d_S_S402"%(GNSSid,eachsat)] = complete_ismr_S4_2 #+ np.ones((len(complete_ismr_phi1)))*(init_time//86400)*86400.0
						dic_out["%s_%03d_S_ELEV"%(GNSSid,eachsat)] = complete_ismrelev
						dic_out["%s_%03d_S_S_TW"%(GNSSid,eachsat)] = complete_ismrtime_1to24
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

		h5filename = h5filename.replace('sc3_lvl1','sc3_lvl2')
		print ("Creating HDF5 file : %s"%(h5filename))
		fileh5 = h5py.File(h5filename,'w')
		for GNSSid in gnsslist:
			print (GNSSid)
			print ("%s"%(gnssdic[GNSSid][0]))
			group = fileh5.create_group("%s"%(gnssdic[GNSSid][0]))
			for eachsat in gnssdic[GNSSid][1]:
				rows=len(dic_out["%s_%03d_%s"%(GNSSid,eachsat,'S_TW')])
				if rows>0:
					print ("/%s/SVID%03d"%(gnssdic[GNSSid][0],eachsat))
					sub_group = fileh5.create_group("/%s/SVID%03d"%(gnssdic[GNSSid][0],eachsat))
					for field in out_fields:

						datatype= type(dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
						veclengh= len(dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)])
						dataset = sub_group.create_dataset("%s"%(field), (1,veclengh), dtype =datatype)
						dataset[...] = dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)]
						print ("/%s/SVID%03d-%s"%(gnssdic[GNSSid][0],eachsat,field))

					rowsSEP=len(dic_out["%s_%03d_%s"%(GNSSid,eachsat,'S_S_TW')])
					if rowsSEP>0:
						for field in sep_fields:
							datatype= type(dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)][0])
							dataset = sub_group.create_dataset("%s"%(field), (1,rowsSEP), dtype =datatype)
							dataset[...] = dic_out["%s_%03d_%s"%(GNSSid,eachsat,field)]

		fileh5.close()
		print("--- %s seconds ---" % (time.time() - start_time))

if __name__=="__main__":
	parser = optparse.OptionParser()
	parser.add_option('-p',"--path",dest='datapath',type="string",default=r'\\UARS_NAS01\scintpi3_data\sc000\proc')
	parser.add_option('-d',"--day", dest='daystring',type="string",default="20210826")
	(op, args) = parser.parse_args()
	main(op.datapath,op.daystring)
