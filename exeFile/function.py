from pandas import *
import csv
import os
import re
import glob
import sys

collectedDate_list = ['0314-0316', '0317-0319', '0320-0327', '0328-0407', '0408-0423', '0424-0514', '0515-0605', '0606-062702', '062714-0717', '0718-0807', '0808-082602', '082614-0918', '0919-1013']
fractionlist = ['_alliance', '_horde']
fields_name = 'Realm Name,Export Time,PMktPrice Date,Reserved,Item ID,Item Name,AH MarketPrice Coppers,AH Quantity,AH MarketPrice,AH MinimumPrice,14-day Median Market Price,Median Market Price StdDev,14-day Todays PMktPrice,PMktPrice StdDev,Daily Price Change,Avg Daily Posted,Avg Estimated Daily Sold,Estimated Demand\n' 
fields_name = fields_name.replace(' ', '_')

source_dir = '../sourceFile/'
auction_dir = source_dir + 'auctionData/'
csv_dir = source_dir + 'csvFile/'
working_dir = '../workingFile/'

if not os.path.isdir(working_dir):
  os.makedirs(working_dir)

# auctionData directory collect all time range of an auction together, stills in dat format
# csvFile will store same data as auctionData Directory, but in csv format

'''
 Collect realm data that distribute in different date file into sourceFile/auctionData directory.
 Noted that this function will only gather filename that is *02.dat.

 ### This Function should be run again if the dataset is extended.

 paraneters: (realm)
'''

def collectRealmData(realm):
  for date in collectedDate_list:
    for fraction in fractionlist:
      auction = realm + fraction
      # directory you want to save the data
      target_dir = auction_dir + auction
      if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
      
      cmd_find = 'find ' + source_dir + date + ' -name "' + auction + '" -print'
      print cmd_find

      for path in os.popen(cmd_find).readlines():
        path = path[:-1]
        cmd_copy = 'cp ' + path + '/*02.dat ' + target_dir
        os.system(cmd_copy)
        # if next line isn't executed, it means the auction cannot be found
        print  cmd_copy


'''
 Copy files in auctionData directory into csvFile with correct csv format.
 
 parameters: (realm)
'''
def createCopyOfCSV(realm): 
  for fraction in fractionlist:
    auction = realm + fraction
    target_dir = csv_dir + auction + '/'
    if not os.path.isdir(target_dir):
      os.makedirs(target_dir)

    for datfile in os.listdir(auction_dir + auction):
      csvfile = datfile[:-6]
      csvfile += '.csv'
      if os.path.isfile(target_dir + csvfile):
        continue
      with open(auction_dir + auction + '/' + datfile) as f: 
        print 'copying ' + auction + ' from .dat to .csv'

        f_write = open(target_dir + csvfile , 'a')
        for row in f:
          matchObj = re.match(r'(.*), (.*)', row)
          if matchObj is not None:
            row = matchObj.group(1) + ' ' + matchObj.group(2)
          f_write.write(row) 
        f_write.close()


'''
 Read auction data in given time range from (/sourceFile/csv/auction) and then combine all of them into a big file.
 The final big file will be stored in (workingFile).

parameters: (realm, start date, end date)

'''
def mergeSameAuction(realm, start_date, end_date):
  '''
  the method below will disturb the order of auction data.

  auctionData = DataFrame()
  sourcepath = '../sourceFile/auctionData/csv/'
  for fraction in fractionlist:
    auction = realm + fraction
    for csvfile in os.listdir(sourcepath + auction):
      newData = read_csv(sourcepath + auction + '/' + csvfile)
      auctionData = auctionData.append(newData, ignore_index=True)

  auctionData.to_csv('storm') 
  '''
  
  target_dir = working_dir + start_date + '-' + end_date + '/'
  if not os.path.isdir(target_dir):
    os.makedirs(target_dir)

  for fraction in fractionlist:
    auction = realm + fraction
    if os.path.isfile(target_dir + auction + '.csv'):
      continue
    f_write = open(target_dir + auction +'.csv', 'a')
    f_write.write(fields_name)
    print 'Merging', auction, '...'

    for csv_file in os.listdir(csv_dir + auction):
      if int(csv_file[:-4]) >= int(start_date)+1 and int(csv_file[:-4]) <= int(end_date)+1:
        with open(csv_dir + auction + '/' + csv_file) as f_read:
          for line in xrange(1):
            f_read.next()
          for row in f_read:
            f_write.write(row)
        f_read.close() 
      
    f_write.close()


'''
 This function will return the index of collectedDate_list,
 which stand for the range you need.
'''
def getDirIdxNeeded(start_date, end_date):
  idx_start = 0  
  idx_end = 0
  for idx in range(0, len(collectedDate_list)):
    list_start = int(collectedDate_list[idx][:4])
    list_end = int(collectedDate_list[idx][-4:])

    if start_date >= list_start:
      idx_start = idx
      break
  
  for idx in range(idx_start, len(collectedDate_list)):
    list_start = int(collectedDate_list[idx][:4])
    list_end = int(collectedDate_list[idx][-4:])

    if list_end >= end_date:
      idx_end = idx
      break
  return idx_start, idx_end


# argv1: realm name, argv2: start date, argv3: end date
#collectRealmData(sys.argv[1])
#createCopyOfCSV(sys.argv[1])
#mergeSameAuction(sys.argv[1], sys.argv[2], sys.argv[3])
