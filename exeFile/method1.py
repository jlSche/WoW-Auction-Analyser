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

reading_dir = '0313-1012/temp/'
for auction_name in os.listdir(working_dir + reading_dir):
    auction = read_csv(working_dir + reading_dir + auction_name)

    auction = DataHandling.getTimeRangeData(auction,start='2014-04-01',end='2014-04-21')
    auction['Week Num'] = auction['PMktPrice Date'].apply(DataHandling.toWeekNumber)
    
    # temp_auction is used for doing remove outliers of item price
    temp_auction = DataHandling.removeUselessColumns(auction, remain_columns=['Item ID','Week Num','AH MarketPrice'])
    auction = DataHandling.removeUselessColumns(auction, remain_columns=['Item ID','Week Num','Avg Daily Posted'])
    temp_auction = DataHandling.removeOutlierOfDailyPrice(temp_auction)
    auction = auction.merge(temp_auction, on=['Item ID','Week Num'],right_index=True,left_index=True)
    
    # get profit of each item, and then drop duplicates
    auction = DataHandling.calItemsProfit(auction)
    auction.drop_duplicates(inplace=True)
    
    # group auction by 'week number' and 'item id'
    auction = auction.ix[:, ['Week Num','Item ID','Avg Daily Posted','Profit']]
    grouped_auction = auction.groupby(['Week Num','Item ID'], as_index=False)

    # get "item weekly quantity"
    item_q_weekly_mean = grouped_auction['Avg Daily Posted'].mean()

    # get "totoal profit of a week"
    item_profit_weekly_mean = grouped_auction['Profit'].mean()
    realm_weekly_profit = item_profit_weekly_mean.groupby(['Week Num'])['Profit'].sum()
    item_weekly_profit = DataFrame(realm_weekly_profit, columns=['Profit']).reset_index()
    
    auction = item_q_weekly_mean.merge(item_weekly_profit)
    
    # get all item id show up in that realm
    temp_id_list = auction['Item ID']
    temp_id_list = temp_id_list.drop_duplicates()
    id_list = temp_id_list.tolist()
    
    # get correlation coefficient between "item's mean daily posted" and "auction weekly profit"
    item_corr_df = DataFrame(columns=['Item ID','Corr'])
    for item in id_list:
        temp_item = auction[auction['Item ID']==item]
        corr = np.corrcoef(x=temp_item['Avg Daily Posted'], y=temp_item['Profit'])
        new_corr = DataFrame([{'Item ID':item, 'Corr':corr[0][1]}])
        item_corr_df = item_corr_df.append(new_corr, ignore_index=True)
    item_corr_df.to_csv('../corr/'+auction_name, index=False)