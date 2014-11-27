from pandas import *
import pandas
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import re
import xml.etree.ElementTree as etree

# check if there are missing data
# detail of missing will be stored in missingData(Dict)

def findMissing(date_start, date_end):
	missingData = dict()
	month_start = int(date_start[:2])
	month_end = int(date_end[:2]) + 1

	for auction in os.listdir('./sourceDir'):
		if os.path.isdir('./sourceDir/' + auction):

			missing_time = list()

			for month in range(month_start, month_end):
				day_start = int(date_start[2:4])
				
				if month != month_start:
					day_start = 1

				if month == month_end - 1:					
					day_end = int(date_end[2:4]) + 1
				else:
					day_end = 32
					if month % 2 == 0:
						day_end = 31

				for day in range(day_start, day_end):
					if month < 10:
						filename = '0' + str(month)
					else:
						filename = str(month)

					if day < 10:
						filename += '0' + str(day)
					else:
						filename += str(day)

					#print './sourceDir/' + auction + '/' + filename + '02.dat'
					if not os.path.isfile('./sourceDir/' + auction + '/' + filename + '02.dat'):
						missing_time.append(filename+'02.dat') 
					if not os.path.isfile('./sourceDir/' + auction + '/' + filename + '14.dat'):
						missing_time.append(filename+'14.dat')
			missingData[auction] = missing_time
	return missingData

# delete the useless field, and then save it as a new file
# this process should be done in ipython due to unnamed field is generated 
def trimField(auction, wanted_field):
	writeFilePath = ('/'.join(auction.split('/')[:-1])) + '/trimmed_' + str(auction.split('/')[-1:])[2:-2]
	#f_write = open(writeFilePath, 'a')
	df = read_csv(auction)
	df.rename(columns={'':'ID'}, inplace=True)
	df = df.ix[:, wanted_field]
	df.to_csv(writeFilePath)
	"""
	csvwriter = csv.writer(f_write)
	for row in df:
		csvwriter.writerow(row)
	"""

# clean all the reagents
# check if the output is the same as the 'reserved' from ckckItemList 
def cleanItemList(source):

	tree = etree.parse(source)
	itemlist = list()
	for child in tree.iter('item'):
		itemlist.append([child.attrib.get('id'), child.attrib.get('name'), child.attrib.get('classid'), child.attrib.get('classname'), child.attrib.get('subclassid'),
		 child.attrib.get('subclassname'), child.attrib.get('qualityid'), child.attrib.get('qualityname')])
	line = 0
	with open('./workingData/itemlist.csv', 'a') as f_write:
		f_write.write("Item_ID,Item_Name,classid,classname,subclassid,subclassname,qualityid,qualityname\n")
		writer = csv.writer(f_write, delimiter=',')
		for item in itemlist:
			writer.writerow(item)
			line += 1
	print line

# print the total number of item count in itemlist
# you should look at the number of 'reserved_count'
def checkItemList(source):
	deleted_count = 0
	total_count = 0
	reserved_count = 0
	with open(source, 'r') as f:
		for row in f:
			#print 'row: ', row
			matchObj1 = re.match(r'(\s*)<spell (.*)', row)
			matchObj2 = re.match(r'(\s*)<reagent (.*)', row)
			matchObj3 = re.match(r'(\s*)</spell>', row)
			matchObj5 = re.match(r'(\s*)</item>', row)
			matchObj4 = re.match(r'<item (.*)>(.*)', row)

			total_count += 1
			if matchObj1 or matchObj2 or matchObj3 or matchObj5:
				deleted_count += 1
			elif matchObj4:
				reserved_count += 1
			else:
				print row
	print 'total:', total_count
	print 'deleted:', deleted_count
	print 'reserved:', reserved_count


'''
	parameters: (path to new collected data, name of realm)
	note: You need to put the new collected data into sourceDir first!
	
	func: cpoy all files of the given realm name in sourceDir to Realms directory
''' 
def collectRealmsData(sourceName, auction):
	if not os.path.isdir('../RealmsData/' + auction):
		os.makedirs('../RealmsData/' + auction)

	target_dir = '../RealmsData/' + auction
	cmd_find = 'find ../sourceDir/' + sourceName + ' -name "' + auction + '" -print'

	for path in os.popen(cmd_find).readlines():
		path = path[:-1]
		cmd_copy = 'cp ' + path + '/* ' + target_dir
		os.system(cmd_copy)
		print cmd_copy

