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
working_dir = '../workingDir/0313-1012/'
# comment three lines below if the data are in local computer
'''
usb_mode = '/Volumes/TOSHIBA/'
source_dir = usb_mode + source_dir[3:]
working_dir = usb_mode + working_dir[3:] + '0313-1012/'
'''
pop_dir = source_dir + 'population/'
auction_dir = source_dir + 'auctionData/'
csv_dir = source_dir + 'csvFile2015/'
itemlist = read_csv(source_dir+'itemlist.csv')

reading_dir = '0313-1012/temp/'
def method1(auction_list, date_start='2014-03-13', date_end='2014-10-12'):
    for fraction in fractionlist:
        auction_profit = DataFrame(columns=['Realm','Fraction','Week Num','Profit'])
        for auction_name in auction_list:
            auction = read_csv(working_dir + auction_name + fraction + '.csv')

            # time range
            auction = DataHandling.getTimeRangeData(auction,start=date_start,end=date_end)
            
            # add 'Week Num' column
            auction['Week Num'] = auction['PMktPrice Date'].apply(DataHandling.toWeekNumber)
             
            # temp_auction is used for doing remove outliers of weekly item price
            temp_auction = DataHandling.removeUselessColumns(auction, remain_columns=['Item ID','Week Num','AH MarketPrice'])
            auction = DataHandling.removeUselessColumns(auction, remain_columns=['Item ID','Week Num','AH Quantity'])
            temp_auction = DataHandling.removeOutlierOfDailyPrice(temp_auction)
            auction = auction.merge(temp_auction, on=['Item ID','Week Num'],right_index=True,left_index=True)
            
            # get profit of each item, the calItemsProfit will generate 'Profit' column
            auction = DataHandling.calItemsProfit(auction)

            # drop duplicates 
            auction.drop_duplicates(inplace=True)
            
            # group auction by 'week number' and 'item id'
            auction = auction.ix[:, ['Week Num','Item ID','AH Quantity','Profit', 'AH MarketPrice']]
            grouped_auction = auction.groupby(['Week Num','Item ID'], as_index=False)

            # get "mean of item weekly quantity"
            item_q_weekly_mean = grouped_auction['AH Quantity'].mean()
            
            # get "mean of item weekly profit"
            item_profit_weekly_mean = grouped_auction['Profit'].mean()

            # get "mean of item weekly price"
            item_price_weekly_mean = grouped_auction['AH MarketPrice'].mean()
           
            # generate auction detail file, columns contain (Week Num, Item ID, Avg Daily Posted, AH MarketPrice)
            auction_detail = item_q_weekly_mean.merge(item_price_weekly_mean) 
            auction_detail.to_csv('../corr_result/auction_detail/' + auction_name + fraction, index=False)

            # get "realm's weekly profit"
            realm_weekly_profit = item_profit_weekly_mean.groupby(['Week Num'])['Profit'].sum()
            realm_weekly_profit = DataFrame(realm_weekly_profit, columns=['Profit']).reset_index()
           
            auction = item_q_weekly_mean.merge(realm_weekly_profit) 

            # gathering data for building auction_profit dataframe.            
            realm_weekly_profit['Realm'] = auction_name
            realm_weekly_profit['Fraction'] = fraction[1:]
            auction_profit = auction_profit.append(realm_weekly_profit, ignore_index=True)
            
            # get all item id show up in that realm
            # put the code here note outside for loop because items show up in each realm may be different
            temp_id_list = auction['Item ID']
            temp_id_list = temp_id_list.drop_duplicates()
            id_list = temp_id_list.tolist()
             
            # get correlation coefficient between "item's mean daily posted" and "auction weekly profit" for each item.
            # item shows up at least 10 of 30 weeks will be recorded.
            item_corr_df = DataFrame(columns=['Item ID','Corr'])
            for item in id_list:
                temp_item = auction[auction['Item ID']==item]
                occurence_count = len(temp_item)
                if occurence_count >= 15:
                    corr = np.corrcoef(x=temp_item['AH Quantity'], y=temp_item['Profit'])
                    new_corr = DataFrame([{'Item ID':item, 'Corr':corr[0][1]}])
                    item_corr_df = item_corr_df.append(new_corr, ignore_index=True)
            item_corr_df.to_csv('../corr_result/'+auction_name+fraction, index=False)
            
            print 'finish',auction_name+fraction,'...'
            
        auction_profit.to_csv('../corr_result/'+fraction[1:]+'_profit.csv', index=False, header=False, mode='a')
    


