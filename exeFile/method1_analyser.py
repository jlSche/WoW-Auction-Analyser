#-*-:encoding=utf-8
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
def getHighCorrItem(auction_list,threshold=0.7):
    result_df = DataFrame(columns=['Realm', 'Fraction','Item ID', 'Corr'])
    for fraction in fractionlist:
        for auction_name in auction_list:
            auction = read_csv(corr_dir + auction_name + fraction) 
            auction = auction[(auction['Corr'] > threshold ) | (auction['Corr'] < -threshold)]
            auction['Realm'] = auction_name
            auction['Fraction'] = fraction[1:]
            result_df = result_df.append(auction, ignore_index=True)
   
    # need only the top 8 population realms from pvp and pve
    realms_detail = read_csv('../sourceDir/target_realm.dat') 
    result_df = result_df.merge(realms_detail, on=['Realm'], how='left')
    
    # generate complete information of high corr items
    itemlist = read_csv('../sourceDir/itemlist.csv')
    result_df = result_df.merge(itemlist, on=['Item ID'], how='left')

    result_df.to_csv('../corr_result/HighCorr/ItemsDetail75.csv', index=False)

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


#########################################################################
# Return the occurence of each high-corr items
#########################################################################
def returnItemOccurence():
    df = read_csv('../corr_result/HighCorr/ItemsDetail.csv')
    
    '''
    p_a = df[(df['pvp']=='pvp') & (df['Fraction']=='alliance')]
    p_h = df[(df['pvp']=='pvp') & (df['Fraction']=='horde')]
    e_a = df[(df['pvp']=='pve') & (df['Fraction']=='alliance')]
    e_h = df[(df['pvp']=='pve') & (df['Fraction']=='horde')]
    
    for realm_type in [p_a, p_h, e_a, e_h]:
    '''
        ##########################################################
        # find occurence of each cluster
        ##########################################################
    item_dict = {}
    for idx in range(0, len(df)):
        itemid = df.iloc[idx]['Item ID']
        if item_dict.has_key(itemid):
            item_dict[itemid] += 1
        else:
            item_dict[itemid] = 1
   
    #print realm_type.iloc[0]['pvp'],realm_type.iloc[0]['Fraction'],': (len):',len(item_dict)
    for key, val in item_dict.items():
        if val > 1:
            print int(key), 'shows up', val, 'times in', df[df['Item ID']==key].iloc[0]['Realm'], df[df['Item ID']==key].iloc[0]['Fraction'], 'and', df[df['Item ID']==key].iloc[1]['Realm'], df[df['Item ID']==key].iloc[1]['Fraction'] 



def analysisArmor():
    all_items = read_csv('../corr_result/HighCorr/ItemsDetail.csv')
    armor_detail = read_csv('../corr_result/HighCorr/armorDetail_new.dat')

    armor = all_items[all_items['classname']=='Armor']
    armor_detail = armor_detail.merge(armor, on=['Item ID'], how='inner').drop_duplicates().reset_index()

    # items used for enchanting
    enchanting = armor_detail[(armor_detail['Usage']=='飾品')|(armor_detail['Usage']=='手指')|(armor_detail['Usage']=='頸部')]
    
    # items used for style
    style = armor_detail[(armor_detail['Usage']!='飾品')&(armor_detail['Usage']!='手指')&(armor_detail['Usage']!='頸部')]
    
    realms = set(style['Realm'].tolist())
    
    for realm in realms:
        print realm,
        df = style[style['Realm']==realm]
        print '\nalliance:', len(df[df['Fraction']=='alliance']), '\t horde:', len(df[df['Fraction']=='horde'])

    for realm in realms:
        print realm,
        df = enchanting[enchanting['Realm']==realm]
        print '\nalliance:', len(df[df['Fraction']=='alliance']), '\t horde:', len(df[df['Fraction']=='horde'])
    return  
    subclass = armor.groupby('qualityname').size().reset_index()
    return subclass

    return armor

#   看四大類拍賣場,是否有各自有 同類型的指標商品
def analysisCluster():
    df = read_csv('../corr_result/HighCorr/ItemsDetail.csv')
    
    #df = df.ix[:,['classname','Realm','Fraction','pvp']].drop_duplicates()
    p = df[(((df['Realm']=='illidan')&(df['Fraction']=='alliance'))|((df['Realm']=='kelthuzad')&(df['Fraction']=='horde'))|((df['Realm']=='sargeras')&(df['Fraction']=='horde')))]
    return p
    #e = df[(df['pvp']=='pve')]
    '''
    p_a = df[(df['pvp']=='pvp') & (df['Fraction']=='alliance')]
    p_h = df[(df['pvp']=='pvp') & (df['Fraction']=='horde')]
    e_a = df[(df['pvp']=='pve') & (df['Fraction']=='alliance')]
    e_h = df[(df['pvp']=='pve') & (df['Fraction']=='horde')]
    '''
    classlist = ['Consumable', 'Container', 'Weapon', 'Gem', 'Armor', 'Projectile', 'Trade Goods', 'Book', 'Money', 'Quest', 'Key', 'Junk', 'Glyph', 'Caged Pet']
    #for cluster in [p_a, p_h, e_a, e_h]:
    for cluster in [p]:
        #print '\n',cluster.iloc[0]['pvp'], cluster.iloc[0]['Fraction']
        print '\n',cluster.iloc[0]['pvp']
        for category in classlist:
            print category, len(cluster[cluster['classname']==category])

###############################################################################        
# get target realms
###############################################################################        
def getTargetRealms(return_columns='Realm'):
    realms = read_csv('../sourceDir/target_realm.dat')
    
    realms = realms[realms['pvp']=='pvp'][:8]['Realm'].tolist() + realms[realms['pvp']=='pve'][:8]['Realm'].tolist()
    return realms
    #elif return_columns == 'all':
    #    realms = realms[realms['pvp']=='pvp'][:8] + realms[realms['pvp']=='pve'][:8]




