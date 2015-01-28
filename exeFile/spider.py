import urllib2
import re
from pandas import *
from bs4 import BeautifulSoup

#main_url = 'http://www.wowdb.tw/item-14159.html'
main_url = 'http://www.wowdb.tw/item-'

def getItemName(itemid):
    url = main_url + str(itemid) + '.html'
    response = urllib2.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html)
    title = soup.find(id='itemtitle')
    title = str(title)
    pattern = r"(.+)>(.+)(</h1>)"
    match = re.match(pattern, title)
    if match:
        return match.group(2)
    else:
        return str(itemid) + ' does not match anything!'

def main():

    df_allItems = read_csv('../corr_result/HighCorr/allRealms.csv')
    item_detail = DataFrame(columns=['Realm','Fraction','Item','Corr'])
    for idx in df_allItems.index:

        realm = df_allItems.ix[idx]['Realm']
        fraction = df_allItems.ix[idx]['Fraction']
        item = getItemName(int(df_allItems.ix[idx]['Item ID']))
        corr = df_allItems.ix[idx]['Corr']
        
        new_item = DataFrame(([{'Realm': realm,'Fraction': fraction,'Item': item,'Corr': corr}]))
        item_detail = item_detail.append(new_item, ignore_index=True)
    item_detail.to_csv('../corr_result/HighCorr/highCorrItemName.dat',index=False)
        

if __name__ == '__main__':
    main()
        

