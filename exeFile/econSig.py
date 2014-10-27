from pandas import *
from function import *
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

working_dir = '../workingFile/'
source_dir = '../sourceFile/'

## comment these three lines if use the data in local computer
usb_mode = '/Volumes/TOSHIBA/'
working_dir = usb_mode + working_dir[3:]
source_dir = usb_mode + source_dir[3:]

itemlist = read_csv(source_dir+'itemlist.csv')
pop_dir = source_dir + 'population/'
description = '_horde_0401-0414'

qualitylist = ['Poor', 'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Heirloom']
qualityIDlist = [0, 1, 2, 3, 4, 5, 7]
classlist = ['Consumable', 'Container', 'Weapon', 'Gem', 'Armor', 'Projectile', 'Trade Goods', 'Book', 'Money', 'Quest', 'Key', 'Junk', 'Glyph', 'Caged Pet']
classIDlist = [0, 1, 2, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 17]
fractionlist = ['_alliance', '_horde']

'''
  Workflow:
    1)  read csv file
    2)  deleteUselessData
    3)  removeOutliers
    4)  normalize

  ex: 
  area_52 = read_csv()
  df = deleteUselessData(area_52)
  df = removeOutliers(df)
  df = normalize(df)
'''

def convertDateFormat(val):
  month, day, year = val.split('/')
  return datetime(int(year), int(month), int(day))

def getWeekNumber(val):
  return val.isocalendar()[1]

# Delete auction data which amount of item is zero. Return field is remain_field
def deleteUselessData(auction, remain_fields=['PMktPrice_Date', 'Item_ID', 'AH_MarketPrice']):
  auction = auction[auction['AH_Quantity'] != 0]
  auction = auction[auction['AH_MarketPrice'] != 0]  
  '''
    This 2 lines may cause some problems.
  '''
  return auction.ix[:, remain_fields]

def getMaxAndMinValue(auction, field):
  return [auction[field].max(), auction[field].min()]

# Remove outliers that its value is more than threshold=2 stdev from mean,
# the removed value will be NaN
def removeOutliers(data, threshold=2, on_field=['AH_MarketPrice']):
  for field in on_field:
    data[field] = data[field][np.abs(data[field]-np.mean(data[field])) <= threshold*np.std(data[field])]
  '''
    This function does not remove those column values are all NaN 
  '''
  return data

def normalizeFunction(val, v_max, v_min):
  max_diff = v_max - v_min
  if max_diff > 0:
    return (val-v_min)/max_diff
  else:
    return 0.5

def normalize(data, max_min_value, on_field):
  for field in on_field:
    data[field] = data[field].apply(normalizeFunction, args=(max_min_value[0], max_min_value[1]))
  return data

def preprocessData(realm, target_field, date='0401-0414', threshold=2):
  source_path = working_dir + date + '/'
  remain_fields = (['PMktPrice_Date', 'Item_ID'])
  remain_fields.append(target_field)
  if not os.path.isdir(source_path + 'timeSeries/'):
    os.makedirs(source_path + 'timeSeries')
  for fraction in fractionlist:
    auction_name = realm + fraction
    print 'preprocessing', target_field, 'of', auction_name
    auction = read_csv(source_path + auction_name + '.csv')
    df = deleteUselessData(auction, remain_fields)
    if target_field == 'AH_MarketPrice':
      df = removeOutliers(df, threshold)
    df = df.pivot(remain_fields[0], remain_fields[1], remain_fields[2])
    df = DataFrame(df.mean()) # this line mean the same item within given time range
    df.columns = [target_field]

    if target_field == 'AH_MarketPrice':
      df.to_csv(source_path + 'timeSeries/p_' + auction_name + '.csv')
    elif target_field == 'AH_Quantity':  
      df.to_csv(source_path + 'timeSeries/q_' + auction_name + '.csv')
    else:
      print 'No target field matched.'

