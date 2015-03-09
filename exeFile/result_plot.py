#-*- encoding=utf-8
from pandas import *
import numpy as np
from mpl_toolkits.axes_grid1 import host_subplot
from matplotlib.backends.backend_pdf import PdfPages
from DataHandling import convertDateFormat
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt
import os
import sys


auction_list = read_csv('../sourceDir/target_realm.dat')
auction_name = auction_list['Realm']
item_list = read_csv('../sourceDir/itemlist.csv')

###################################################################################
# the profit trend of each auction
###################################################################################
def plotAuctionProfit():
    alliance = read_csv('../corr_result/alliance_profit.csv')
    horde = read_csv('../corr_result/horde_profit.csv')
    realms = read_csv('../sourceDir/target_realm.dat')
    realms = realms[realms['pvp']=='pvp'][:8]['Realm'].tolist() + realms[realms['pvp']=='pve'][:8]['Realm'].tolist()
    #pp = PdfPages('../corr_result/fig/auctionProfitTrend.pdf')

    patch_dates = [convertDateFormat('06/27/2014')]#,convertDateFormat('10/14/2014')]
    patch_dates = [Timestamp(x).week for x in patch_dates]
    
    for df in [alliance, horde]:
        for name in realms:
            auction = df[df['Realm']==name]
            
            fig, ax = plt.subplots()

            ax.plot(auction['Week Num'].tolist(), auction['Profit'].tolist(), label='Proft Trend', marker='o')
            ax.set_xlim([min(auction['Week Num'].tolist()), max(auction['Week Num'].tolist())])
            ax.set_xticks(auction['Week Num'].tolist())
            
            ax.set_title(auction.iloc[0]['Realm']+' '+auction.iloc[0]['Fraction'])
            ax.annotate('patch',xy=(patch_dates[0],int(auction[auction['Week Num']==patch_dates[0]]['Profit'])), xytext=(patch_dates[0],(max(auction['Profit'])+min(auction['Profit']))/2), arrowprops=dict(facecolor='black', shrink=0.05))

            plt.xlabel('Week Number')
            plt.ylabel('Market Value')

            plt.draw()
            #plt.savefig(pp, format='pdf')
            plt.savefig('../corr_result/fig/auctionTrend/'+auction.iloc[0]['Realm']+' '+auction.iloc[0]['Fraction']+'.png', format='png')
    #pp.close()

def plotCorrelation(name='darkspear', fraction='alliance', attr=['Avg Daily Posted','Profit','AH MarketPrice']):
    high_corr_items = read_csv('../corr_result/HighCorr/'+fraction)
    high_corr_items = high_corr_items[high_corr_items['Realm']==name]
    high_corr_items = high_corr_items.ix[:,['Item ID','Corr']]
    print name, '\'s', fraction, 'has', len(high_corr_items), 'high corr items.'
    
    # prepare the data of high corr
    auction_data = read_csv('../corr_result/auction_detail/'+name+'_'+fraction)
    auction_profit = read_csv('../corr_result/'+fraction+'_profit.csv') 
    target_auction = auction_profit[(auction_profit['Realm']==name)]
    auction_detail = auction_data.merge(target_auction, how='inner', on=['Week Num'])
    auction_detail = auction_detail.merge(high_corr_items, how='inner', on=['Item ID']) 
    
    pp = PdfPages('../corr_result/fig/'+name+'-'+fraction+'.pdf')
    print auction_detail
    '''
    for item in high_corr_items['Item ID']:
        fig = plt.figure()
        fig.suptitle('Item ID: '+ str(item), fontsize=14)
        item_detail = auction_detail[auction_detail['Item ID']==item]
        week_list = list(item_detail['Week Num'])
        quantity_list = list(item_detail['Avg Daily Posted'])
        profit_list = list(item_detail['Profit'])
    
        host = host_subplot(111, axes_class=AA.Axes)
        par1 = host.twinx()

        host.set_xlim(min(week_list), max(week_list))
        host.set_ylim(min(quantity_list),max(quantity_list))

        host.set_xlabel('Week Number')
        host.set_ylabel('Item Quantity')
        par1.set_ylabel('Realm Profit')

        p1, = host.plot(list(item_detail['Week Num']), quantity_list, label='Item Quantity', marker='o')
        p2, = par1.plot(list(item_detail['Week Num']), profit_list, label='Realm Profit', marker='o')

        par1.set_ylim(min(profit_list),max(profit_list))
        
        host.legend()

        host.axis['left'].label.set_color(p1.get_color())
        par1.axis['right'].label.set_color(p2.get_color())

        plt.draw()
        plt.savefig(pp, format='pdf')
        #plt.show()
    pp.close()
    '''


