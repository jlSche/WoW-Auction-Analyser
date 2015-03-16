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
       
######################################################################################################
#indivudual : AH Quantity, AH MarketPrice
#market     : AH Quantity, Profit
# 找出 某樣商品的價或是量 與 拍賣場的量或是景氣 呈現高相關的物品
# 尚未檢查
######################################################################################################
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

        # group auction to get weekly market information
        if market == profit:
            auction['Profit'] = auction['AH Quantity']*auciton['AH MarketPrice']
        market_weekly = auction.groupby(['Week Num'],as_index=False)[market].sum()

        for itemid in set(eco_items['Item ID']):
            item_weekly = auction[auction['Item ID']==int(itemid)].ix[:,['Week Num',individual]]
            item_weekly = item_weekly.merge(market_weekly,on=['Week Num'],how='left')

            # if both individual and market variable are AH Quantity, add some words to their end
            if market == individual:
                individiual += '_x'
                market += '_y'

            corr = np.corrcoef(x=item_weekly[market],y=item_weekly[individual])
            if (corr[0][1] > 0.7) or (corr[0][1]<-0.7):
                matched_item = DataFrame([{'Realm': realm,'Fration': fraction,'Item ID': int(itemid),'Corr': corr[0][1]}])
                matched_df = matched_df.append(matched_item,ignore_index=True)
                print 'item', int(itemid), 'in', realm, fraction, 'also has high correlation with market quantity with corr value ',corr[0][1]
    
    matched_df.to_csv('../corr_result/HighCorr/'+individual+'CorrWithMarket'+market,index=False)



######################################################################################################
# check the population, economic poverty status of all auctions
# return those auction has least population and least poverty
######################################################################################################
def getWorstAuction():
    target_realms = read_csv('../sourceDir/target_realm.dat')
    pvp = target_realms[target_realms['pvp']=='pvp'][:8]
    pve = target_realms[target_realms['pvp']=='pve']
    pop_auctions = pvp.append(pve,ignore_index=True)

    alliance = read_csv('../corr_result/alliance_profit.csv')
    horde = read_csv('../corr_result/horde_profit.csv')
    poverty_auctions = alliance.append(horde,ignore_index=True)
    
    # sort the auctions with population
    pop_alliance = pop_auctions.sort(columns=['alliance'])
    pop_horde = pop_auctions.sort(columns=['horde'])

    # sort the auctions with poverty
    poverty = poverty_auctions.groupby(['Realm','Fraction'])['Profit'].mean()
    poverty = poverty.reset_index().sort(columns=['Profit'])

    return pop_alliance[:10], pop_horde[:10], poverty

###################################################################################
# 看除了armor外,是否還有某一class是每一個拍賣場都會有的
###################################################################################
def getEcoItemsComposing():
    df = read_csv('../corr_result/HighCorr/ItemsDetail75.csv')
    realms = read_csv('../sourceDir/target_realm.dat')
    #realms = realms[realms['pvp']=='pvp'][:8]['Realm'].tolist() + realms[realms['pvp']=='pve']['Realm'].tolist()
    

    df = df.groupby(['classname','Realm','Fraction']).size().reset_index()
    for itemclass in set(df['classname']):
        print itemclass,'shows up in',len(df[df['classname']==itemclass])
    
####################################################################################
# 檢驗經濟體人口與 裝甲類型指標商品、指標商品 數量 的相關性
###################################################################################   
def getCorr():
    all_df = read_csv('../corr_result/HighCorr/ItemsDetail.csv')
    armor_df = read_csv('../corr_result/HighCorr/03pricedata.csv')

    t_all = all_df.groupby(['Realm','Fraction']).size()
    t_armor = armor_df.groupby(['Realm','Fraction']).size()

    t_all = t_all.reset_index()
    t_armor = t_armor.reset_index()
    
    t_all.rename(columns={0: 'all'}, inplace=True)
    t_armor.rename(columns={0: 'armor'}, inplace=True)

    t_df = t_armor.merge(t_all,how='outer',on=['Realm','Fraction'])

    pop = armor_df.ix[:,['Realm','Fraction','alliance','horde']].drop_duplicates()
    t_df = t_df.merge(pop)

    pop_list = []
    for i, row in t_df.iterrows():
        if row['Fraction'] == 'alliance':
            pop_list.append(row['alliance'])
        else:
            pop_list.append(row['horde'])

    t_df['pop'] = pop_list
    t_df.drop(['alliance','horde'], axis=1, inplace=True)
    t_df.loc[len(t_df)+1] = ['illidan','alliance',0,1,8654]
    t_df.loc[len(t_df)+1] = ['kelthuzad','horde',0,1,12691]
    t_df.loc[len(t_df)+1] = ['sargeras','horde',0,10,16191]

    corr1 = np.corrcoef(x=t_df['pop'], y=t_df['armor'])
    corr2= np.corrcoef(x=t_df['pop'], y=t_df['all'])
    print corr1[0][1],corr2[0][1]


