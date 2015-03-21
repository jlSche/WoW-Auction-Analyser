#-*- encoding=utf-8
from pandas import *
from collections import Counter
import numpy as np
from matplotlib import pyplot as plt
from sklearn_pandas import DataFrameMapper
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
import sklearn.preprocessing
import sklearn.decomposition
import math
from DataPreprocess import removeOutliers

armor_econ_items = '../corr_result/HighCorr/armorDetail_new.dat'
armor_items_price = '../corr_result/HighCorr/armorDetail_withPriceNew.csv'
item_detail = '../corr_result/HighCorr/itemsDetail.csv'
auctiondata_path = '../corr_result/auction_detail/'

######################################################################################################
# classify econ-items into 3 parts: wearing, enchanting, styling
######################################################################################################
def classifyEconItems(return_category='unknown'):
	df = read_csv(armor_econ_items)
	df = df.drop_duplicates()
	print '# of all items:', len(df)

	# for wearing
	wearing = df[(df['Required Level'] >= 90) & (df['Item Level'] >= 553)]
	print '# of items - wearing:', len(wearing)

	# for enchanting
	enchanting = df[(df['Usage'] == '飾品') | (df['Usage'] == '頸部') | (df['Usage'] == '手指')]
	print '# of items - enchanting:', len(enchanting)

	# unknown category
	enchanting_id = enchanting.index
	unknown = df.drop(enchanting_id)
	print '# of items left:',len(unknown)

	if return_category == 'unknown':
		return unknown
	elif return_category == 'enchanting':
		return enchanting
	
	#return unknown, enchanting


#############################################################################################################
# use generateDF() to merge armorDetail_withPriceNew.csv and itemsDetail.csv first
# and then generate a file contains all armor econ items with vendor price, price std, price mean
# output file: 03pricedata.csv
#############################################################################################################

def getPriceData():
	df = generateDF()
	realm_list = groupAuction(df)
	df = df.groupby(['Realm','Fraction'])

	result_list = []
	for realm in realm_list:
		for fraction in ['alliance','horde']:
			print realm, fraction
			try:
				auction = df.get_group((realm,fraction))
			except KeyError:
				print 'no econ-items in', realm, fraction, 'auction.'
				continue
			
			filename = realm+'_'+fraction
			auction_detail = read_csv(auctiondata_path+filename)
			auction_detail = auction_detail.groupby(['Item ID']).agg({'AH MarketPrice':[np.mean,np.std]}).reset_index()

			temp_df = auction_detail.merge(auction, how='inner', on='Item ID')
			result_list.append(temp_df)

	result_df = concat(result_list, ignore_index=True)

	result_df.rename(columns={('AH MarketPrice', 'mean'): 'PriceMean', ('AH MarketPrice', 'std'): 'PriceStd'}, inplace=True)
	result_df.drop(('Item ID', ''), axis=1, inplace=True)

	result_df.to_csv('../corr_result/HighCorr/03pricedata.csv', index=False)
	return result_df

def generateDF():
	price_df = read_csv(armor_items_price)
	price_df.drop_duplicates(inplace=True)
	detail_df = read_csv(item_detail)

	df = price_df.merge(detail_df, how='inner', on=['Item ID'])
	return df