##############################################################################################
# 在四大類伺服器中，各class的eco-item的composing ratio
# 各物品類別的組成比例
##############################################################################################
def plotEconItemsComposing(_divide=None):
    high_corr_items = read_csv('../corr_result/HighCorr/ItemsDetail.csv')

    target_realms = []
    if _divide == 4:
        # p: pvp, e: pve, a: alliance, h: horde
        p_a = high_corr_items[(high_corr_items['pvp']=='pvp') & (high_corr_items['Fraction']=='alliance')]
        p_h = high_corr_items[(high_corr_items['pvp']=='pvp') & (high_corr_items['Fraction']=='horde')]
        e_a = high_corr_items[(high_corr_items['pvp']=='pve') & (high_corr_items['Fraction']=='alliance')]
        e_h = high_corr_items[(high_corr_items['pvp']=='pve') & (high_corr_items['Fraction']=='horde')]
        target_realms.append(p_a)
        target_realms.append(p_h)
        target_realms.append(e_a)
        target_realms.append(e_h)

    elif _divide == 2:
        pve = high_corr_items[(high_corr_items['pvp']=='pvp')]
        pvp = high_corr_items[(high_corr_items['pvp']=='pve')]
        target_realms.append(pvp)
        target_realms.append(pve)
    
    elif _divide == None:
        target_realms.append(high_corr_items)

    # pie plot
    #pp = PdfPages('../corr_result/fig/ItemComposingPie.pdf')
    colors = ['lime','lightcoral','white','lightyellow','yellowgreen','lightskyblue','magenta','slateblue','gold','hotpink','blueviolet']

    for realm_type in target_realms:
        df = realm_type.groupby(['classname']).size().reset_index()
        df.columns = ['classname','size']
        df['size'] = df['size'] / len(set(realm_type['Realm']))

        fig, ax = plt.subplots()
        ax.pie(df['size'].tolist(), labels=df['classname'].tolist(), colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
        if _divide == None:
            ax.set_title('Economic Items Composing')
        else:
            ax.set_title(realm_type.iloc[0]['pvp']+' '+realm_type.iloc[0]['Fraction']+ ': Item Class Distribution.')
        plt.draw()
        plt.savefig('../corr_result/fig/econItemsComposing.png', format='png')
    #pp.close()
    ''' 
    #scatter plot
    for realm_type in [p_a, p_h, e_a, e_h]:
        quality_list = list(realm_type['qualityid'])
        class_list = list(realm_type['classid'])

        ##########################################################
        # find occurence of each cluster
        ##########################################################
        item_dict = {}
        for idx in range(0, len(quality_list)):
            classid = class_list[idx]*10
            qualityid = quality_list[idx]
            itemid = classid + qualityid

            if item_dict.has_key(itemid):
                item_dict[itemid] += 1
            else:
                item_dict[itemid] = 1
        
        quality_list = []
        class_list = []
        occurrence_list = []
        for item in item_dict.items():
            _class = item[0] / 10
            _quality = item[0] % 10
            _occurrence = item[1]
            quality_list.append(_quality)
            class_list.append(_class)
            occurrence_list.append(_occurrence)
        
        print 'quality:',quality_list 
        print 'class:',class_list 
        print 'occurrence:',occurrence_list 
        
        ##########################################################
        #pp = PdfPages('../corr_result/fig/cluster_'+realm_tpye['pvp']+'_'+realm_type['Fraction'])
        fig, ax = plt.subplots()
        sizes = np.pi * (2 * np.asarray(occurrence_list)) ** 2
        colors = np.random.rand(len(quality_list))
        ax.scatter(class_list, quality_list, s=sizes, c=colors, alpha=0.5)
        
        ax.set_xlim([-1,17])
        ax.set_xticks([-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])
        ax.set_yticks([-1,0,1,2,3,4,5,6,7])

        ax.set_xlabel('Class ID', fontsize=20)
        ax.set_ylabel('Quality ID', fontsize=20)
        ax.set_title(realm_type.iloc[0]['pvp']+' '+realm_type.iloc[0]['Fraction']+ ': Item Class Distribution.')

        ax.grid(True)
        #fig.tight_layout()

        plt.draw()
        plt.savefig(pp, format='pdf')
    pp.close()
    '''

##############################################################################################
# Plot realms with same fraction in a grapgh
##############################################################################################
def plotFractionCluster(fraction='alliance', attr=['Avg Daily Posted','Profit','AH MarketPrice']):
    high_corr_items = read_csv('../corr_result/HighCorr/'+fraction)

    ##########################################################
    #positive corr
    #high_corr_items = high_corr_items[high_corr_items['Corr'] < 0]
    ##########################################################

    item_list.rename(columns={'Item_ID':'Item ID'}, inplace=True)
    high_corr_items = high_corr_items.merge(item_list, how='left', on=['Item ID'])

    quality_list = list(high_corr_items['qualityid'])
    class_list = list(high_corr_items['classid'])

    ##########################################################
    # find occurence of each cluster
    ##########################################################
    item_dict = {}
    for idx in range(0, len(quality_list)):
        classid = class_list[idx]*10
        qualityid = quality_list[idx]
        itemid = classid + qualityid

        if item_dict.has_key(itemid):
            item_dict[itemid] += 1
        else:
            item_dict[itemid] = 1
    #print item_dict
    
    quality_list = []
    class_list = []
    occurrence_list = []
    for item in item_dict.items():
        _class = item[0] / 10
        _quality = item[0] % 10
        _occurrence = item[1]
        quality_list.append(_quality)
        class_list.append(_class)
        occurrence_list.append(_occurrence)
    '''
    print quality_list 
    print class_list 
    print occurrence_list 
    '''
    ##########################################################
    #'''
    pp = PdfPages('../corr_result/fig/cluster_'+fraction+'.pdf')
    fig, ax = plt.subplots()
    sizes = np.pi * (3 * np.asarray(occurrence_list)) ** 2
    colors = np.random.rand(len(quality_list))
    ax.scatter(class_list, quality_list, s=sizes, c=colors, alpha=0.5)
    
    ax.set_xlim([-1,17])
    ax.set_xticks([-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])

    ax.set_xlabel('Class ID', fontsize=20)
    ax.set_ylabel('Quality ID', fontsize=20)
    ax.set_title('Item Class Distribution')

    ax.grid(True)
    fig.tight_layout()

    plt.draw()
    plt.savefig(pp, format='pdf')
    #plt.show()
    #'''
    #print high_corr_items
    pp.close()
    #'''


##############################################################################################
# Plot  1. plottype = composing.    how are the high corr items composed in each realms
#       2. plottype = sum.          the amount of each category in each realms
# 畫出每一拍賣場指標商品的組成
##############################################################################################
def plotEachRealmCluster(realmlist, plottype='sum'):
    high_corr_items = read_csv('../corr_result/HighCorr/ItemsDetail.csv')
    
    pp = None
    '''
    if plottype == 'composing':
        pp = PdfPages('../corr_result/fig/cluster_eachRealmComposing.pdf')
    elif plottype == 'sum':
        pp = PdfPages('../corr_result/fig/cluster_eachRealmSum.pdf')
    '''
    for fraction in ['alliance','horde']:
        for realm in realmlist:
            temp_df = high_corr_items[(high_corr_items['Realm']==realm)&(high_corr_items['Fraction']==fraction)]
            if len(temp_df) == 0:
                continue

            quality_list = list(temp_df['qualityid'])
            class_list = list(temp_df['classid'])

            ##########################################################
            # find occurence of each cluster
            ##########################################################
            item_dict = {}
            for idx in range(0, len(quality_list)):
                classid = class_list[idx]*10
                qualityid = quality_list[idx]
                itemid = classid + qualityid

                if item_dict.has_key(itemid):
                    item_dict[itemid] += 1
                else:
                    item_dict[itemid] = 1
            
            quality_list = []
            class_list = []
            occurrence_list = []
            for item in item_dict.items():
                _class = item[0] / 10
                _quality = item[0] % 10
                _occurrence = item[1]
                quality_list.append(_quality)
                class_list.append(_class)
                occurrence_list.append(_occurrence)
            ##########################################################
            
            if plottype == 'composing':
                fig, ax = plt.subplots()
                sizes = np.pi * (3 * np.asarray(occurrence_list)) ** 2
                colors = np.random.rand(len(quality_list))
                ax.scatter(class_list, quality_list, s=sizes, c=colors, alpha=0.5)
                
                ax.set_xlim([-1,17])
                ax.set_xticks([-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])
                ax.set_yticks([-1,0,1,2,3,4,5,6,7])

                ax.set_xlabel('Class ID', fontsize=20)
                ax.set_ylabel('Quality ID', fontsize=20)
                ax.set_title(realm + ' ' + fraction + '\'s Item Class Distribution') 
                ax.grid(True)
                fig.tight_layout()

                plt.draw()
                plt.savefig(pp, format='pdf')

            elif plottype == 'sum':
                temp_df = temp_df.ix[:,['classname','qualityname']]
                temp_df = temp_df.groupby(['classname','qualityname'])
                t = temp_df.size().unstack().fillna(0)
                t.plot(kind='barh',stacked=True,xlim=[0,20],title=realm+' '+fraction)
                plt.draw()
                plt.savefig('../corr_result/fig/ecoItemsTypeHist/'+realm+' '+fraction+'.png', format='png')

    #pp.close()

##############################################################################################
# 畫出四大類拍賣場指標商品的組成
##############################################################################################
def plotClusterComposing():
    high_corr_items = read_csv('../corr_result/HighCorr/ItemsDetail.csv')

    # p: pvp, e: pve, a: alliance, h: horde
    p_a = high_corr_items[(high_corr_items['pvp']=='pvp') & (high_corr_items['Fraction']=='alliance')]
    p_h = high_corr_items[(high_corr_items['pvp']=='pvp') & (high_corr_items['Fraction']=='horde')]
    e_a = high_corr_items[(high_corr_items['pvp']=='pve') & (high_corr_items['Fraction']=='alliance')]
    e_h = high_corr_items[(high_corr_items['pvp']=='pve') & (high_corr_items['Fraction']=='horde')]
    
    pp = PdfPages('../corr_result/fig/cluster_composing.pdf')

    for cluster in [p_a, p_h, e_a, e_h]:
        quality_list = list(cluster['qualityid'])
        class_list = list(cluster['classid'])

        ##########################################################
        df = cluster.ix[:,['classname','qualityname']]
        df = df.groupby(['classname','qualityname'])
        t = df.size().unstack().fillna(0)
        t.plot(kind='barh',stacked=True,xlim=[0,200],title=cluster.iloc[0]['pvp']+' '+cluster.iloc[0]['Fraction'])
        plt.draw()
        plt.savefig(pp, format='pdf')

    pp.close()

##############################################################################################
# 看各伺服器的拍賣場，是由哪些商品所組成
# not tested yet
##############################################################################################
def plotAuctionComposing(category='classname'):
    color_list = ['lightcoral','white','lightyellow','yellowgreen','lightskyblue','magenta','lightgray','gold','hotpink']
    pp = PdfPages('../corr_result/fig/auctionComposing.pdf')
    for name in os.listdir('../corr_result/auction_detail/'):
        auction = read_csv('../corr_result/auction_detail/'+name)
        auction = auction.merge(item_list,on=['Item ID'],how='left')
        
        # get the mean quantity of each class in each week
        auction = auction.ix[:,['Week Num', 'Item ID', category, 'AH Quantity']]
        grouped = auction.groupby(['Week Num',category])['AH Quantity'].sum().reset_index()
        grouped.columns=['Week Num',category,'mean q']

        # get the mean quantity of each class in 31 weeks
        # we use mean() because all of the class appear 31 weeks
        grouped = grouped.groupby([category])['mean q'].mean().reset_index()

        fig, ax = plt.subplots()
        plt.pie(grouped['mean q'].tolist(), labels=grouped[category].tolist(), colors=color_list,autopct='%1.1f%%', shadow=True, startangle=90)
        plt.axis('equal')
        
        splitted_str = name.split('_')
        realm = splitted_str[0]
        fraction = splitted_str[1]
        ax.set_title(realm+' '+fraction, loc='left')
        ax.grid(True)

        plt.draw()
        plt.savefig(pp, format='pdf')
    pp.close()


####################################################################################
#   裝甲類別物品的資訊,包含需要等級, 物品等級, 附魔等級
####################################################################################
def plotArmorItemsInfo():
    df = read_csv('../corr_result/HighCorr/armorDetail.dat')
    df = df.fillna(0)
    #pp = PdfPages('../corr_result/fig/armorItemInfo.pdf')

    for fig_type in ['Enchanting','Item Level','Required Level']:
        fig, ax = plt.subplots()
        ax.hist(df[fig_type].tolist(), bins=20)
        ax.set_title(fig_type)
        
        plt.xlabel('Level')
        plt.ylabel('Item Quantity')
        plt.draw()
        plt.savefig('../corr_result/fig/armorDetail_'+fig_type+'.png', format='png')
    #pp.close()

####################################################################################
# 各個經濟體內的econ items數量
####################################################################################
def plotEconItemQuant():
    df = read_csv('../corr_result/HighCorr/ItemsDetail.csv')
    df = df.ix[:, ['Realm','Fraction']]

    df = df.groupby(['Realm','Fraction']).size().reset_index()
    df.rename(columns={0:'count'}, inplace=True)
    data = df.pivot('Realm','Fraction','count')
    
    data.plot(kind='bar')
    
    plt.draw()
    plt.savefig('../corr_result/fig/EconItemQuantity.png', format='png')
