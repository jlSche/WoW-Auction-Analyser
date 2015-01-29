from pandas import *
import numpy as np
from mpl_toolkits.axes_grid1 import host_subplot
from matplotlib.backends.backend_pdf import PdfPages
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt


auction_list = read_csv('../sourceDir/target_realm.dat')
auction_name = auction_list['Realm']
item_list = read_csv('../sourceDir/itemlist.csv')

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
    
    pp = PdfPages('../corr_result/fig/'+name+'-'+fraction)
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
# Plot realms with same realm_type(pvp or pve) in a grapgh.
# So this function will generate (fraction)*(type) 4 figures
##############################################################################################
def plotTypeCluster():
    high_corr_items = read_csv('../corr_result/HighCorr/allRealms.csv')
    item_list.rename(columns={'Item_ID':'Item ID'}, inplace=True)
    high_corr_items = high_corr_items.merge(item_list, how='left', on=['Item ID'])

    # p: pvp, e: pve, a: alliance, h: horde
    p_a = high_corr_items[(high_corr_items['pvp']=='pvp') & (high_corr_items['Fraction']=='alliance')]
    p_h = high_corr_items[(high_corr_items['pvp']=='pvp') & (high_corr_items['Fraction']=='horde')]
    e_a = high_corr_items[(high_corr_items['pvp']=='pve') & (high_corr_items['Fraction']=='alliance')]
    e_h = high_corr_items[(high_corr_items['pvp']=='pve') & (high_corr_items['Fraction']=='horde')]
    
    pp = PdfPages('../corr_result/fig/cluster_type')
    
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
    pp = PdfPages('../corr_result/fig/cluster_'+fraction)
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
##############################################################################################
def plotEachRealmCluster(realmlist, plottype='composing'):
    high_corr_items = read_csv('../corr_result/HighCorr/ItemsDetail.csv')
    
    pp = None
    if plottype == 'composing':
        pp = PdfPages('../corr_result/fig/cluster_eachRealmComposing')
    elif plottype == 'sum':
        pp = PdfPages('../corr_result/fig/cluster_eachRealmSum')

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
                plt.savefig(pp, format='pdf')

    pp.close()



##############################################################################################
# Plot how the eco-items composed in 4 different economic systems
##############################################################################################
def plotComposing(category='classname'):
    high_corr = read_csv('../corr_result/HighCorr/allRealms.csv')
    items = read_csv('../sourceDir/itemlist.csv')
    high_corr = high_corr.merge(items,left_on='Item ID',right_on='Item_ID',how='left')

    p_a = high_corr[(high_corr['pvp']=='pvp') & (high_corr['Fraction']=='alliance')] 
    p_h = high_corr[(high_corr['pvp']=='pvp') & (high_corr['Fraction']=='horde')] 
    e_a = high_corr[(high_corr['pvp']=='pve') & (high_corr['Fraction']=='alliance')] 
    e_h = high_corr[(high_corr['pvp']=='pve') & (high_corr['Fraction']=='horde')]


    pp = PdfPages('../corr_result/fig/ecoItemsComposing')

    for realm_type in [p_a, p_h, e_a, e_h]:
        # sum each category
        grouped = realm_type.groupby([category]).size()
        category_list = list(grouped.index)
        count_list =  grouped.values
        color_list = ['lightcoral','white','lightyellow','yellowgreen','lightskyblue','magenta','lightgray','gold','hotpink']

        # plot
        fig, ax = plt.subplots()
        plt.pie(count_list, labels=category_list, colors=color_list,autopct='%1.1f%%', shadow=True, startangle=90)
        plt.axis('equal')
        
        ax.set_title(realm_type.iloc[0]['pvp']+' '+realm_type.iloc[0]['Fraction'], loc='left')

        ax.grid(True)

        plt.draw()
        plt.savefig(pp, format='pdf')
    pp.close()