def classifyUnknownCategory():
	unknown = classifyEconItems()
	o_df = read_csv('../corr_result/HighCorr/03pricedata.csv')

	# get only the set from unknown from o_df
	unknown_list = unknown['Item ID'].tolist()
	o_df = o_df[o_df['Item ID'].isin(unknown_list)]
	o_df.drop_duplicates('Item ID', inplace=True)

	o_df = o_df.merge(unknown, how='inner', on=['Item ID'])

	df = o_df.copy()
	zero = df[(df['PriceMean']==0.0) | (df['VPrice']==0.0)]
	print '# of items no longer sell from NPC:', len(zero)
	df = df[df.VPrice!=0] #????????????????????????  why are there items price is 0 ?
	df['diff'] = o_df['PriceMean'] / (o_df['VPrice']) 

	copy_df = df.copy()
	#df = df.ix[:,['PriceMean', 'Item Level', 'Required Level']]	

	#_enchanting = getMeanPriceOf27EnchantingItems()
	#init_centers = np.asarray(_enchanting)

	'''
	#############################################################################################################
	# the below will use kmeans to cluster
	#############################################################################################################
	#df['PriceMean'] = np.log10(df['PriceMean'])
	df = df.ix[:,['PriceMean','diff']]
	mapper = DataFrameMapper([([df.columns], sklearn.preprocessing.StandardScaler())])
	df = sklearn.preprocessing.normalize(df)
	centers = KMeans(n_clusters=2).fit(df)
	result =  KMeans(n_clusters=2).fit_predict(df)
	print '\ncenters are:\n'
	print centers.cluster_centers_
	print '\npredict result:\n'
	print Counter(result)
	result = result.tolist()

	plt.scatter(df[:, 0], df[:, 1], c=result)
	plt.show()
	'''

	#'''
	#############################################################################################################
	# the below will use AgglomerativeClustering to cluster
	#############################################################################################################	
	df = df.ix[:,['PriceMean','diff']]	
	mapper = DataFrameMapper([([df.columns], sklearn.preprocessing.StandardScaler())])
	df = sklearn.preprocessing.normalize(df)

	model = AgglomerativeClustering(n_clusters=2, linkage='average')
	model.fit(df)
	result = model.labels_.tolist()
	#plt.scatter(df[:, 0], df[:, 1], c=model.labels_)
	#plt.show()
	#return 
	#'''

	copy_df['category'] = result
	copy_df['diff'] = np.log10(copy_df['diff'])
	copy_df['PriceMean'] = np.log10(copy_df['PriceMean'])
	#copy_df = copy_df.ix[:,['PriceMean','diff','category']]
	my_scatter = plt.axes([0.1,0.1,0.65,0.65])
	my_scatter.scatter(x=copy_df['diff'], y=copy_df['PriceMean'], c=copy_df['category'])

	plt.title('Enchanting and Styling')
	plt.xlabel('log( Auction Price / Vendor Price )')
	plt.ylabel('log( Auction Price )')
	#plt.axvline(x = 2.604, linewidth=1, color='r')
	#plt.axhline(y = 2.7466, linewidth=1, color='r')
	plt.legend(loc='best')
	plt.draw()
	plt.savefig('../corr_result/fig/unknownCategory.png', format='png')
	return copy_df
	#print len(df[(df['diff']>=2.604) & (df['PriceMean']>=2.7466)])
	#'''

	'''
	price_list = getMeanPriceOf27EnchantingItems()
	
	common = df[df['qualityname']=='Common']
	poor = df[df['qualityname']=='Poor']
	uncommon = df[df['qualityname']=='Uncommon']
	epic = df[df['qualityname']=='Epic']
	rare = df[df['qualityname']=='Rare']

	# get styling list
	qualitylist = ['Poor', 'Common', 'Uncommon', 'Rare', 'Epic']
	for idx in range[0, qualitylist]:
		p_enchanting = price_list[idx]
		temp_df = df[df['qualityname']==qualitylist[idx]]

		enchanting = temp_df[temp_df['PriceMean'] < p_enchanting]
		styling = temp_df[temp_df['PriceMean'] >= p_enchanting]

	df['style'] = df.apply(determineCategory)
	'''




def determinCategory(row):
	if row['PriceMean'] >= row['std_price']:
		return 'styling'
	else:
		return 'enchanting'



#############################################################################################################
# remember to change to return value in classifyEconItems()
#############################################################################################################
def getMeanPriceOf27EnchantingItems():
	enchanting = classifyEconItems('enchanting')
	df = read_csv('../corr_result/HighCorr/03pricedata.csv')

	enchanting_list = enchanting['Item ID'].tolist()
	df = df[df['Item ID'].isin(enchanting_list)]
	df.drop_duplicates('Item ID', inplace=True)
	return df
	df = df.merge(enchanting, how='inner', on=['Item ID'])
	df['diff'] = df['PriceMean'] / (df['VPrice'])
	removeOutliers(df, on_columns=['PriceMean','diff'])
	return [df['PriceMean'].mean(), df['PriceMean'].std(), df['diff'].mean(), df['diff'].std()	]

