from pandas import *
import numpy as np
import os
import DataHandling
import DataPreprocess
import method1_analyser

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
def generateMethod2Material(auction_list, date_start='2014-04-01', date_end='2014-04-07'):
    for auction_name in auction_list:
        auction = read_csv(working_dir + reading_dir + auction_name + '_alliance.csv')

        # trim date range to a specific week (a week that does not encounter realm connection)
        # need not to generate week num column
        auction = DataHandling.getTimeRangeData(auction, start=date_start, end=date_end)
        
        # create temp_auction dataframe in order to do outlier detection
        temp_auction = DataHandling.removeUselessColumns(auction, remain_columns=['Item ID','AH MarketPrice'])
        auction = DataHandling.removeUselessColumns(auction, remain_columns = ['Item ID','Avg Daily Posted'])

        # remove outlier of item price
        temp_auction = temp_auction.groupby(['Item ID'], as_index=False)
        temp_auction = temp_auction.apply(DataPreprocess.removeOutliers)

        auction = auction.merge(temp_auction,on=['Item ID'],right_index=True,left_index=True)
        
        # calculate profit
        auction = DataHandling.calItemsProfit(auction)
        auction.drop_duplicates(inplace=True)

        #merge all datafrme together
        grouped_auction = auction.groupby(['Item ID'], as_index=False)

        # get "item weekly quantity"
        item_q_weekly_mean = grouped_auction['Avg Daily Posted'].mean()

        # get "totoal profit of a week"
        item_profit_weekly_mean = grouped_auction['Profit'].mean()
        realm_weekly_profit = item_profit_weekly_mean['Profit'].sum()

        item_q_weekly_mean['Realm Profit'] = realm_weekly_profit
        item_q_weekly_mean.to_csv('../method2/'+date_start+'_'+auction_name, index=False)
        print 'finished',auction_name,'...'

'''
# Return auction_list and item_list.
# auction_list contains a dataframe composed by {item id, avg daily posted, realm profit}
# item_list contains all item appear in realm_list
'''
def generateAuctionAndItemList(realm_list, date='2014-04-01'):
    #read all csv file first
    #generate a itemlist that contains all item appear in realm_list
    auction_list = []
    item_list = []
    for realm in realm_list:
        auction = read_csv('../method2/'+date+'_'+realm)
        auction_list.append(auction)

        item_id_list = auction['Item ID']
        item_id_list.drop_duplicates()
        item_id_list = item_id_list.tolist()
        item_list.append(item_id_list)

    item_list = getUnion(item_list)        
    return auction_list, item_list


def generateMethod2Corr(realm_list, auction_list, item_list, date='2014-04-01'):
    item_corr_df = DataFrame(columns=['Item ID','Corr'])
    for item in item_list:
        result_df = DataFrame(columns=['Item Quantity','Realm Profit'])
        for idx in range(0, len(auction_list), 1):
            # skip this auction if no this kind of item
            auction = auction_list[idx]
            _item = auction[auction['Item ID']==item]
            if len(_item) == 0:
                continue

            _quantity = _item.iat[0,1]
            _realm_profit = _item.iat[0,2]
            new_df = DataFrame([{'Item Quantity':_quantity,'Realm Profit':_realm_profit}])
            result_df = result_df.append(new_df,ignore_index=True)

        if len(result_df) > 3:
            corr = np.corrcoef(x=result_df['Item Quantity'], y=result_df['Realm Profit'])
            new_corr = DataFrame([{'Item ID':item, 'Corr':corr[0][1]}])
            item_corr_df = item_corr_df.append(new_corr, ignore_index=True)

    item_corr_df.to_csv('../method2/method2_result',index=False)
        


def getHighCorrItem(filename, date='2014-04-01'):
    df = read_csv('../method2/'+filename)
    df = df[(df['Corr'] > 0.8) | (df['Corr'] < -0.8)]
    return df['Item ID']


def getUnion(realm_list):
    df = realm_list[0]
    for idx in range(1, len(realm_list)-1, 1):
        df = list(set(df) | set(realm_list[idx]))
    return df



