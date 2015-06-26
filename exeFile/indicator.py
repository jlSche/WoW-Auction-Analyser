import pandas as pd
import scipy.stats as stats
import DataHandling

# gather all economic indicator items
def gatherItems():
	df = pd.read_csv('../corr_result/HighCorr/ItemsDetail.csv')
	df = df.ix[:, ['Realm','Fraction','Item ID','classname','qualityname']]
	return df

# return mean item appearance of each week
def getItemWeeklySupply(item_id=None, realm=None, fraction=None):
	# find the item first
	df = pd.read_csv('../corr_result/auction_detail/' + realm + '_' + fraction)
	df = df[df['Item ID'] == item_id]

	return df

def calCorrelation(item_id=None, realm=None, fraction=None, merged_df=None):
	corr, pval = stats.pearsonr(merged_df['AH Quantity'], merged_df['Profit'])
	new_record = pd.DataFrame([{'Realm': realm, 'Fraction': fraction, 'Item ID': item_id, 'Corr': corr, 'p Val': pval}])
	return new_record


def main():
	items_df = gatherItems()
	profit_df = pd.read_csv('../corr_result/profit_detail.csv')
	corr_result_df = pd.DataFrame(columns=['Realm','Fraction','Item ID','Corr','p Val'])

	for index, row in items_df.iterrows():
		item_id = int(row['Item ID'])
		realm = row['Realm']
		fraction = row['Fraction']
		print 'now processing', item_id, realm, fraction, '\t',

		weekly_supply = getItemWeeklySupply(item_id, realm, fraction)
		weekly_profit = profit_df[(profit_df['Realm']==realm) & (profit_df['Fraction']==fraction)]
		merged_df = weekly_supply.merge(weekly_profit, on='Week Num')
		#print merged_df

		new_record = calCorrelation(item_id, realm, fraction, merged_df)
		corr_result_df = corr_result_df.append(new_record, ignore_index=True)
		print new_record

	corr_result_df.to_csv('../corr_result/indicator_corr.csv', index=False)

if __name__ == '__main__':
	main()