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

fields_name = 'Realm Name,Export Time,PMktPrice Date,Reserved,Item ID,Item Name,AH MarketPrice Coppers,AH Quantity,AH MarketPrice,AH MinimumPrice,14-day Median Market Price,Median Market Price StdDev,14-day Todays PMktPrice,PMktPrice StdDev,Daily Price Change,Avg Daily Posted,Avg Estimated Daily Sold,Estimated Demand\n' 
fields_name = fields_name.replace(' ', '_')

source_dir = '../sourceDir/'
working_dir = '../workingDir/'
corr_dir = '../corr_result/'
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

'''
    Collect those items with corr value together, and write them to file('../corr_result/HighCorr').
'''
def getHighCorrItem(auction_list,threshold=0.9):
    result_df = DataFrame(columns=['Realm', 'Fraction','Item ID', 'Corr'])
    for fraction in fractionlist:
        for auction_name in auction_list:
            auction = read_csv(corr_dir + auction_name + fraction) 
            auction = auction[(auction['Corr'] >= threshold ) | (auction['Corr'] <= -threshold)]
            auction['Realm'] = auction_name
            auction['Fraction'] = fraction[1:]
            result_df = result_df.append(auction, ignore_index=True)
    
    realms_detail = read_csv('../sourceDir/target_realm.dat') 
    result_df = result_df.merge(realms_detail, on=['Realm'], how='left')
    result_df.to_csv('../corr_result/HighCorr/allRealms.csv', index=False)

'''
    Find the intersection items in given auction_list.
'''
def getIntersection(auction_list):
    duplicate = auction_list[0]
    for idx in range(1, len(auction_list)-1, 1):
        duplicate = list(set(duplicate).intersection(auction_list[idx]))
    return duplicate


def analysis(corr_result):
    new_df = corr_result.rename(columns={'Item ID':'Item_ID'}, inplace=False)
    detail = new_df.merge(itemlist, how='left', on='Item_ID')

    quality_amount = []
    class_amount = []
    for quality in qualitylist:
        quality_amount.append(len(detail[detail['qualityname']==quality]))

    for class_name in classlist:
        class_amount.append(len(detail[detail['classname']==class_name]))

    return quality_amount, class_amount
















