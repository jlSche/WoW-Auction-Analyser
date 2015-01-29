#-*- coding=utf-8
from pandas import *
import os

def getAuctionComposing():
    itemlist = read_csv('../sourceDir/itemlist.csv')
    high_corr_items = read_csv('../corr_result/HighCorr/ItemsDetail.csv')
    realms_composing = []
    for auction in os.listdir('../corr_result/auction_detail/'):
        df = read_csv('../corr_result/auction_detail/'+auction)
        #df = df.merge(itemlist, on='Item ID', how='left')
        
        '''
        ######################################################################################################
            #   下面區塊程式碼將會計算每一伺服器在這半年期間，市場上每一種類別的商品平均一個禮拜出現的次數
        ######################################################################################################
        grouped_week = df.groupby(['Week Num','classname','qualityname']).size() 
        if (auction =='kiljaeden_alliance') or (auction=='frostmourne_alliance') or (auction=='thrall_alliance') or (auction=='wyrmrest-accord_alliance') or (auction=='bleeding-hollow_horde'):
            print auction+':'
            grouped_week = grouped_week.reset_index()
            grouped_week.rename(columns={0: 'count'}, inplace=True)
            grouped_week = grouped_week.ix[:,['classname','qualityname','count']]
            categroy_mean_q = grouped_week.groupby(['classname','qualityname']).mean()
            print caeogry_mean_q
        '''
       
        #'''
        ######################################################################################################
            #   下面區塊程式碼將會計算每一伺服器在這半年期間，在指標性商品中（裝甲，不常見）這類別的商品，
            #   一個禮拜平均出現的數量
        ######################################################################################################
        splitted_str = auction.split('_')
        realm = splitted_str[0]
        fraction = splitted_str[1]

        # high corr items in this auction
        eco_items = high_corr_items[(high_corr_items['Realm']==realm) & (high_corr_items['Fraction']==fraction)]

        # weekly data of high corr items in this auction
        eco_items = eco_items.merge(df, on=['Item ID'], how='left')
        #print 'allHighCorr', len(high_corr_items), 'high corr in this auction', len(eco_items)
        #return eco_items
        eco_items = eco_items[(eco_items['classname']=='Armor') & (eco_items['qualityname']=='Uncommon')]

        eco_items = eco_items.ix[:,['Item Name','AH Quantity']]
        eco_items = eco_items.groupby(['Item Name']).mean()
        realms_composing.append(eco_items)
        #''' 
    return realms_composing
       
#indivudual : AH Quantity, AH MarketPrice
#market     : AH Quantity, Profit
def isCorrWithMarketQuantity(classname='Armor',qualityname='Uncommon',individual='AH Quantity',market='AH Quantity'):
    high_corr_items = read_csv('../corr_result/HighCorr/ItemsDetail.csv')

    matched_df = DataFrame(columns=['Realm','Fration','Item ID','Corr'])
    for name in os.listdir('../corr_result/auction_detail/'):
        auction = read_csv('../corr_result/auction_detail/'+name)

        # get realm and fraction
        splitted_str = name.split('_')
        realm = splitted_str[0]
        fraction = splitted_str[1]
        eco_items = None        

        if classname=='all':
            ######################################################################################################
            #   所有 數量與拍賣場物品數量呈高度相關的eco_items
            ######################################################################################################
            eco_items = high_corr_items[(high_corr_items['Realm']==realm)&(high_corr_items['Fraction']==fraction)]
        
        else:
        ######################################################################################################
            #   所有 數量與拍賣場物品數量呈高度相關
            #   且屬於(armor,uncommon)的eco_items
        ######################################################################################################
            eco_items = high_corr_items[(high_corr_items['Realm']==realm)&(high_corr_items['Fraction']==fraction)&(high_corr_items['classname']==classname)&(high_corr_items['qualityname']==qualityname)]

        # group auction to get weekly market quantity
        # if market == profit, need to calculate profit
        market_weekly = auction.groupby(['Week Num'],as_index=False)[market].sum()

        for itemid in set(eco_items['Item ID']):
            item_weekly = auction[auction['Item ID']==int(itemid)].ix[:,['Week Num',individual]]

            item_weekly = item_weekly.merge(market_weekly,on=['Week Num'],how='left')

            # if both are AH Quantity, change to xx_x, xx_y
            #corr = np.corrcoef(x=item_weekly_quantity['AH Quantity_x'],y=item_weekly_quantity['AH Quantity_y'])
            corr = np.corrcoef(x=item_weekly[market],y=item_weekly[individual])
            if (corr[0][1] > 0.7) or (corr[0][1]<-0.7):
                matched_item = DataFrame([{'Realm': realm,'Fration': fraction,'Item ID': int(itemid),'Corr': corr[0][1]}])
                matched_df = matched_df.append(matched_item,ignore_index=True)
                print 'item', int(itemid), 'in', realm, fraction, 'also has high correlation with market quantity with corr value ',corr[0][1]
    
    matched_df.to_csv('../corr_result/HighCorr/priceCorrWithMarketQuantity.csv',index=False)





    

