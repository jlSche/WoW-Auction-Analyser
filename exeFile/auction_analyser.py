#-*- coding=utf-8
from pandas import *
import os

def getAuctionComposing():
    itemlist = read_csv('../sourceDir/itemlist.csv')
    high_corr_items = read_csv('../corr_result/HighCorr/allRealms.csv')
    realms_composing = []
    for auction in os.listdir('../corr_result/auction_detail/'):
        df = read_csv('../corr_result/auction_detail/'+auction)
        df = df.merge(itemlist, left_on='Item ID', right_on='Item_ID',how='left')

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
       
        '''
        ######################################################################################################
            #   下面區塊程式碼將會計算每一伺服器在這半年期間，在指標性商品中（裝甲，不常見）這類別的商品，
                一個禮拜平均出現的數量
        ######################################################################################################
        df = df[(df['classname']=='Armor') & (df['qualityname']=='Uncommon')]

        splitted_str = auction.split('_')
        realm = splitted_str[0]
        fraction = splitted_str[1]

        eco_items = high_corr_items[(high_corr_items['Realm']==realm) & (high_corr_items['Fraction']==fraction)]
        eco_items = eco_items.merge(df, on='Item ID', how='left')

        print auction,':'
        eco_items = eco_items.ix[:,['Item_Name','AH Quantity']]
        eco_items = eco_items.groupby(['Item_Name']).mean()
        print eco_items
        print '\n'
        ''' 
       





    

