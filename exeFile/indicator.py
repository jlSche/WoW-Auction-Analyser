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
	df = pd.read_csv('../workingDir/0313-1012/' + realm + '_' + fraction + '.csv')
	df = df[df['Item ID'] == item_id]

	# remove rows that AH Quantity is zero
	df = df[df['AH Quantity']!=0]

	# add "Week Num" column
	df['Week Num'] = df['PMktPrice Date'].apply(DataHandling.toWeekNumber)

	df = df.groupby(['Week Num'], as_index=False)
	return df['AH Quantity'].mean()



#def calCorrelation():


def main():
	items_df = gatherItems()
	profit_df = pd.read_csv('../corr_result/profit_detail.csv')
	corr_result_df = pd.DataFrame(columns=['Realm','Fraction','Item ID','Corr','p Val'])

	for index, row in items_df.iterrows():
		item_id = int(row['Item ID'])
		realm = row['Realm']
		fraction = row['Fraction']
		print 'now processing', item_id, realm, fraction

		weekly_supply = getItemWeeklySupply(item_id, realm, fraction)
		#print weekly_supply
		weekly_profit = profit_df[(profit_df['Realm']==realm) & (profit_df['Fraction']==fraction)]
		#print weekly_profit

		merged_df = weekly_supply.merge(weekly_profit, on='Week Num')
		print merged_df
		#'''
		corr, pval = stats.pearsonr(merged_df['AH Quantity'], merged_df['Profit'])
		new_record = pd.DataFrame([{'Realm': realm, 'Fraction': fraction, 'Item ID': item_id, 'Corr': corr, 'p Val': pval}])
		corr_result_df = corr_result_df.append(new_record, ignore_index=True)
		#'''
		break
	print corr_result_df

if __name__ == '__main__':
	main()