'''
	parameters: (auction name)
	func: copy files in directory (Realmsdata) into (Realmsdata/csv), and make the copied file into correct csv format 
'''
def createCopyOfCSVFormat(auction): 
  for datatime in os.listdir('../RealmsData/' + auction):
    with open('../RealmsData/' + auction + '/' + datatime) as f:
      csvDir = '../RealmsData/csv/' + auction
      if not os.path.exists(csvDir):
        os.makedirs(csvDir)

      datatime = datatime[:-3]
      datatime += 'csv'
      f_write = open(csvDir + '/' + datatime , 'a')
      for row in f:
        matchObj = re.match(r'(.*), (.*)', row)
        if matchObj is not None:
          row = matchObj.group(1) + ' ' + matchObj.group(2)
        f_write.write(row) 
      f_write.close()

'''
	parameters: (start_date, end_date, auction name)
	func: auction with same name (ex: shadowsong_alliance) would be combined into a file. The combined file would be stored in (workingData)
'''
def mergeSameAuction(date_start, date_end, auction):

	month_start = int(date_start[:2])
	month_end = int(date_end[:2]) + 1

	auction_path = '../RealmsData/csv/' + auction

	f_w = open('../workingData/' + auction + '.csv', 'a')
	if os.path.getsize('../workingData/' + auction + '.csv') == 0:
		fields_name = 'Realm Name,Export Time,PMktPrice Date,Reserved,Item ID,Item Name,AH MarketPrice Coppers,AH Quantity,AH MarketPrice,AH MinimumPrice,14-day Median Market Price,Median Market Price StdDev,14-day Todays PMktPrice,PMktPrice StdDev,Daily Price Change,Avg Daily Posted,Avg Estimated Daily Sold,Estimated Demand\n' 
		fields_name = fields_name.replace(' ', '_')
		f_w.write(fields_name)

	#print fields_name
	filename = ""
	if os.path.isdir(auction_path):
		for month in range(month_start, month_end):
			day_start = int(date_start[2:4])
			
			if month != month_start:
				day_start = 1

			if month == month_end - 1:					
				day_end = int(date_end[2:4]) + 1
			else:
				day_end = 32
				if month % 2 == 0:
					day_end = 31

			for day in range(day_start, day_end):
				if month < 10:
					filename = '0' + str(month)
				else:
					filename = str(month)

				if day < 10:
					filename += '0' + str(day)
				else:
					filename += str(day)

				if os.path.isfile(auction_path + '/' + filename + '02.csv'):
					with open(auction_path + '/' + filename + '02.csv') as f_r:
						for line in xrange(1):
							f_r.next()
						for row in f_r:
							f_w.write(row)

				if os.path.isfile(auction_path + '/' + filename + '14.csv'):
					with open(auction_path + '/' + filename + '14.csv') as f_r:
						for line in xrange(1):
							f_r.next()
						for row in f_r:
							f_w.write(row)
	f_w.close()



#makeCSVformat()
#"""
fraction = ['_alliance', '_horde']
sourceDir_date = ['0314-0316', '0317-0319', '0320-0327', '0328-0407', '0408-0423', '0424-0514', '0515-0605', '0606-062702', '062714-0717']
merged_date_0403 = ['shadowsong', 'borean-tundra', 'dathremar', 'khazgoroth']
merged_date_0612 = ['drenden', 'arathor', 'nagrand', 'caelestrasz', 'duskwood', 'bloodhoof', 'azuremyst', 'staghelm']
merged_data_0619 = ['tanaris', 'greymane', 'grizzly-hills', 'lothar', 'blackwater-raiders', 'shadow-council']
merged_date_0626 = ['gnomeregan', 'moonrunner', 'alterac-mountains', 'balnazzar']
merged_date_0703 = ['doomhammer', 'baelgun', 'the-scryers', 'argent-dawn'] 
merged_date_0710 = ['ysera', 'durotan']
merged_date_0717 = ['dawnbringer', 'madoran']


# WORKFLOW
realms_to_update = ['borean-tundra']
date_to_update = sourceDir_date

for realm in realms_to_update:
	for date in date_to_update:
		collectRealmsData(date, realm + fraction[0])
		collectRealmsData(date, realm + fraction[1])

for realm in realms_to_update:
	createCopyOfCSVFormat(realm + fraction[0])
	createCopyOfCSVFormat(realm + fraction[1])

if not os.path.isdir('../workingData/'):
	os.makedirs('../workingData')
for realm in realms_to_update:
	mergeSameAuction('0314', '0717', realm + fraction[0])
	mergeSameAuction('0314', '0717', realm + fraction[1])
#clean RealmsData




#print 'clean item list:', cleanItemList('./sourceDir/itemlist.xml')
#print 'check item list:', checkItemList('./sourceDir/itemlist.xml')
#trimField('./workingData/mergedAuction/shadowsong_alliance.csv', [0, 1, 4, 6])
#ff = read_csv('./workingData/mergedAuction/shadowsong_alliance.csv')
#print ff


