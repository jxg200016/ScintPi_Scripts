'''
rsync -a --progress -e "ssh -i /home/jm/Documents/scintpi.key -p 22" scintpi@debye.utdallas.edu:/mfs/io/groups/uars/scintpi/sc000/scintpi3_20210806*.bin.zip /mnt/c/Users/JmGomezs/Documents/Scintpi/
'''

import numpy as np
import glob
import os
import time
from datetime import datetime
from datetime import timedelta

execute_commands = True
outfolder = "~/Documents/"
Len_Rawdata = 52
group = 'sc000'
datelist=['20210801']
#1. Download last day scintpis data :

#1.1 Creating datestring
for daystring in datelist:
	today = datetime.today()- timedelta(days=3)
	yesterday = today - timedelta(days=i) #depends on the time when this script is executed.
	daystring = yesterday.strftime("%Y%m%d") # year allways has 4 digits, month 2 and day 2.
	print("1. Downloading data from:", daystring)
	rsync_command = "rsync -a --progress -e \"ssh -i ~/.ssh/scintpi.key -p 22\" scintpi@debye.utdallas.edu:/mfs/io/groups/uars/scintpi/%s/scintpi3_%s_* %s"%(group,daystring,outfolder)
	'''
	rsync -a --progress -e "ssh -i /home/jm/Documents/scintpi.key -p 22" scintpi@debye.utdallas.edu:/mfs/io/groups/uars/scintpi/sc000/scintpi3_20210720* /mnt/c/Users/JmGomezs/Documents/Scintpi/
	'''
	print (rsync_command)
	if execute_commands:
		os.system(rsync_command)

	#Step2 : unzip files.
	print("2. Unziping data from:", daystring)
	unzip_command = "unzip \'~/Documents/scintpi3_%s_*\' -d %s"%(daystring,outfolder)
	#print (unzip_command)

	if execute_commands:
		os.system(unzip_command)

	#Step3: list all the *.dat files

	raw_data_files=[]
	raw_data_files = glob.glob("%s/scintpi3_%s_*.dat"%(outfolder,daystring)) #only get the files from the same day and no others files
	raw_data_filtered_files = []
	#Check if the files has all the fields which the same lenght
	for index in range(0,len(raw_data_files)):
		if len(str(raw_data_files[index]).split('/')[-1]) == Len_Rawdata:
			#print str(raw_data_files[index])
			raw_data_filtered_files.append(raw_data_files[index])

	#Step3.1 grab all the *.dat files that are at the same coordinates an put in a temporal sublist.
	print("3. Sorting data by station from %s:", daystring)
	OF=0
	while(len(raw_data_filtered_files)!=0):
		sublist=[]
		current_lat =raw_data_filtered_files[0].split('_')[4+OF].replace('.dat','')
		current_long =raw_data_filtered_files[0].split('_')[3+OF]
		current_lat_wout_dec =raw_data_filtered_files[0].split('_')[4+OF].split('.')[0] #Without decimals
		current_long_wout_dec=raw_data_filtered_files[0].split('_')[3+OF].split('.')[0]
		print ("File from lat : %s and  long : %s"%(current_lat,current_long))
		print ("File from lat : %s and  long : %s"%(current_lat_wout_dec,current_long_wout_dec))
		for each_file in range(0,len(raw_data_filtered_files)):
			#Step3.1.1 get the current coordinates
			#TODO in the future we are going to need separete between West and east, and North and South
			latcoor =raw_data_filtered_files[each_file].split('_')[4+OF].split('.')[0]
			longcoor=raw_data_filtered_files[each_file].split('_')[3+OF].split('.')[0]
			#Step3.1.2 for the next files compare coordinates
			#print ("Checking file: %s")%(str(raw_data_filtered_files[each_file]))
			if abs(int(current_lat_wout_dec)-int(latcoor))<=2.0 and abs(int(current_long_wout_dec)-int(longcoor))<=2.0 : #using radios to join files
				sublist.append(raw_data_filtered_files[each_file])

		#print ("sublist:",sublist)
		#3.1.3. Order files by Hour and minute
		sublist.sort(key=lambda x: x.split('_')[2+OF])
		print (sublist)
		full_filename = ("%sscintpi3_%s_%s_%s.dat")%(outfolder,daystring,current_long,current_lat)
		print ("Full file created at: %s "%(full_filename) )

		#step 4: plot Full file
		plot_command = "python %splotting_chunksScintpi3.py -a %s -b %s -c %s -d %s -e %s -f %s -o %s"%("~/Documents/",sublist[0],sublist[1],sublist[2],sublist[3],sublist[4],sublist[5],full_filename)
		#print ("plot command:", plot_command)
		if execute_commands or True:
			print ("plot command:", plot_command)
			os.system(plot_command)
				#3.1.5. Delete files from the original list, to avoid work with them again.
		for each_file2 in sublist:
			raw_data_filtered_files.remove(each_file2)
