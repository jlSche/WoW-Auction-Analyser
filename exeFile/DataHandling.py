from pandas import *
from function import *
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

working_dir = '../workingFile/'
source_dir = '../sourceFile/'

# comment three lines below if the data are in local computer
usb_mode = '/Volumes/TOSHIBA/'
working_dir = usb_mode + working_dir[3:]
source_dir = usb_mode + source_dir[3:]

itemlist = read_csv(source_dir+'itemlist.csv')
pop_dir = source_dir + 'population/'

qualitylist = ['Poor', 'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Heirloom']
qualityIDlist = [0, 1, 2, 3, 4, 5, 7]
classlist = ['Consumable', 'Container', 'Weapon', 'Gem', 'Armor', 'Projectile', 'Trade Goods', 'Book', 'Money', 'Quest', 'Key', 'Junk', 'Glyph', 'Caged Pet']
classIDlist = [0, 1, 2, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 17]
fractionlist = ['_alliance', '_horde']

 
#########################################################################################################
# Calculate the p*q of every item first, 
# group items by "groupby_field", sum them up, 
# and then calculate mean value of all groups.
#########################################################################################################
def getMeanProfitOfAllGroups(auction, groupby_column=['PMktPrice_Date']):
  auction['Profit'] = auction['AH_MarketPrice'] * auction['AH_Quantity']
  grouped = auction.groupby(groupby_column, as_index=False).sum()
  return grouped['Profit'].mean()

#########################################################################################################
# Group the auction by "groupby_field" first, and then calculate mean value of each column.
#########################################################################################################
def getMeanOrSumOfEachGroup(auction, groupby_columns=['Item_ID'], opt='mean'):
  df = auction
  if opt == 'mean':
    df = df.groupby(groupby_columns, as_index=False).mean()
  elif opt =='sum':
    df = df.groupby(groupby_columns, as_index=False).sum()
  return df


#########################################################################################################
#########################################################################################################
# Read file ('../sourceFile/connected_date.csv').
# Return Realms satisfiy given conditions (PvP, RP).
#########################################################################################################
def getConnectedRealms(connected_date, PvP='PvE', RP='Normal'):
  print 'Getting Connected Realms...'
  df = read_csv('../sourceFile/connected_date.csv')
  df = df[(df['Date'] == connected_date) & (df['PvP'] == PvP) & (df['RP'] == RP)]

  realmlist = []
  for ele in df['Realms']:
    for realm in ele.split():
      realmlist.append(realm.lower())
  print 'Connected realms:', realmlist
  return realmlist

#########################################################################################################
# Read file ('../sourceFile/population/pop****.csv').
# Return Realms satisfiy given conditions (connected, PvP, RP).
#########################################################################################################
def getRealms(filename, ascending_order=True, amount=5, Connected='N', PvP='PvE', RP='Normal', sort_by='Total'):
  print 'Getting Realms...'
  df = read_csv(pop_dir+'pop'+filename+'.csv')
  df = df[(df['PvP'] == PvP) & (df['RP'] == RP) & (df['Connected'] == Connected)]
  df = df.sort(columns=sort_by, ascending=ascending_order)
  df = df[:amount]
  
  realmlist = []
  for ele in df['Realm']:
    for realm in ele.split():
      realmlist.append(realm.lower())
  print 'Realms:', realmlist
  return realmlist

#########################################################################################################
# Merge the input auction with itemlist, default mergeing method is on 'Item ID' with 'left' method.
# The function will only return specific column, which is claimed in the input argument 'field'.
#########################################################################################################
def mergeWithCategory(auction, return_field, merge_on='Item_ID', merge_method='left'):
  auction = merge(auction, itemlist, on=merge_on, how=merge_method)
  return auction.ix[:, return_field]

#########################################################################################################
#########################################################################################################
def readFile(name):
  return read_csv(working_dir + name + '.csv')

#########################################################################################################
#########################################################################################################
def convertDateFormat(val):
  month, day, year = val.split('/')
  return datetime(int(year), int(month), int(day))

#########################################################################################################
#########################################################################################################
def getWeekNumber(val):
  return val.isocalendar()[1]

#########################################################################################################
#########################################################################################################
def generateAuctionStatus(realm_name, fraction, start_date, end_date, field='classname'):
  print 'Generating auction data of', realm_name, '...'
  auction = readFile(realm_name+'_'+fraction+'_'+start_date+'-'+end_date)
  auction = deleteUselessData(auction)
   
  merged = mergeWithCategory(auction, field)
  return getSum(merged)
  return sumEachCategory(merged, field)
  '''
  merged = mergeWithCategory(auction, field)

  # NEED TO MEAN THE AMOUNT OF EACH ITEM (2-WEEKS DATA NOW)   

  print 'Finished generating auction data.\n'
  return sumEachCategory(merged, field)
  '''

#########################################################################################################
#########################################################################################################
def concateRealmsData(realm_list, fraction='_alliance', date='0401-0414', threshold=2):
  source_path = working_dir + date + '/timeSeries/'
  pieces = []
  for realm in realm_list:
    auction_name = realm + fraction
    print 'Concating', target_field, 'of', auction_name
    auction = read_csv(source_path + auction_name + '.csv')
    auction['Profit'] = getMeanProfitOfAllGroups(auction)
    pieces.append(auction)
  
  return concat(pieces, ignore_index=True)

#########################################################################################################
# Use this function to look into 'AH_Quantity' and 'AH_MarketPrice' field.
# Read the csv file first, first apply "deleteUselessData", take mean of the targe_field.
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

#########################################################################################################
#########################################################################################################
def process(realm_list, fraction='_alliance', date='0401-0414', threshold=2):
  source_path = working_dir + date + '/timeSeires/'
  pieces = []
  for realm in realm_list:
    auction_name = realm + fraction
    print 'processing', target_field, 'of', auction_name
    auction = read_csv(source_path + auction_name + '.csv')
    auction['Profit'] = getMeanProfit(auction)
    pieces.append(auction)
  
  return concat(pieces, ignore_index=True)


###############################################################################################################
