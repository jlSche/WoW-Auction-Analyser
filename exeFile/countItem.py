from os import listdir
from os.path import isfile, join
import pandas as pd

target_path = '../corr_result/auction_detail/'

def getFiles():
	auction_files = [ f for f in listdir(target_path) if isfile(join(target_path,f)) ]
	return auction_files[1:]


def getItems(auction_list):
	items = list()
	for auction in auction_list:
		df = pd.read_csv(target_path + auction)
		items.extend(df['Item ID'].tolist())
	return items


def main():
	'''
		The function will return a set of items that has appeared in the auction.
	'''
	auction_list = getFiles()
	items = getItems(auction_list)
	return set(items)

if '__name__' == '__main__':
	main()







