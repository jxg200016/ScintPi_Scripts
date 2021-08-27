import glob
import os
from datetime import datetime
from datetime import timedelta
import matplotlib
matplotlib.use('Agg')
#30 4 * * * python ~/tasks/processing_scintpi3_data.py >> ~/tasks/logs/reports.txt

#TODO: call step1_calltec.py, call step2 , move lvl2 to proc_data and NAS, erase tmp
datapath= '/mfs/io/groups/uars/scintpi/' #Where are the scintpi data
tmp_path= datapath
i=1
today = datetime.today()
yesterday = today - timedelta(days=i) #depends on the time when this script is executed.
daystring = yesterday.strftime("%Y%m%d") # year allways has 4 digits, month 2 and day 2.
datafolder =  glob.glob("%s/sc*/"%(datapath))
for eachgroup in datafolder:
    group_folder = eachgroup.split('/')[-2]#just the group Id
    unzip_path = "%s%s/proc/"%(tmp_path,group_folder)
    print(unzip_path)
    isExist = os.path.exists(unzip_path)
    if isExist==False:
        create_folder_command = "mkdir %s"%(unzip_path)
        os.system(create_folder_command)
    unzip_command = " unzip -o \'%s%s/scintpi3_%s*.bin.zip\' -d %s"%(datapath,group_folder,daystring,unzip_path)#-o to overwrite past files or incomplete files
    os.system(unzip_command) #just to test


    plot_path = "%s%s/plots/"%(tmp_path,group_folder)
    print(plot_path)
    isExist = os.path.exists(plot_path)
    if isExist==False:
        create_folder_command = "mkdir %s"%(plot_path)
        os.system(create_folder_command)

    raw_data_files=[]
    raw_data_files = glob.glob("%sscintpi3_%s_*.bin"%(unzip_path,daystring)) #only get the files from the same day and no others files

    while(len(raw_data_files)!=0):
        sublist=[]
	# 	# current_lat =raw_data_filtered_files[0].split('_')[4].replace('.dat','')
	# 	# current_long =raw_data_filtered_files[0].split('_')[3]
	current_lat = raw_data_files[0].split('_')[-2]
	current_long =raw_data_files[0].split('_')[-3]
	current_lat_wout_dec =raw_data_files[0].split('_')[-2].split('.')[0] #Without decimals
	current_long_wout_dec=raw_data_files[0].split('_')[-3].split('.')[0]
	# 	print ("File from lat : %s and  long : %s"%(current_lat,current_long))
	# 	print ("File from lat : %s and  long : %s"%(current_lat_wout_dec,current_long_wout_dec))
	for each_file in range(0,len(raw_data_files)):
	    #Step3.1.1 get the current coordinates
	    #TODO in the future we are going to need separete between West and east, and North and South
	    latcoor =raw_data_files[each_file].split('_')[-2].split('.')[0]
	    longcoor=raw_data_files[each_file].split('_')[-3].split('.')[0]
	    #Step3.1.2 for the next files compare coordinates
	    #print ("Checking file: %s")%(str(raw_data_filtered_files[each_file]))
	    if abs(int(current_lat_wout_dec)-int(latcoor))<=2.0 and abs(int(current_long_wout_dec)-int(longcoor))<=2.0 : #using radios to join files
	        sublist.append(raw_data_files[each_file])
	#3.1.3. Order files by Hour and minute
	sublist.sort(key=lambda x: x.split('_')[-4])
        print("sublist:",sublist)
        #3.1.5. Delete files from the original list, to avoid work with them again.
	filelist=''
        for each_file2 in sublist:
	    raw_data_files.remove(each_file2)
            if each_file2 == sublist[0]:
                filelist = sublist[0]
            else:
                filelist = "%s,%s"%(filelist,each_file2)
        step0_command = "python /home/scintpi/tasks/step0_readRawdata_v325.py -f %s"%(filelist)#step0_readRawdata_v325.py
        #print(step0_command)
        os.system(step0_command)

    step1_command = "python /home/scintpi/tasks/step1_calcTEC.py -p %s -d %s"%(unzip_path,daystring)
    #print(step1_command)
    os.system(step1_command)
    step2_command = "python /home/scintpi/tasks/step2_calc_S4_SigPhi.py -p %s -d %s"%(unzip_path,daystring)
    os.system(step2_command)
    step3_command = "rm %s*.bin; rm %ssc3_lvl0* ; rm %ssc3_lvl1*"%(unzip_path,unzip_path,unzip_path)
    os.system(step3_command)
    step4_command = "python /home/scintpi/tasks/plot_rTEC_and_S4.py -p %s -d %s"%(unzip_path,daystring)
    os.system(step4_command)

#rsync all the folders, but not the files.
step5_command = 'rsync -a --progress -e \'ssh -i ~/.ssh/UARS_NAS -p 22\' --include=\'*/\' --exclude=\'*.zip\' /mfs/io/groups/uars/scintpi/* uars@10.202.42.160:/volume1/scintpi3_data/'
os.system(step5_command)
print("*********************************************************************")
