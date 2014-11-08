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
working_dir = '../workingFile/'

# comment three lines below if the data are in local computer
usb_mode = '/Volumes/TOSHIBA/'
source_dir = usb_mode + source_dir[3:]
working_dir = usb_mode + working_dir[3:]


auction_dir = source_dir + 'auctionData/'
csv_dir = source_dir + 'csvFile/'

if not os.path.isdir(working_dir):
  os.makedirs(working_dir)

#########################################################################################################
# Delete auction data which amount of item is zero.
# Return columns which are given in "remain_columns" argment.
# NOTE: Will the first 2 lines cause some problems?
#########################################################################################################
def removeUselessColumns(auction, remain_columns=['PMktPrice_Date', 'Item_ID', 'AH_MarketPrice', 'AH_Quantity']):
  auction = auction[auction['AH_Quantity'] != 0]
  auction = auction[auction['AH_MarketPrice'] != 0]  
  #auction = auction[auction['AH_MarketPrice'].notnull()]
  #auction = auction[auction['Profit'] != 0]
  return auction.ix[:, remain_columns]

#########################################################################################################
# Remove outliers that its value is away from threshold=2 stdev from mean.
# The removed value will be NaN.
# NOTE: This function does not remove those column values are all NaN 
#########################################################################################################
def removeOutliers(data, threshold=2, on_columns=['AH MarketPrice']):
  for column in on_columns:
    data[column] = data[column][np.abs(data[column]-np.mean(data[column])) <= threshold*np.std(data[column])]
  return data

#########################################################################################################
# Return the max & min value of a given column in auction.
# The returned value is used for normalize.
#########################################################################################################
def getMaxAndMinValue(auction, column):
  return [auction[column].max(), auction[column].min()]

#########################################################################################################
#########################################################################################################
def normalizeFunction(val, v_max, v_min):
  max_diff = v_max - v_min
  if max_diff > 0:
    return (val-v_min)/max_diff
  else:
    return 0.5

#########################################################################################################
#########################################################################################################
def normalize(data, max_min_value, on_field):
  for field in on_field:
    data[field] = data[field].apply(normalizeFunction, args=(max_min_value[0], max_min_value[1]))
  return data

#########################################################################################################
# Look into 'AH_Quantity' and 'AH_MarketPrice' field.
# Read the csv file, then apply "deleteUselessData", take mean of the targe_field.
# The return dataframe will contain (item id, mean of targe field)
#########################################################################################################
def preprocessData(realm, date='0401-0414', threshold=2):
  source_path = working_dir + date + '/'
  target_path = source_path + 'afterPreprocess/'

  if not os.path.isdir(target_path):
    os.makedirs(target_path)
  for fraction in fractionlist:
    auction_name = realm + fraction
    print 'preprocessing',  auction_name
    auction = read_csv(source_path + auction_name + '.csv')
    df = deleteUselessData(auction)
    df = removeOutliers(df, threshold)
    '''
    #df['Profit'] = df['AH_MarketPrice'] * df['AH_Quantity']
    #df

    #df = df.pivot(remain_fields[0], remain_fields[1], remain_fields[2])
    #df = DataFrame(df.mean()) # this line mean the same item within given time range
    #df.columns = [target_field]
    '''
    df.to_csv(target_path + auction_name + '.csv',index=False)