# try do analysis data before/after connected, 
# also try to merge with subclassname
def analyseData(realm, target_field='AH_Quantity', merge_with='classname', date='0401-0414'):
  source_path = working_dir + date + '/timeSeries/'
  for fraction in fractionlist:
    auction_name = realm + fraction
    print 'analysing', target_field, 'of', auction_name
    if target_field == 'AH_MarketPrice':
      auction_name = 'p_' + auction_name
    elif target_field == 'AH_Quantity':
      auction_name = 'q_' + auction_name
    auction = read_csv(source_path + auction_name + '.csv')
    
    df = mergeWithCategory(auction, [merge_with, target_field])
    if target_field == 'AH_Quantity':
      df = df.groupby([merge_with]).sum() 
    elif target_field == 'AH_MarketPrice':
      df = df.groupby([merge_with]).mean()

    return normalize(df, getMaxAndMinValue(df, target_field), [target_field]) 
###############################################################################################################


def getSum(auction, group_by='classname'):
  auction = auction.groupby([group_by], as_index=False).sum()
  return auction
  #return auction.ix[:, ['Item_id', 'AH_MarketPrice', 'AH_Quantity']]

# Merge the input auction with itemlist, default mergeing method is on 'Item ID' with 'inner' method.
# The function will only return the given column, which is the input argument 'field'.
def mergeWithCategory(auction, return_field, merge_on='Item_ID', merge_method='left'):
  auction = merge(auction, itemlist, on=merge_on, how=merge_method)
  return auction.ix[:, return_field]

# Sum up item amount in each category
def sumEachCategory(categorized, field):
  '''
    NEEDED TO DO MEAN, AND SHOULD AGGREGATE BY AH_QUANTITY
  '''

  return categorized.groupby(field).agg('sum')
  #return categorized.groupby(field).agg('count')

def readFile(name):
  return read_csv(working_dir + name + '.csv')


# Read file ('../sourceFile/connected_date.csv') and return Realms satisfiy connected_date, Type, and RP.
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


# Read file ('../sourceFile/population/pop****.csv') and return Realms satisfiy connected_date, Type, and RP.
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

'''
 Work Flow: 
  0)  Run getRealms function with proper parameters to generate realm list.
      Parameters: (pop filename, ascending_order=True, amount=5, Connected='N', PvP='PvE', RP='Normal', sort_by='Total'):

  1)  Run generateWorkingData function to grenerate time range of *.csv file needed.
      Parameters: (realm name), (start date), (end date)
  
  2)  Run generateAuctionStatus function to obtain the detail data of the realm.
      Parameters: (realm name), (field='classname')

  3)  Use the return value of generateAuctionStatus to plot.

'''

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
def generateWorkingData(realm_name, start_date, end_date):
  # check if the file exis first
  dirpath = working_dir + start_date + '-' + end_date + '/'
  if not os.path.isdir(dirpath):
    os.makedirs(dirpath)
  if os.path.isfile(dirpath + realm_name+'_alliance.csv'):
    print dirpath+realm_name+'_alliance(horde).csv is already existed.'
    return
  print 'Generating working data of', realm_name, '...'
  collectRealmData(realm_name)
  createCopyOfCSV(realm_name)
  mergeSameAuction(realm_name, start_date, end_date)
  print 'Finished generating working data.\n'

def plotAuctionSignature(realmlist, fraction, start_date, end_date):
  for realm in realmlist:
    auction = generateAuctionStatus(realm, fraction, start_date, end_date)
    auction.plot(kind='bar', title=realm)
  plt.show()
  


'''
# argv1: field(ex: qualityname), 
for name in ['tichondrius', 'illidan', 'frostmourne', 'stormrage', 'area-52']:
#for name in ['the-venture-co', 'gallywix', 'tol-barad', 'ravenholdt', 'the-scryers']:
  realm = generateAuctionStatus(name+description, sys.argv[1])
  realm.plot(kind='bar', title=name)
plt.show()
'''
