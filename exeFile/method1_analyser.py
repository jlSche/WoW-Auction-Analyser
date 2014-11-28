from pandas import *
import numpy as np
import os
import DataHandling
import DataPreprocess

collectedDate_list = ['0314-0316', '0317-0319', '0320-0327', '0328-0407', '0408-0423', '0424-0514', '0515-0605', '0606-062702', '062714-0717', '0718-0807', '0808-082602', '082614-0918', '0919-1013']
fractionlist = ['_alliance', '_horde']
qualitylist = ['Poor', 'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Heirloom']
qualityIDlist = [0, 1, 2, 3, 4, 5, 7]
classlist = ['Consumable', 'Container', 'Weapon', 'Gem', 'Armor', 'Projectile', 'Trade Goods', 'Book', 'Money', 'Quest', 'Key', 'Junk', 'Glyph', 'Caged Pet']
classIDlist = [0, 1, 2, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 17]
fractionlist = ['_alliance', '_horde']

fields_name = 'Realm Name,Export Time,PMktPrice Date,Reserved,Item ID,Item Name,AH MarketPrice Coppers,AH Quantity,AH MarketPrice,AH MinimumPrice,14-day Median Market Price,Median Market Price StdDev,14-day Todays PMktPrice,PMktPrice StdDev,Daily Price Change,Avg Daily Posted,Avg Estimated Daily Sold,Estimated Demand\n' 
fields_name = fields_name.replace(' ', '_')

source_dir = '../sourceDir/'
working_dir = '../workingDir/'
corr_dir = '../corr/'
# comment three lines below if the data are in local computer
'''
usb_mode = '/Volumes/TOSHIBA/'
source_dir = usb_mode + source_dir[3:]
working_dir = usb_mode + working_dir[3:] + '0313-1012/'
'''
pop_dir = source_dir + 'population/'
auction_dir = source_dir + 'auctionData/'
csv_dir = source_dir + 'csvFile/'
itemlist = read_csv(source_dir+'itemlist.csv')

def getAuctionList(time='0411'):
	pve_top = DataHandling.getRealmsList('0411',ascending_order=False,PvP='PvE')
	pve_low = DataHandling.getRealmsList('0411',ascending_order=True,PvP='PvE')

	pvp_top = DataHandling.getRealmsList('0411',ascending_order=False,PvP='PvP')
	pvp_low = DataHandling.getRealmsList('0411',ascending_order=True,PvP='PvP')
	return pve_top, pve_low, pvp_top, pvp_low

'''
	Return a list of dataframes that contain high correlation item for each auction.
'''
def getHighCorrItem(auction_list, threshold=0.8):
	result_df = []
	for auction_name in auction_list:
	    auction = read_csv(corr_dir + auction_name + '_alliance.csv')
	    auction = auction[(auction['Corr'] > 0.8 ) | (auction['Corr'] < -0.8)]
	    id_list = auction['Item ID']
	    result_df.append(id_list)
	return result_df

'''
	Find the intersection items in given auction_list.
'''
def getIntersection(auction_list):
	duplicate = auction_list[0]
	for idx in range(1, len(auction_list)-1, 1):
	    duplicate = list(set(duplicate).intersection(auction_list[idx]))