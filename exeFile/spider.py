#-*- encoding=utf-8
import urllib2
import re
import time
from pandas import *
from bs4 import BeautifulSoup

#main_url = 'http://www.wowdb.tw/item-14159.html'
main_url = 'http://www.wowdb.tw/item-'

def getItemDetail(itemid):
    url = main_url + str(itemid) + '.html'
    response = urllib2.urlopen(url)
    html = response.read()

    # find item name
    soup = BeautifulSoup(html)
    title = soup.find(id='itemtitle')
    title = str(title)
    pattern = r"(.+)>(.+)(</h1>)"
    match = re.match(pattern, title)

    # find item level and item required level
    iteminfo = soup.body.find(id='info')
    target_numbers =  iteminfo.find_all(text=re.compile('(.+): (\d+)'))
    
    # find usage
    usage = iteminfo.find('td')
    usage = str(usage)
    pattern = r"(.+)>(.+)(</td>)"
    usage = re.match(pattern,usage)

    item_level = int(target_numbers[0].split(' ')[1])
    required_level = None
    if len(target_numbers) == 2:
        required_level = int(target_numbers[1].split(' ')[1])

    # find enchanting
    iteminfo = soup.body.find(id='itemdetailright')
    enchanting = iteminfo.find_all(text=re.compile(': ([0-9])'))
    if len(enchanting) != 0:
        enchanting = unicode(enchanting[0]).encode('ascii','replace')
        enchanting = enchanting.split(' ')[1]
        enchanting = int(re.match(r'\d+',str(enchanting)).group())
    else:
        enchanting = None
    
    return match.group(2), usage.group(2), item_level, required_level, enchanting
    '''
    if match:
        return match.group(2)
    else:
        return str(itemid) + ' does not match anything!'
    '''

def getItemPrice(itemid):
    url = main_url + str(itemid) + '.html'
    response = urllib2.urlopen(url)
    html = response.read()


    soup = BeautifulSoup(html)
    moneygold = soup.findAll("span", {"class": "moneygold"})
    moneysilver = soup.findAll("span", {"class": "moneysilver"})
    moneycopper = soup.findAll("span", {"class": "moneycopper"})

    price = 0
    if len(moneygold) != 0:
        price += float(re.search(r'\d+',str(moneygold)).group())
    if len(moneysilver) != 0:
        price += float(re.search(r'\d+',str(moneysilver)).group()) / 100
    if len(moneycopper) != 0:
        price += float(re.search(r'\d+',str(moneysilver)).group()) / 10000

    return price


def main():
    armor = read_csv('../corr_result/HighCorr/armorDetail_new.dat')
    armor.drop_duplicates(inplace=True)
    armor['Item ID'] = armor['Item ID'].astype('int')
    
    item_detail_price = DataFrame(columns=['Item ID','VPrice'])

    for idx in armor.index:
        print 'now retrieving item', armor.ix[idx]['Item ID']
        vendor_price = getItemPrice(armor.ix[idx]['Item ID'])
        new_item = DataFrame(([{'Item ID':armor.ix[idx]['Item ID'], 'VPrice': vendor_price}]))
        item_detail_price = item_detail_price.append(new_item, ignore_index=True)
        time.sleep(3)

    item_detail_price.to_csv('../corr_result/HighCorr/armorDetail_withPrice.csv',index=False)
    
    '''
    #item_detail = DataFrame(columns=['Item ID','Item Name','Item Level','Required Level','Enchanting','Usage'])
    for idx in range(500,544):
        print int(armor.ix[idx]['Item ID']),
        #return getItemDetail(int(armor.ix[idx]['Item ID']))
        name, usage, item_level, required_level, enchanting = getItemDetail(int(armor.ix[idx]['Item ID']))
        print name, usage, item_level, required_level, enchanting
        
        new_item = DataFrame(([{'Item ID':armor.ix[idx]['Item ID'], 'Item Name':name,'Item Level':item_level, 'Required Level':required_level, 'Enchanting':enchanting, 'Usage':usage}]))
        item_detail = item_detail.append(new_item, ignore_index=True)
        time.sleep(3)
    item_detail.to_csv('../corr_result/HighCorr/armorDetail6.dat',index=False)
    ''' 

if __name__ == '__main__':
    main()
        

