import scipy.stats as stats
import pandas as pd
from realm_list import realm_list

# group by realm and fraction  high_corr/itemsdetail.csv
high_corr_items = pd.read_csv('../corr_result/HighCorr/ItemsDetail.csv')
high_corr_items = high_corr_items.ix[:, ['Realm','Fraction','Item ID']]


alliance_profit = pd.read_csv('../corr_result/alliance_profit.csv')
alliance_profit['Week Num'] = alliance_profit['Week Num'].astype(int)
horde_profit = pd.read_csv('../corr_result/horde_profit.csv')
horde_profit['Week Num'] = horde_profit['Week Num'].astype(int)

corr_result_df = pd.DataFrame(columns=['Realm','Fraction','Item ID','Corr','p Val'])

all_df = []
for realm in realm_list:
	for fraction in ['alliance','horde']:
		print 'finding high corr items in', fraction, 'of', realm, '...'
		df = high_corr_items[(high_corr_items['Realm']==realm) & (high_corr_items['Fraction']==fraction)]
		all_df.append(df)

print '\n'

for df in all_df:
	realm = df['Realm'].iloc[0]
	fraction = df['Fraction'].iloc[0]
	
	print '\ngathering items detail in', fraction, 'of', realm 
	auction_detail = pd.read_csv('../corr_result/auction_detail/' + realm + '_' + fraction)

	auction_profit = None
	if fraction == 'alliance':
		auction_profit = alliance_profit[alliance_profit['Realm']==realm]
	elif fraction == 'horde':
		auction_profit = horde_profit[horde_profit['Realm']==realm]

	merged = auction_detail.merge(auction_profit, on='Week Num')

	for item_id in df['Item ID']:
		print 'processing correlation of item', item_id, 'in', fraction, 'of', realm 

		item = merged[merged['Item ID']==item_id]
		corr, pval = stats.pearsonr(item['AH Quantity'], item['Profit'])
		
		new_record = pd.DataFrame([{'Realm': realm, 'Fraction': fraction, 'Item ID': item_id, 'Corr': corr, 'p Val': pval}])
		corr_result_df = corr_result_df.append(new_record, ignore_index=True)


passed = corr_result_df[corr_result_df['p Val']<0.05]
corr_result_df.to_csv('../corr_result/corrResult_0604.csv', index=False)

print len(passed), '/', len(corr_result_df), 'passed the Correlation Test.'








