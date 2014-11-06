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
description = '_horde_0401-0414'

qualitylist = ['Poor', 'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Heirloom']
qualityIDlist = [0, 1, 2, 3, 4, 5, 7]
classlist = ['Consumable', 'Container', 'Weapon', 'Gem', 'Armor', 'Projectile', 'Trade Goods', 'Book', 'Money', 'Quest', 'Key', 'Junk', 'Glyph', 'Caged Pet']
classIDlist = [0, 1, 2, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 17]
fractionlist = ['_alliance', '_horde']

#########################################################################################################
# Merge with the merge_with field first, take sum after you group data by merge_with field
# Return the normalized datafram. The return value can be used to plot  
#########################################################################################################
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
# the function belowed can be ignored.
###############################################################################################################

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
